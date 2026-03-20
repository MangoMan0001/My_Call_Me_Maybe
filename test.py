#!usr/bin/env python3

import json
import sys
import os

sys.path.insert(0, os.path.abspath("llm_sdk"))

from llm_sdk import Small_LLM_Model

TARGET_TOKEN = ['{', '}']

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
    prompt = "２と３を足したら？"
    print(f"\n📝 初期プロンプト: '{prompt}'")

    eos_token_id = model._tokenizer.eos_token_id
    print(f"🛑 このモデルの終了フラグID: {eos_token_id}")

    target_id = [int(model.encode(token)[0]) for token in TARGET_TOKEN]
    print(f"target_token {TARGET_TOKEN}")
    print(f"target_id: {target_id}")
    print(type(model.encode('{')))

    ids = model._tokenizer.encode(prompt)

    for step in range(30):
        prompt = model.decode(ids)
        print(f"\n📝 現在プロンプト: '{prompt}'")

        # 4. LLMに「次に来る言葉のスコア（Logits）」を要求
        logits = model.get_logits_from_input_ids(ids)

        # 5. スコアが高い順に並べ替えて、トップ5を表示
        top_indices = sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)[:5]

        print("\n🏆 --- 次に来る確率が高いトークン Top 5 ---")
        for idx in top_indices:
            token_str = model.decode([idx])
            score = logits[idx]
            print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

        for i in range(len(logits)):
            if i not in target_id:
                logits[i] = -float('inf')

        # 2. 一番スコアが高い「次の一文字（ID）」を決める
        next_token_id = logits.index(max(logits))

        # 一番スコアが高い「次の一文字（ID）」を文字にする
        next_token = model.decode([next_token_id])
        print(f"選択されたtoken: {next_token}")

        # 3. 💥 終了判定！ 出てきたIDが終了フラグだったらループを抜ける！
        if next_token_id == eos_token_id:
            print("\n✨ AI「これで私のお話は終わりですわ！」")
            break

        # 4. 終了じゃなければ、出力済みの配列に付け足して、次のループへ！
        ids.append(next_token_id)
        print(model.decode([next_token_id]), end="", flush=True)

if __name__ == "__main__":
    main()
