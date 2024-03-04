import bpy
from .core import *


bl_info = {
    "name": "ShapekeyDuplicator",
    "author": "kokoromati",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Duplicate & sort shape keys based on external file.",
    "category": "Object",
}


class_list = [
    SHAPEKEYDUPLICATOR_OT_duplicate_and_sort,
    SHAPEKEYDUPLICATOR_OT_toml_selector,
    SHAPEKEYDUPLICATOR_PT_main,
]


def register():
    for c in class_list:
        bpy.utils.register_class(c)
    bpy.types.Scene.toml_path = bpy.props.StringProperty(name="toml path")


def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.toml_path


if __name__ == "__main__":
    register()
