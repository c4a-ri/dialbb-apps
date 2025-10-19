# dialbb-connect-client.py
import sys
import re
import time
import yaml
import argparse
from typing import Dict, Any, Tuple, Optional
import requests
import re

# 入出力の文字列を UTF-8 にする
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


def set_request(user_id: str = '', session_id: str = '',
                user_utterance: str = ''):
    data = {
        "user_id": user_id,
        "session_id": session_id,
        "user_utterance": user_utterance,
        "aux_data": {}
    }

    return data


def post_request(endpoint: str = '', data: Dict = None):
    headers = {"content-type": "application/json"}
    result = {}
    if not data:
        data = []
    try:
        # POSTリクエストを送信
        response = requests.post(f'{url}/{endpoint}', json=data,
                                 headers=headers)
        # ステータスコードを確認
        if response.status_code == 200:
            # レスポンスデータを表示
            result = response.json()
            # print("Resource created:", result)

        else:
            print(f"Failed to connect: Status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        # 例外処理
        print(f"Error occurred: {e}")
        sys.exit(1)
    
    return result

# do gesture
def exec_motion(motion_table: Dict[str, str], motion_name: str):

    motion_file = motion_table.get(motion_name)
    if motion_file:
        print(f"MOTION_ADD|0|action|{motion_file}")

def split_motion(s: str) -> Tuple[str, Optional[str]]:
    """
    文字列 s の末尾に (motion: <motion_id>) がある場合、
    (<motion_id> を除いた文字列, <motion_id>) のタプルを返す。
    見つからない場合は (s, None) を返す。
    """
    match = re.search(r'\s*\(motion:\s*([^)]+)\)\s*$', s)
    if match:
        motion_id = match.group(1)
        # (motion: xxx)部分を削除して末尾の空白も除去
        s_clean = re.sub(r'\s*\(motion:\s*([^)]+)\)\s*$', '', s).rstrip()
        return s_clean, motion_id
    else:
        return s, None


def speak_and_move(resp, motion_table):

    # 応答文を SYNTH_START メッセージとして出力
    utterance = resp.get('system_utterance')
    utterance = utterance.strip()
    utterance, motion_name = split_motion(utterance)

    # 発話
    if utterance and utterance not in ("empty", "silence"):  # empty, silenceの場合は何も話さない
        print(f"SYNTH_START|0|mei_voice_normal|{utterance}")

    # ジェスチャーの実行
    if motion_name:
        exec_motion(motion_table, motion_name)



# メイン
def main(url: str, motion_table_file: str):
    # print(f'START connect to url={url}')
    user_id = 'user1'

    # ジェスチャーテーブル読み込み
    with open(motion_table_file, 'r', encoding='utf-8') as f:
        motion_table = yaml.safe_load(f)

    # 初期発話メッセージ送信
    time.sleep(3)
    # 送信データ設定
    data = set_request(user_id=user_id)
    # リクエスト送信
    resp = post_request('init', data)

    # 応答データの抽出
    session_id = resp.get('session_id')

    # 最初の発話
    speak_and_move(resp, motion_table)

    while True:
        # MMDAgentからの入力
        instr = input().strip()
        # 入力が RECOG_EVENT_STOP かどうか調べる
        utterance = re.findall('^RECOG_EVENT_STOP\|(.*)$', instr)

        if utterance:
            # dialbb-serverにメッセージ送信
            data = set_request(user_id=user_id, session_id=session_id,
                               user_utterance=utterance[0])
            # POSTリクエストを送信
            resp = post_request('dialogue', data)
            speak_and_move(resp, motion_table)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="dialbb server host", default="localhost")
    parser.add_argument("--port", help="port number", default=8080)
    parser.add_argument("--motion_table", help="motion table file", required=True)
    args = parser.parse_args()
    
    url = f"http://{args.host}:{args.port}"
    main(url, args.motion_table)
