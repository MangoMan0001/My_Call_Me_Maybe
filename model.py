#!/usr/bin/env python3

import argparse
import json
import sys
import numpy as np
from llm_sdk import Small_LLM_Model
from typing import Generator


class LimitationModel():
    def __init__(self, args: argparse.Namespace) -> None:
        f_text = args.functions_definition.read_text(encoding="utf-8")
        i_text = args.input.read_text(encoding="utf-8")

        self.functions = json.loads(f_text)
        self.inputs = json.loads(i_text)
        self.model = Small_LLM_Model()
        vocab_path = self.model.get_path_to_vocab_file()
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        self.token_to_id = vocab
        self.id_to_token = {v: k for k, v in vocab.items()}
        self.output: list[dict[str, str | int]] = []

        self._get_fn_tokens()
        self._gen_prompt()
        self._gen_pre_output()
        self._gen_param_tokens()

    def _get_fn_tokens(self) -> None:
        self.fn_tokens: list[list[int]] = []

        for fn in self.functions:
            self.fn_tokens.append(
                self.model.encode(fn['name'] + '"').tolist()[0])

    def _gen_prompt(self) -> None:
        self.main_prompts: list[str] = []

        for prompt in self.inputs:
            self.main_prompts.append(
                f"""You are a strict AI assistant designed for function calling.
Your task is to analyze the user's prompt and generate a JSON object to call the correct function.

[Available Functions]
{json.dumps(self.functions, indent=2)}

[Rules]
1. You MUST choose one of the available functions.
2. You MUST extract the required parameters based on the function's definition.
3. You MUST respond ONLY with a valid JSON object. No markdown formatting like ```json, no greetings, no explanations.

[Output Format]
{{"name": "function_name", "parameters": {{"key": "value"}}}}

[User Prompt]
{prompt['prompt']}
""")

    def _gen_pre_output(self) -> None:
        """プロンプトによって変わらない出力フォーマットを用意する"""
        text = '{\n\t"name": "'
        self.pre_funtion_ouput: list[int] = self.model.encode(text).tolist()[0]

    def _gen_post_output(self) -> None:
        """選ばれた関数によって変わる変数名と変数の数で出力フォーマットを作成する"""
        text = [',\n\t"parameters": {"']
        chose_fn = "".join(
            self.model.decode(self.current_result)).split('"')[-2]
        params: dict[str, str] = {}
        for fn in self.functions:
            if fn['name'] == chose_fn:
                for key, value in fn['parameters'].items():
                    params[key] = value['type']
        for i, (key, value) in enumerate(params.items(), 1):
            text.append(f'{key}": {value}')
            if i < len(params):
                text.append(', "')

        text.append('}\n}')
        encode_text = self.model.encode("".join(text)).tolist()[0]
        self.post_funtion_ouput: list[int] = encode_text
        # for token in self.post_funtion_ouput:
        #     print(self.model.decode([token]))
        # sys.exit(1)

    def _gen_param_tokens(self) -> None:
        self._gen_num_tokens()
        self._gen_str_tokens()

    def _gen_num_tokens(self) -> None:
        nm = ['-', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.num_tokens = [self.token_to_id[token] for token in nm]

    def _gen_str_tokens(self) -> None:
        self.str_tokens: list[int] = []
        self.dquote_token: list[int] = []
        self.str_end_token_1: list[int] = []
        self.str_end_token_2: list[int] = []
        for id, token in self.id_to_token.items():
            if '"' == token:
                self.dquote_token.append(id)
            # elif token == '"}':
            #     self.str_end_token_1.append(id)
            # elif token == '",':
            #     self.str_end_token_2.append(id)
            else:
                self.str_tokens.append(id)
        # for id, token in self.id_to_token.items():
        #     if '"' in token:
        #         if token == '"':
        #             self.dquote_tokens.append(id)
        #     else:
        #         self.str_tokens.append(id)

    def run(self) -> None:
        try:
            for main_prompt, prompt in zip(self.main_prompts, self.inputs):
                print('-------- run --------')
                self._run_model(main_prompt)
                self._gen_output(prompt)
                for object in self.output:
                    print(object)
                print(self.model.decode(self.current_result))
                print(json.dumps(self.output, indent=4))
                print('---------------------')
                print()
                # sys.exit(1)
        except Exception as e:
            print(e)
            for object in self.output:
                print(object)
            print(self.model.decode(self.current_result))
            print(json.dumps(self.output, indent=4))
            sys.exit(1)

    def _run_model(self, prompt: str) -> None:
        self.current_result: list[int] = []
        tokens: list[int] = []
        tokens = self.model.encode(prompt).tolist()[0]

        state_gen = self._status_manager()

        try:
            allowed_tokens = next(state_gen)
        except StopIteration:
            return
        while True:
            # logitsを要求
            print('logitsを要求')
            logits = self.model.get_logits_from_input_ids(tokens)

            print('arryに')
            # logits_arr = np.array(logits)
            # ソートで昇順に
            # top_indices = np.argsort(logits_arr)[-5:][::-1]

            top_indices = sorted(range(len(logits)),
                                 key=lambda i: logits[i], reverse=True)[:5]

            print("\n--- preトークン ---")
            for idx in top_indices:
                token_str = self.model.decode([idx])
                score = logits[idx]
                print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

            # 状態分けでlogitsの中身を変更
            print('状態分けでlogitsの中身を変更')
            original = np.array(logits)
            masked = np.full_like(original, -np.inf)
            masked[allowed_tokens] = original[allowed_tokens]
            logits[:] = masked.tolist()

            # ソートで昇順に
            top_indices = sorted(range(len(logits)),
                                 key=lambda i: logits[i], reverse=True)[:5]

            # top_indices = np.argsort(masked)[-5:][::-1]
            print("\n--- postトークン ---")
            for idx in top_indices:
                token_str = self.model.decode([idx])
                score = logits[idx]
                print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

            # 一番スコアが高い「次の一文字（ID）」を決める
            print('一番スコアが高い「次の一文字（ID）」を決める')
            next_token_id = logits.index(max(logits))
            # next_token_id = int(np.argmax(masked))
            self.current_result.append(next_token_id)

            # トークンを選択
            print('トークンを選択')
            try:
                allowed_tokens = state_gen.send(next_token_id)
            except StopIteration:
                break

            # 終了じゃなければ、出力済みの配列に付け足して、次のループへ！
            print('終了じゃなければ、出力済みの配列に付け足して、次のループへ！')
            tokens.append(next_token_id)

    def _status_manager(self) -> Generator[list[int], int, None]:
        for token in self.pre_funtion_ouput:
            chosen_token = yield [token]

        possible_paths = self.fn_tokens.copy()
        while possible_paths:
            # 各関数トークンリストの先頭のみ抜粋
            allowed_token = list(set(path[0] for path in possible_paths))

            chosen_token = yield allowed_token

            # 選ばれなかったトークンから始まる関数をリストから除外
            left_tokens = [path for path in possible_paths
                           if path[0] == chosen_token]

            # 各関数リストの先頭を削除
            possible_paths = [path[1:] for path in left_tokens
                              if len(path) > 1]

        self._gen_post_output()
        prev_tokens: list[int] = [self.post_funtion_ouput[0]]
        iter_post_output = iter(self.post_funtion_ouput)
        # for token in self.post_funtion_ouput:
        #     print(self.model.decode([token]))
        # print(self.model.decode(self.current_result))
        # sys.exit(1)
        for token in iter_post_output:
            # number
            if (self.model.decode([prev_tokens[-1]]) == '":' and
                    self.model.decode([token]) == ' number'):
                next_token = next(iter_post_output)
                while True:
                    chosen_token = yield self.num_tokens + [next_token]
                    if chosen_token == next_token:
                        break
                continue
            # string
            if (self.model.decode([prev_tokens[-1]]) == '":' and
                    self.model.decode([token]) == ' string'):
                _ = yield self.dquote_token

                str_tokens = self.str_tokens + self.dquote_token
                while True:
                    chosen_token = yield str_tokens
                    if chosen_token == self.dquote_token[0]:
                        break
                    elif ('",' in self.model.decode([chosen_token]) or
                          '"}' in self.model.decode([chosen_token])):
                        next(iter_post_output)
                        break
                continue
            # bool
            if (self.model.decode([prev_tokens[-1]]) == '":' and
                    self.model.decode([token]) == ' boolean'):
                possible_paths = (self.model.encode('"true"').tolist()[0] +
                                  self.model.encode('"false"').tolist()[0])
                while possible_paths:
                    # 各boolトークンリストの先頭のみ抜粋
                    allowed_token = list(set(path[0]
                                             for path in possible_paths))

                    chosen_token = yield allowed_token

                    # 選ばれなかったトークンから始まるboolをリストから除外
                    left_tokens = [path for path in possible_paths
                                   if path[0] == chosen_token]

                    # 各boolリストの先頭を削除
                    possible_paths = [path[1:] for path in left_tokens
                                      if len(path) > 1]
                continue
            # null
            if (self.model.decode([prev_tokens[-1]]) == '":' and
                    self.model.decode([token]) == ' null'):
                null_tokens = self.model.encode('"null"').tolist()[0]
                for token in null_tokens:
                    _ = yield [token]
                continue

            prev_token = yield [token]
            prev_tokens.append(prev_token)

    def _gen_output(self, prompt: dict[str, str]) -> None:
        model_result = json.loads(
            "".join(self.model.decode(self.current_result)))
        json_object: dict[str, str | int] = {
            **prompt,
            **model_result
        }
        self.output.append(json_object)
