#!usr/bin/env python3

import json
from llm_sdk.__init__ import Small_LLM_Model

def main() -> None:
    print("🤖 モデルをロードしていますわ...（初回はダウンロードが入るかもしれません）")
    model = Small_LLM_Model()

    # 1. LLMが知っている全単語の「辞書（ボキャブラリー）」を読み込みますわ
    vocab_path = model.get_path_to_vocab_file()
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    # IDから文字（トークン）を引けるように「逆引き辞書」を作りますの
    id_to_token = {v: k for k, v in vocab.items()}

    # 2. 課題にあるテストプロンプトを用意しますわ
    prompt = "What is the sum of 2 and 3?"
    print(f"\n📝 プロンプト: '{prompt}'")

    # 3. プロンプトをAIが読める「数字（トークンID）」の配列に変換しますわ
    # （※_tokenizerはSmall_LLM_Modelの内部変数ですの）
    input_ids = model._tokenizer.encode(prompt)
    print(f"🔢 変換された入力ID: {input_ids}")

    # 4. LLMに「次に来る言葉のスコア（Logits）」を出させますわ！
    logits = model.get_logits_from_input_ids(input_ids)
    print(f"📊 スコア配列の長さ（全語彙数）: {len(logits)}")

    # 5. スコアが高い順に並べ替えて、トップ5を表示してみましょう！
    top_indices = sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)[:5]

    print("\n🏆 --- 次に来る確率が高いトークン Top 5 ---")
    for idx in top_indices:
        token_str = id_to_token.get(idx, "???")
        score = logits[idx]
        print(f"ID: {idx:6} | スコア: {score:7.2f} | トークン: '{token_str}'")

if __name__ == "__main__":
    main()
