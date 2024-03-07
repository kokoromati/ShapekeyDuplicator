# ShapekeyDuplicator

![概要](https://raw.githubusercontent.com/wiki/kokoromati/ShapekeyDuplicator/2024-03-07_08-33-31.png)

toml 定義ファイルを元にシェイプキーを複製・ソートする Blender アドオンです。

Blender 3.1 で動作確認をしています。

## 想定している利用状況

「MMD 用シェイプキーが必要だけど、MMD 用シェイプキーは名前が解かりづらくそれのみで管理するのはつらい。
　でも、自分で命名したシェイプキーを複製して MMD 用シェイプキーを作成しようとすると手間がかかる」

そういった場合に当アドオンを使用することで、一括で自分のシェイプキーから MMD 用シェイプキーを複製し、
ついでに解かりやすい順番に並べ替えることができます。

## インストール手順

1. GitHub `Code > Download ZIP` から zip ファイルをダウンロードします。
2. Blender の `編集 > プリファレンス` を選択、`アドオン > インストール` を選択、 zip ファイルを選択、インストールボタンを押します。
3. 当アドオンの左側のチェックボックスを ON にします。
4. `左下のメニューアイコン > プリファレンスを保存` を選択します。

## 使用手順

1. GitHub `example-01.toml` をダウンロードします。
    - テキストエディタで一から toml ファイルを作成しても良いですが、エンコードが UTF-8 である必要があります。
    - `example-02.toml` の内容もあわせて確認すると応用方法が解かります。
2. toml ファイルをメモ帳などのテキストエディタで開きます。
3. toml ファイル内のコメントに説明がありますので、それに従って自分の環境に合わせて定義を行います。
4. Blender で対象の .blend ファイルを開き、`ツール > ShapekeyDuplicator > toml を選択` を選択、編集した toml ファイルを指定します。
5. 複製・ソートの対象とするオブジェクトをオブジェクトモードで１つまたは複数選択します。
6. `ツール > ShapekeyDuplicator > 複製＆ソートを実行` を選択します。
7. 画面下部などに実行結果が表示されます。
    - 正常に実行されると `Done! : ...` という表示がでます。
    - エラーなどが出た場合はメッセージに従って toml ファイルを見直してください。
    - アンドゥすることで複製・ソートを取り消すことが出来ます。

## 使用ライブラリ

### tomlkit

Copyright (c) sdispater
Released under the MIT license
[https://github.com/sdispater/tomlkit/blob/master/LICENSE](https://github.com/sdispater/tomlkit/blob/master/LICENSE)

