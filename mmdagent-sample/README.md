# MMDAgent-EXを利用したサンプルアプリケーション

## 使い方

### MMDAgent-EXのセットアップ

#### MMDAgent-EXのインストール 

[MMDAgent-EXのインストール方法の説明](https://mmdagent-ex.dev/ja/docs/build/)にしたがってインストールします。
できたディレクトリ（例：`MMDAgent-EX-win32-v2.0.1`）を`<mmdagent>`ディレクトリと呼びます。

#### 音声認識のセットアップ

[音声モデル](https://drive.google.com/file/d/1d82CpinrlDmY9MgjTYa-awCdLOsz16MF/view?usp=sharing)をダウンロードします。

ダウンロードしてできた`Julius_Models_20231015`の中身を `<mmdagent>/AppData/Julius/`にコピーします。

#### Exampleコンテンツの入手

以下のコマンドで行います。

```sh
cd <mmdagent>
git clone --recursive https://github.com/mmdagent-ex/example
```

`<mmdagent>/example/main.mdf`を編集し、下記2行のコメントを外します。

```
Plugin_Julius_lang=ja
Plugin_Julius_conf=dnn
```

### DialBBとの接続の設定

`<mmdagent>/example/main.mdf` の最後に以下を加えます。

```
Plugin_AnyScript_Command=python -u <このディレクトリへのパス>/dialbb_connector.py --motion_table <このディレクトリへのパス>/motion_table.yml
log_file=_log.txt
```

ここで`<このディレクトリへのパス>`とは、`<mmdagent>/example`から本READMEがあるディレクトリへの相対パスです。

## サンプルアプリの実行方法

### DialBBサーバの起動

以下のコマンドでノーコードツールを起動します。

```sh
dialbb-nc
```

本READMEのあるディレクトリにある`cooking.zip`を読み込みます。

設定ボタンを押して`OPENAI_API_KEY`を設定します。

起動ボタンでサーバを起動します。

### MMDAgentの起動

作業フォルダへ移動します。
```
cd <mmdagent>
```

MMDAgentを起動 します。以下はWindowsの場合です。その他の場合は適宜コマンドを変更してください。
```
MMDAgent-EX.exe example\main.mdf
```

対話ができるようになります。

### 変更の仕方






## （参考）
### モーションの変更
motion_table.ymlを編集して[状態]に対する[モーションファイル]を変更する  
モーションファイルの所在は、exampleフォルダの **motions/**, **gene/motion/**, **uka/motion/**, です
```
e.g. "初期状態の時に"：お辞儀をするモーションファイル  を指定する場合、
  "#initial": motions/action/ojigi.vmd
```

### ログ出力

* Shift+f キーでスクリーン上に詳細なログを表示切替が可能
* ファイル出力する場合は：main.mdfに「log_file=log.txt」の1行追加

### MMDAgentの画面制御
* 矢印キーで回転
* Shift＋矢印キーで移動
* \+ キーでズームイン／- キーでズームアウト
* C キーでマウスの有効／無効切り替え
* Escで終了

