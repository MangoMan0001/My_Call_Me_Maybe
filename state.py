#!/usr/bin/env python3

class JSONStateMachine:
    def __init__(self, allowed_functions: list):
        self.state = 0  # 現在の関所の状態
        self.allowed_functions = allowed_functions
        self.current_json_string = ""

    def get_allowed_tokens(self) -> list[int]:
        # 今の self.state に合わせて、許可するトークンIDのリストを返す！
        if self.state == 0:
            return encode_tokens(['{'])
        # ... 以降の関所ルール ...

    def update_state(self, generated_token: str):
        # AIが出力したトークンを見て、self.state を +1 したりする！
        self.current_json_string += generated_token
        # ... 状態更新のロジック ...
