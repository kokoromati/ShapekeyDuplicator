import bpy
import os
import traceback
from dataclasses import dataclass
from bpy_extras.io_utils import ImportHelper
from .tomlkit import *


# ShapeKey 管理用
@dataclass
class SK:
    index: int
    name: str


# 複製・ソートの実行
class SHAPEKEYDUPLICATOR_OT_duplicate_and_sort(bpy.types.Operator):
    bl_idname = "shapekey_duplicator.duplicate_and_sort"
    bl_label = "複製＆ソートを実行"

    _duplicate_cnt = 0
    _overwrite_cnt = 0

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            self.report({'INFO'}, "Skip : オブジェクトモードでのみ実行できます。")
            return {'FINISHED'}
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, "Skip : 選択しているオブジェクトがありません。")
            return {'FINISHED'}
        toml_path = context.scene.toml_path
        if len(toml_path) == 0:
            self.report({'INFO'}, "Skip : toml path が指定されていません。")
            return {'FINISHED'}
        if not os.path.isfile(toml_path):
            self.report({'INFO'}, "Error : toml path にファイルが存在しません。")
            return {'FINISHED'}
        try:
            toml_data = self._read_toml(toml_path)
            result_text = self._duplicate_and_sort(context, toml_data, bpy.context.selected_objects)
        except Exception as e:
            result_text = f"Error : {e}"
            print(traceback.format_exc())
        self.report({'INFO'}, result_text)
        return {'FINISHED'}

    # toml の読み込み、バリデート＆加工
    def _read_toml(self, toml_path):
        with open(toml_path, 'r', encoding='utf-8') as file:
            toml_data = parse(file.read())
        # バリデート＆加工
        for duplicate in toml_data.get("duplicate", []):
            if "from" not in duplicate:
                raise Exception("[[duplicate]] 以下に from がありません。")
            if not isinstance(duplicate["from"], str):
                raise Exception("[[duplicate]] 以下の from 直下に文字列ではない値が入っています。")
            if "to" not in duplicate:
                raise Exception("[[duplicate]] 以下に to がありません。")
            if isinstance(duplicate["to"], str):
                duplicate["to"] = [duplicate["to"]]
            elif isinstance(duplicate["to"], list):
                pass
            else:
                raise Exception("[[duplicate]] 以下の to 直下に文字列または配列ではない値が入っています。")
            if len(duplicate["from"]) == 0:
                raise Exception("[[duplicate]] 以下の from が空です。")
            for sk_name_to in duplicate["to"]:
                if not isinstance(sk_name_to, str):
                    raise Exception("[[duplicate]] 以下の to に文字列ではない値が入っています。")
                if len(sk_name_to) == 0:
                    raise Exception("[[duplicate]] 以下の to が空です。")
        order_list = toml_data.get("sort", {}).get("order", [])
        if not isinstance(order_list, list):
            raise Exception("[sort] 以下の order に配列ではない値が入っています。")
        count_dict = {}
        for sk_name in order_list:
            if not isinstance(sk_name, str):
                raise Exception("[sort] 以下の order 配列に文字列ではない値が入っています。")
            if len(sk_name) == 0:
                raise Exception("[sort] 以下の order 配列に空文字が入っています。")
            if sk_name in count_dict:
                count_dict[sk_name] += 1
            else:
                count_dict[sk_name] = 1
        duplicate_list = [key for key, value in count_dict.items() if value > 1]
        if len(duplicate_list) > 0:
            raise Exception(f"[sort] 以下の order 配列内で重複があります。{duplicate_list}")
        return toml_data        

    # 複製・ソートの実行
    def _duplicate_and_sort(self, context, toml_data, object_list):
        self._duplicate_cnt = 0
        self._overwrite_cnt = 0
        self._duplicate_skip_cnt = 0
        self._sort_cnt = 0
        # 
        for object in object_list:
            # シェイプキーがないものは無視する
            if not hasattr(object.data, "shape_keys") or not object.data.shape_keys:
                continue
            # アクティブオブジェクトの設定（これを実行しないとシェイプキーのソートが正常動作しない）
            context.view_layer.objects.active = object
            # 複製
            for duplicate in toml_data.get("duplicate", []):
                sk_name_from = duplicate["from"]
                for sk_name_to in duplicate["to"]:
                    self._duplicate_shape_key(object, sk_name_from, sk_name_to)
                    print(f"duplicate {sk_name_from} => {sk_name_to}")
            # ソート
            self._sort_shape_key(object, toml_data.get("sort", {}).get("order", []))
        return f"Done! : 複製 {self._duplicate_cnt} " + \
                f"(上書き {self._overwrite_cnt}), " + \
                f"シェイプキーが存在せず複製スキップ {self._duplicate_skip_cnt}, " + \
                f"ソート {self._sort_cnt}"

    # シェイプキーの複製
    def _duplicate_shape_key(self, object, sk_name_from, sk_name_to):
        # 元のシェイプキーを取得する
        original_shape_key = object.data.shape_keys.key_blocks.get(sk_name_from)
        if original_shape_key:
            # 既存のシェイプキーがあれば削除する
            existing_shape_key = object.data.shape_keys.key_blocks.get(sk_name_to)
            if existing_shape_key:
                object.shape_key_remove(existing_shape_key)
                self._overwrite_cnt += 1
            # 新しいシェイプキーを複製する
            new_shape_key = object.shape_key_add(name=sk_name_to, from_mix=False)
            # 複製されたシェイプキーに元のシェイプキーの値をコピーする
            vals = [0.0] * len(original_shape_key.data) * 3
            original_shape_key.data.foreach_get("co", vals)
            new_shape_key.data.foreach_set("co", vals)
            self._duplicate_cnt += 1
        else:
            self._duplicate_skip_cnt += 1

    # シェイプキーのソート
    def _sort_shape_key(self, object, order_list):
        if len(order_list) <= 0:
            return
        shape_keys = object.data.shape_keys
        if not shape_keys:
            return
        if len(shape_keys.key_blocks) <= 1:
            return
        # 現在の並びを取得する
        old_sk_list = []
        for index, shape_key in enumerate(shape_keys.key_blocks):
            old_sk_list.append(SK(index, shape_key.name))
            print(f"old_sk_list : {index}, {shape_key.name}")
        new_sk_list = []
        new_sk_index = 0
        # 現在の先頭のシェイプキーはソート時も先頭を保つ
        new_sk_list.append(SK(old_sk_list[0].index, old_sk_list[0].name))
        new_sk_index += 1
        old_sk_list[0].index = -1
        # 新しい並びを作成する
        for sk_name in order_list:
            sk_hit = None
            for sk in old_sk_list:
                if sk.name == sk_name:
                    sk_hit = sk
                    break
            if sk_hit:
                new_sk_list.append(SK(new_sk_index, sk_name))
                new_sk_index += 1
                sk_hit.index = -1
        for sk in old_sk_list:
            if sk.index >= 0:
                new_sk_list.append(SK(new_sk_index, sk.name))
                new_sk_index += 1
        # ソート（先頭は対象としない）
        current_sk_name = object.active_shape_key.name
        for sk in new_sk_list[1:]:
            shape_key_index = shape_keys.key_blocks.find(sk.name)
            object.active_shape_key_index = shape_key_index
            bpy.ops.object.shape_key_move(type="BOTTOM")
            print(f"sort : {sk.name}, {shape_key_index} => {sk.index}")
        object.active_shape_key_index = shape_keys.key_blocks.find(current_sk_name)
        self._sort_cnt += 1


# toml ファイルセレクター
class SHAPEKEYDUPLICATOR_OT_toml_selector(bpy.types.Operator, ImportHelper):
    bl_idname = "shapekey_duplicator.toml_selector"
    bl_label = "toml を選択"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")   # type: ignore

    def execute(self, context):
        print("Selected File:", self.filepath)
        context.scene.toml_path = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# パネル
class SHAPEKEYDUPLICATOR_PT_main(bpy.types.Panel):
    bl_label = "ShapekeyDuplicator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        # toml の指定・選択
        row = layout.row()
        row.prop(context.scene, "toml_path")
        row.operator("shapekey_duplicator.toml_selector")
        # コレクションの一覧
        row = layout.row()
        row.label(text=f"現在選択している {len(bpy.context.selected_objects)} 個のオブジェクトに対して処理を実行します。")
        #
        layout.separator()
        # 複製・ソートの実行
        row = layout.row()
        row.operator("shapekey_duplicator.duplicate_and_sort")
