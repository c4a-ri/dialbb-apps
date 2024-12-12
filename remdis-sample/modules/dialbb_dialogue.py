import os
import argparse
import threading
import queue
import time
from base import RemdisModule, RemdisUpdateType, RemdisState, RemdisUtil
import prompt.util as prompt_util
from dialbb.main import DialogueProcessor


class TEST_DIALBB(RemdisModule):
    def __init__(self,
                 pub_exchanges=['dialogue'],
                 sub_exchanges=['tts', 'asr']):
        super().__init__(pub_exchanges=pub_exchanges,
                         sub_exchanges=sub_exchanges)

        # 設定の読み込み
        os.environ['OPENAI_KEY'] = self.config['ChatGPT']['api_key']
        self.history_length = self.config['DIALOGUE']['history_length']
        self.response_generation_interval = self.config['DIALOGUE']['response_generation_interval']
        self.max_message_num_in_context = self.config['ChatGPT']['max_message_num_in_context']

        # 対話履歴
        self.dialogue_history = []
        self.user_utterance_generation = []

        # IUおよび応答の処理用バッファ
        self.system_utterance_end_time = 0.0
        self.input_iu_buffer = queue.Queue()
        self.bc_iu_buffer = queue.Queue()
        self.emo_act_iu_buffer = queue.Queue()
        self.output_iu_buffer = []
        self.llm_buffer = queue.Queue()

        # 対話状態管理
        self.event_queue = queue.Queue()
        self.state = 'idle'
        self._is_running = True

        # IU処理用の関数
        self.util_func = RemdisUtil()

        # 対話アプリ
        self.dialogue_processor = None
        self.dialbb_user_id = 'user'
        self.dialbb_session_id = ''

    def run(self, app_conf):
        # 音声認識結果受信スレッド
        threading.Thread(target=self.listen_asr_loop).start()
        # 逐次応答生成スレッド
        threading.Thread(target=self.parallel_response_generation).start()
        # 状態制御スレッド
        threading.Thread(target=self.state_management).start()
        # 音声合成結果受信スレッド
        threading.Thread(target=self.listen_tts_loop).start()

        # dialbbをインスタンス化
        self.dialogue_processor = DialogueProcessor(app_conf)

        # システム発話から開始の場合
        if self.dialogue_processor:
            time.sleep(1)  # 他のスレッド起動タイミング（念のため）
            # 初回システム発話をリクエスト
            self.start_system_utterance()

    # 音声認識結果受信用のコールバックを登録
    def listen_asr_loop(self):
        self.subscribe('asr', self.callback_asr)

    # 音声合成結果受信用のコールバックを登録
    def listen_tts_loop(self):
        self.subscribe('tts', self.callback_tts)

    # 随時受信される音声認識結果の履歴
    def parallel_response_generation(self):
        # 受信したIUを保持しておく変数
        iu_memory = []
        new_iu_count = 0

        while True:
            # IUを受信して保存
            input_iu = self.input_iu_buffer.get()
            print(f'## parallel_response_generation(): {input_iu=}')
            iu_memory.append(input_iu)
            
            # IUがREVOKEだった場合はメモリから削除
            if input_iu['update_type'] == RemdisUpdateType.REVOKE:
                iu_memory = self.util_func.remove_revoked_ius(iu_memory)
            # ADD/COMMITの場合は応答候補生成
            else:
                user_utterance = self.util_func.concat_ius_body(iu_memory)
                print(f'## user_utterance={user_utterance}')
                if user_utterance == '':
                    continue

                # ADDの場合は閾値以上のIUが溜まっているか確認し，溜まっていなければ次のIUもしくはCOMMITを待つ
                if input_iu['update_type'] == RemdisUpdateType.ADD:
                    new_iu_count += 1
                    if new_iu_count < self.response_generation_interval:
                        continue
                    else:
                        new_iu_count = 0

                # インクリメンタルにdialbbは起動しないのでスキップ
                '''
                # パラレルな応答生成処理
                # 応答がはじまったらLLM自体がbufferに格納される
                llm = ResponseChatGPT(self.config, self.prompts)
                last_asr_iu_id = input_iu['id']
                t = threading.Thread(
                    target=llm.run,
                    args=(input_iu['timestamp'],
                          user_utterance,
                          self.dialogue_history,
                          last_asr_iu_id,
                          self.llm_buffer)
                )
                t.start()
                '''

                # ユーザ発話を順次接続する
                self.user_utterance_generation.append(user_utterance)
                print(f'{self.user_utterance_generation=}')

                # ユーザ発話終端の処理
                if input_iu['update_type'] == RemdisUpdateType.COMMIT:
                    # ASR_COMMITはユーザ発話が前のシステム発話より時間的に後になる場合だけ発出
                    if self.system_utterance_end_time < input_iu['timestamp']:
                        print(f'{self.system_utterance_end_time=}')
                        self.event_queue.put('ASR_COMMIT')
                    iu_memory = []

    # 対話状態を管理
    def state_management(self):
        while True:
            try:
                # イベントに応じて状態を遷移
                event = self.event_queue.get()
                print(f'## state_management(): {event=}')
                prev_state = self.state
                self.state = RemdisState.transition[self.state][event]
                print(f'********** State: {prev_state} -> {self.state}, Trigger: {event} **********')
                
                # 直前の状態がtalkingの場合にイベントに応じて処理を実行
                if prev_state == 'talking':
                    if event == 'SYSTEM_BACKCHANNEL':
                        pass
                    if event == 'USER_BACKCHANNEL':
                        pass
                    if event == 'USER_TAKE_TURN':
                        self.stop_response()
                    if event == 'BOTH_TAKE_TURN':
                        self.stop_response()
                    if event == 'TTS_COMMIT':
                        # 音声合成完了の場合、応答を中断
                        self.stop_response()
                    
                # 直前の状態がidleの場合にイベントに応じて処理を実行
                elif prev_state == 'idle':
                    print(f'## {event=}')
                    if event == 'SYSTEM_BACKCHANNEL':
                        self.send_backchannel()
                    if event == 'SYSTEM_TAKE_TURN':
                        self.send_response()
                    if event == 'ASR_COMMIT':
                        self.send_response()
            except Exception as e:
                print(e)
                break

    # システム発話を生成して送信
    def send_response(self):
        # 受信メッセージを取り出し
        print('>> send_response():')
        if self.llm_buffer.empty():
            # 一瞬スリープしてそれでも応答生成中にならなければシステムから発話を開始
            time.sleep(0.1)
            print(f'user_utterance_generation={self.user_utterance_generation}')
            llm_resp = self.get_system_utterance(self.user_utterance_generation)
        else:
            llm_resp = self.llm_buffer.get()

        # 生成中に状態が変わることがあるためその確認の後，発話を送信
        if self.state == 'talking':
            print(f'system_utterance={llm_resp["system_utterance"]}')
            snd_iu = self.createIU(llm_resp['system_utterance'], 'dialogue', RemdisUpdateType.ADD)
            self.printIU(snd_iu)
            self.publish(snd_iu, 'dialogue')
            self.output_iu_buffer.append(snd_iu)

        # 応答生成終了メッセージ
        print('End of selected llm response. Waiting next user uttenrance.\n')
        response = [d.get('content', '') for d in self.dialogue_history]
        snd_iu = self.createIU(''.join(response), 'dialogue', RemdisUpdateType.COMMIT)
        self.printIU(snd_iu)
        self.publish(snd_iu, 'dialogue')

        # 対話履歴をクリア
        self.dialogue_history = []
        self.user_utterance_generation = []

    # 応答を中断
    def stop_response(self):
        for iu in self.output_iu_buffer:
            iu['update_type'] = RemdisUpdateType.REVOKE
            self.printIU(iu)
            self.publish(iu, iu['exchange'])
        self.output_iu_buffer = []

    # 音声認識結果受信用のコールバック
    def callback_asr(self, ch, method, properties, in_msg):
        in_msg = self.parse_msg(in_msg)
        # 音声認識結果をバッファにセーブ（応答生成時に使用する）
        self.input_iu_buffer.put(in_msg)
        # print(f'## callback_asr(): {self.input_iu_buffer.queue=}')
        print('IN(asr):', end='')
        self.printIU(in_msg, flush=True)

    # 音声合成結果受信用のコールバック
    def callback_tts(self, ch, method, properties, in_msg):
        in_msg = self.parse_msg(in_msg)
        # 音声合成が完了か？
        if in_msg['update_type'] == RemdisUpdateType.COMMIT:
            self.output_iu_buffer = []
            # システム発話の終了タイムスタンプをセット
            self.system_utterance_end_time = in_msg['timestamp']
            # 音声合成完了イベントを発行
            self.event_queue.put('TTS_COMMIT')

    # 対話履歴を更新
    def history_management(self, role, utt):
        self.dialogue_history.append({"role": role, "content": utt})
        if len(self.dialogue_history) > self.history_length:
            self.dialogue_history.pop(0)

    # システム発話から開始
    def start_system_utterance(self):
        # 初期発話メッセージの生成
        request_json = {'user_id': self.dialbb_user_id}
        resp = self.dialogue_processor.process(request_json, initial=True)
        print(f"response: {str(resp)}")
        self.dialbb_session_id = resp.get('session_id')
        # 応答をキューイング
        self.llm_buffer.put(resp)
        # 応答を送信
        self.state = 'talking'
        self.send_response()

    # システム発話を生成
    def get_system_utterance(self, user_utter):
        print(f'get_system_utterance(): {user_utter=}')
        # dialbbを起動して応答生成
        req = {"user_id": self.dialbb_user_id, "session_id": self.dialbb_session_id,
               "user_utterance": user_utter[-1]}
        dialbb_resp = self.dialogue_processor.process(req)
        print(f'{dialbb_resp=}')

        return dialbb_resp


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", default="..\config\dialbb\config.yml",
                        help="application config file.")
    args = parser.parse_args()
    
    TEST_DIALBB().run(args.config)
