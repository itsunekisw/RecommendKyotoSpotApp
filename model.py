from transformers import MLukeTokenizer, LukeModel
import torch
from scipy.spatial import distance
import pandas as pd
import numpy as np
import ast


class SentenceLukeJapanese:
    def __init__(self, model_name_or_path, device=None):
        self.tokenizer = MLukeTokenizer.from_pretrained(model_name_or_path)
        self.model = LukeModel.from_pretrained(model_name_or_path)
        self.model.eval()

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(device)
        # 指定したCSVファイルの指定した列をリスト化

    # CSVに集められたテキストをベクトル化してCSVに保存
    def update_csv(self, csv_file_path, target_column_name, execute=True):
        if execute == False:
            return
        df = pd.read_csv(csv_file_path)
        self.texts = df[target_column_name].tolist()
        texts_embedding = self.encode(self.texts, batch_size=8)
        df["vector"] = texts_embedding.tolist()
        df.to_csv(csv_file_path[:-4] + "_encoded.csv", index=False)

    def read_csv(self, csv_file_path, target_column_name):
        self.data = pd.read_csv(csv_file_path)
        # apply(ast.literal_eval): 文字列として入っているリストをlist型に変換
        self.vectors = self.data[target_column_name].apply(ast.literal_eval)
        self.sentence_embeddings = []
        for vector in self.vectors:
            self.sentence_embeddings.append(vector)

    # 入力された文章をベクトル化して、類似度の高い順にindexを返す
    def calc_distance(self, query):
        query_embedding = self.encode([query], batch_size=8)
        # 既にエンコードした600文のベクトルと入力された文章の1文を結合
        sentence_embeddings = np.concatenate(
            (self.sentence_embeddings, query_embedding), axis=0
        )
        # 入力した文章と他の文章との類似度を計算
        distances = distance.cdist(
            [sentence_embeddings[-1]], sentence_embeddings, metric="cosine"
        )[0]
        # indexと距離をペアにし、類似度x[1]を基準にソート
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])
        return results

    # 複数の文章をベクトル化
    @torch.no_grad()
    def encode(self, sentences, batch_size=8):
        all_embeddings = []
        iterator = range(0, len(sentences), batch_size)
        print("Encoding sentences...", end=" ")
        for batch_idx in iterator:
            batch = sentences[batch_idx : batch_idx + batch_size]
            # 文章をトークン化
            encoded_input = self.tokenizer.batch_encode_plus(
                batch, padding="longest", truncation=True, return_tensors="pt"
            ).to(self.device)
            # トークンごとにベクトル化
            model_output = self.model(**encoded_input)
            # 文章全体のベクトルを各トークンのベクトルの平均とする
            sentence_embeddings = self._mean_pooling(
                model_output, encoded_input["attention_mask"]
            ).to("cpu")
            all_embeddings.extend(sentence_embeddings)
            print(
                f"{batch_idx}/{len(sentences)}...",
                end=" ",
            )
        print("Done!")
        return torch.stack(all_embeddings)

    # モデル出力と拡張分を0にするマスクをかけ合わせ、平均を計算
    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )


def recommendSpot(query, closest_n):
    # 既存モデルの読み込み
    MODEL_NAME = "sonoisa/sentence-luke-japanese-base-lite"
    model = SentenceLukeJapanese(MODEL_NAME)

    # CSVファイル上の口コミをベクトルに変換
    csv_file_path = "review_data/output20240812.csv"
    model.update_csv(csv_file_path, "reviewComment", execute=False)

    # CSVファイル上の口コミのベクトルを取得
    csv_file_path = "review_data/output20240812_encoded.csv"
    model.read_csv(csv_file_path, "vector")

    results = model.calc_distance(query)
    print("======================")
    print("Query:", query)
    print("\nお勧めの京都の旅行先は:")
    for idx, distance in results[1 : closest_n + 1]:
        review = model.data.iloc[idx]
        print("Tourist Spot\t", review["Spot"])
        print("Review Title\t", review["reviewTitle"])
        print("Review Score\t", review["reviewScore"])
        # strip(): 文字列内の空白文字を全て消去
        print("Review Comment\t", review["reviewComment"].strip())
        print("Similarity\t", 1 - distance, "\n")


if __name__ == "__main__":
    # 入力された文章に対して類似度の大きい口コミを取得
    query = input(
        "\n理想の旅行先のイメージを文章で入力してください。　例)『家族で楽しめる』『綺麗な景色』『歴史的な街並み』\n"
    )
    while True:
        try:
            closest_n = int(
                input("\n何個観光地をお勧めしてほしいか、正の整数で入力してください。")
            )
            if closest_n <= 0 or closest_n % 1 != 0:
                continue
            break
        except:
            continue
    recommendSpot(query, closest_n)
