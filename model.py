from transformers import MLukeTokenizer, LukeModel
import torch
import scipy.spatial
import pandas as pd


class SentenceLukeJapanese:
    def __init__(self, model_name_or_path, device=None):
        self.tokenizer = MLukeTokenizer.from_pretrained(model_name_or_path)
        self.model = LukeModel.from_pretrained(model_name_or_path)
        self.model.eval()

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(device)

    # モデル出力のトークン埋め込みを平均化し、その値とマスクをかけ合わせ、合計を計算-----------------------
    def _mean_pooling(self, model_output, attention_mask):
        # モデルの出力であるトークンの埋め込み行列取得 [batch_size, sequence_length, hidden_size]
        token_embeddings = model_output[0]

        # マスクの次元をtoken_embeddingsと同じ形状に拡張[batch_size, sequence_length, 1] => [batch_size, sequence_length, hidden_size]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )

        # 文全体の平均埋め込みベクトルを計算、sum(1): 第2次元（"sequence_length"）について総和を計算
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    # 勾配の計算を無効にし、メモリ使用量を節約（PyTorchのデコレータで、今回はモデルの学習は行わず、推論のみを行なう）
    @torch.no_grad()
    def encode(self, sentences, batch_size=8):
        all_embeddings = []
        iterator = range(0, len(sentences), batch_size)
        for batch_idx in iterator:
            batch = sentences[batch_idx : batch_idx + batch_size]

            # 文章をトークン化
            encoded_input = self.tokenizer.batch_encode_plus(
                batch, padding="longest", truncation=True, return_tensors="pt"
            ).to(self.device)

            # トークン化文章からモデル出力を取得し、
            model_output = self.model(**encoded_input)
            sentence_embeddings = self._mean_pooling(
                model_output, encoded_input["attention_mask"]
            ).to("cpu")
            all_embeddings.extend(sentence_embeddings)

        return torch.stack(all_embeddings)

    def read_csv(self, csv_file_path, target_column_name):
        self.sentences = []
        self.data = pd.read_csv(csv_file_path)
        self.sentences = self.data[target_column_name].tolist()

    def update_csv(self, csv_file_path, target_column_name):
        df = pd.read_csv(csv_file_path)
        self.texts = self.data[target_column_name].tolist()
        texts_embedding = self.encode(self.texts, batch_size=8)
        print(texts_embedding)
        df["vector"] = texts_embedding.tolist()
        print(df)
        df.to_csv(csv_file_path)

    def recommend(self, query):
        self.sentences.append(query)
        print("Encoding sentences...", end=" ")
        sentence_embeddings = self.encode(self.sentences, batch_size=8)
        print("Done!")
        # 入力した文章と他のすべての文章との間のコサイン距離が計算される
        distances = scipy.spatial.distance.cdist(
            [sentence_embeddings[-1]], sentence_embeddings, metric="cosine"
        )[0]
        # インデックスと距離をペアにし、コサイン距離x[1]を基準にソート
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        return results


# 既存モデルの読み込み
MODEL_NAME = "sonoisa/sentence-luke-japanese-base-lite"
model = SentenceLukeJapanese(MODEL_NAME)

# 口コミを取得してリスト化
csv_file_path = "output.csv"
target_column_name = "reviewComment"
model.read_csv(csv_file_path, target_column_name)
model.update_csv(csv_file_path, target_column_name)

# query = input("理想の旅行先のイメージを文章で入力してください。\n")
# results = model.recommend(query)

# 類似度上位5つを出力
# closest_n = 5
# print("======================")
# print("Query:", query)
# print("\nオススメの京都の旅行先は:")
# for idx, distance in results[1 : closest_n + 1]:
#     print("旅行先\t\t", model.data.iloc[idx, 0])
#     print("タイトル\t", model.data.iloc[idx, 1])
#     print("評価\t\t", model.data.iloc[idx, 2])
#     print("口コミ\t\t", model.sentences[idx].strip())
#     print("類似度\t\t", 1 - distance, "\n")
