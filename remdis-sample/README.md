# Remdis＋DialBBの連携（MMDAgentあり）



## 仕組み
* Remdisをベースに逐次応答生成モジュール\[dialogue\]の代わりにDialBBモジュールを作成して、他モジュールと組み合わせることでDialBBを使用した音声認識結果に応答するシステム発話を生成する.  
* RemdisはMMDAgent-EXがバンドルされているためのCGアバターとの対話も可能である.  
* 現状のDialBBはインクリメンタルに対応していないため、発話完了を検出してからDialBBのクラスAPIを実行する作りとしている.  


## 導入方法
※作業ディレクトリを"remdis"として説明する  
1. Remdisをセットアップ  
    * 公式のRemdisはOpenAI APIのバージョンが古いため（[補足](#補足)参照）、Forkしたリポジトリを使用する (https://github.com/c4a-ri/remdis)  
    READMEを参考にremdisフォルダにインストールする  
    * Remdisのdialogueモジュールを使用した音声対話が可能か確認する（この時点でMMDAgentも含めたRemdisの基本動作が正常動作することを確認してください）


1. 本ブランチのファイルをremdisフォルダにコピーする  

1. DialBBパッケージのインストール  
    DialBBのwheelを [ここ](https://github.com/c4a-ri/dialbb/tree/dev-v1.0/dist) から取得してインストールする  
      ```
      pip install dialbb-X.X.XX-py3-none-any.whl
      ```


## 実行方法
* Remdisの READMEに記載の手順「[MMDAgent-EXを用いたエージェント対話](https://github.com/remdis/remdis?tab=readme-ov-file#MMDAgent-EXを用いたエージェント対話)」に従って、python dialogue.pyの箇所を **python dialbb_dialogue.py** に置き換えて実行する  
参考：
    ```
    1. python input.py
    2. python text_vap.py
    3. python asr.py
    4. python tts.py
    5. python dialbb_dialogue.py
    ```
* または、本リポジトリで用意したバッチファイルを実行することでも可能　※仮想環境は**Poetry**を使用  
    1. RabbitMQサーバを実行
    1. エクスプローラなどで **remdis/batch-file** フォルダへ移動する  
    1. バッチファイル： **start-all.bat** をダブルクリックする  
    1. 5個のターミナルとMMDAgentの起動を確認  
    1. 始めのシステム発話を待って対話を開始する


## 補足

* DialBBのアプリケーション(シナリオ)を切り替える場合は、remdis/batch-file/dialbb.bat のapp_conf=xxxx を変更する  
* OpenAI API(openaiライブラリ)は Remdisがバージョン0.28 だがDialBBに合わせのバージョン1.12.0 にアップしている

