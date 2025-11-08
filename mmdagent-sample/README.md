# MMDAgent-EXを利用したサンプルアプリケーション

DialBB ver. 1.1+ で動作します．

## サンプルの使用方法

### MMDAgent-EXのセットアップ

#### MMDAgent-EXのインストール 

[MMDAgent-EXのインストール方法の説明](https://mmdagent-ex.dev/ja/docs/build/)にしたがってインストールします．
できたディレクトリ（例：`MMDAgent-EX-win32-v2.0.1`）を`<mmdagent>`ディレクトリと呼びます．

#### 音声認識のセットアップ

[音声モデル](https://drive.google.com/file/d/1d82CpinrlDmY9MgjTYa-awCdLOsz16MF/view?usp=sharing)をダウンロードします．

ダウンロードしてできた`Julius_Models_20231015`の中身を `<mmdagent>/AppData/Julius/`にコピーします．

#### Exampleコンテンツの入手

以下のコマンドで行います．

```sh
cd <mmdagent>
git clone --recursive https://github.com/mmdagent-ex/example
```

`<mmdagent>/example/main.mdf`を編集し，下記2行のコメントを外します．

```
Plugin_Julius_lang=ja
Plugin_Julius_conf=dnn
```

### DialBBとの接続の設定

`<mmdagent>/example/main.mdf` の最後に以下を加えます．

```
Plugin_AnyScript_Command=python -u <このディレクトリへのパス>/dialbb_connector.py --motion_table <このディレクトリへのパス>/motion_table.yml
log_file=_log.txt
```

ここで`<このディレクトリへのパス>`とは，`<mmdagent>/example`から本READMEがあるディレクトリへの相対パスです．

## サンプルアプリの実行方法

### DialBBサーバの起動

以下のコマンドでノーコードツールを起動します．

```sh
dialbb-nc
```

本READMEのあるディレクトリにある`cooking.zip`を読み込みます．

設定ボタンを押して`OPENAI_API_KEY`を設定します．

起動ボタンでサーバを起動します．

### MMDAgentの起動

作業フォルダへ移動します．
```
cd <mmdagent>
```

MMDAgentを起動 します．以下はWindowsの場合です．その他の場合は適宜コマンドを変更してください．
```
MMDAgent-EX.exe example\main.mdf
```

対話ができるようになります．

`main.mdf`と同じディレクトリの`_log.txt‘`にMMDAgentのログが出力されます．

## アプリケーションの変更方法

### MMDAgentとDialBBの通信

MMDAgentのmdfファイルのPlugin_AnyScript_Commandには以下のように設定します．

```sh
python -u dialbb_connector.py --motion_table <モーションテーブルファイル> 
                              [--host <DialBBサーバのホスト>] 
                              [--port <DialBBサーバのポート番号>]
```

モーションテーブルファイルには，以下のように，モーションIDと，モーションを定義するvmdファイル（mdfファイルからの相対パスで記述）の対応を書きます．

```yaml
うなづく: motions/action/nod.vmd
会釈する: motions/action/eshaku.vmd
お辞儀する: motions/action/ojigi.vmd
考える: motions/action/thinking.vmd
両手を振る: motions/action/wavehands.vmd
```

DialBBサーバから送られるシステム発話文字列の末尾に，`(motion:<モーションID>)`という文字列があると，`<モーションID>`を取り出し，`motion_table.yml`を参照してモーションを取り出します．

### モーションの変更
`motion_table.yml`を編集することで，新しいモーションをつかえるようになります．モーションファイルは，exampleフォルダの `motions/`**, **`gene/motion/`**, **`uka/motion/`にあります．

