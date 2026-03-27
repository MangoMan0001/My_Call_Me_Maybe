#!usr/bin/env python3

import json
import sys
import os

sys.path.insert(0, os.path.abspath("llm_sdk"))

from llm_sdk import Small_LLM_Model

TARGET_TOKEN = []
STATE = 0

def main() -> None:
    print("🤖 モデルをロード...")
    model = Small_LLM_Model()

    # 辞書作成
    vocab_path = model.get_path_to_vocab_file()
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    id_to_token = {v: k for k, v in vocab.items()}

    # 1. テストプロンプトを用意
    # prompt = "What is the sum of 2 and 3?"
    entry_prompt = "２と３を足したら？"
    print(f"\n📝 初期プロンプト: '{entry_prompt}'")

    target_id = [int(model.encode(token)[0]) for token in TARGET_TOKEN]
    print(f"target_token {TARGET_TOKEN}")
    print(f"target_id: {target_id}")

    tokens = model.encode(entry_prompt).tolist()[0]
    test_tokens = model.encode('"name"').tolist()[0]
    for token in test_tokens:
        print(model.decode(token))
    test_tokens = model.encode("fn_add_numbers").tolist()[0]
    for token in test_tokens:
        print(model.decode(token))

    for step in range(30):
        prompt = model.decode(tokens)
        print(f"\n📝 現在プロンプト: '{prompt}'")

        # 4. LLMに「次に来る言葉のスコア（Logits）」を要求
        logits = model.get_logits_from_input_ids(tokens)

        # 5. スコアが高い順に並べ替えて、トップ5を表示
        top_indices = sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)[:5]

        print("\n--- preトークン Top 5 ---")
        for idx in top_indices:
            token_str = model.decode([idx])
            score = logits[idx]
            print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

        print("\n---- classify token ---")

        print("\n--- postトークン Top 5 ---")
        for idx in top_indices:
            token_str = model.decode([idx])
            score = logits[idx]
            print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

        # 2. 一番スコアが高い「次の一文字（ID）」を決める
        next_token_id = logits.index(max(logits))

        # 一番スコアが高い「次の一文字（ID）」を文字にする
        next_token = model.decode([next_token_id])
        print(f"選択されたtoken: {next_token}")

        # 4. 終了じゃなければ、出力済みの配列に付け足して、次のループへ！
        tokens.append(next_token_id)
        print(model.decode([next_token_id]), end="", flush=True)

if __name__ == "__main__":
    main()
