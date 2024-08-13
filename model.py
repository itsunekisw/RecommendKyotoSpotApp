from transformers import MLukeTokenizer, LukeModel

# 深層学習モデルの操作やGPU対応を行なう
import torch

# scipyライブラリの空間計算モジュール、コサイン距離を計算するために使用
import scipy.spatial
import pandas as pd


class SentenceLukeJapanese:
    def __init__(self, model_name_or_path, device=None):
        self.tokenizer = MLukeTokenizer.from_pretrained(model_name_or_path)
        self.model = LukeModel.from_pretrained(model_name_or_path)
        # モデルを評価モードに切り替え
        self.model.eval()

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        # モデルを指定したデバイスに転送
        self.model.to(device)

    def _mean_pooling(self, model_output, attention_mask):
        # モデルの出力であるトークンの埋め込み行列
        token_embeddings = model_output[0]
        # First element of model_output contains all token embeddings
        # attention_maskに基づいてマスクされたトークン埋め込みを取得し、それらの埋め込みを平均化
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        # torch.clump: ゼロ除算を避けるために使用
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    # 勾配の計算を無効にし、メモリ使用量を節約する
    # PyTorchのデコレータで、今回はモデルの学習は行わず、推論のみを行なう
    @torch.no_grad()
    def encode(self, sentences, batch_size=8):
        all_embeddings = []
        iterator = range(0, len(sentences), batch_size)
        for batch_idx in iterator:

            # batch_sizeずつ文章を抽出
            batch = sentences[batch_idx : batch_idx + batch_size]

            # "self.tokenizer.batch_encode_plus": 文章をトークン化し、指定されたデバイスに転送
            # "padding=longest": バッチ内の最長の文章に合わせて、他の文章を補填する。これによって、すべての文章が同じ長さのトークン列を持つようになる
            # "truncation=True": 文章が長すぎる場合、自動的にカット
            # "return_tensors=pt": 出力をPyTorchのテンソル形式にします。これによって、モデルに直接入力できる形になる
            encoded_input = self.tokenizer.batch_encode_plus(
                batch, padding="longest", truncation=True, return_tensors="pt"
            ).to(self.device)

            # self.model: トークン化された文章を入力してモデル出力を取得
            # 出力は、文章内の各トークンに対応するベクトルの集合を含む
            model_output = self.model(**encoded_input)

            # _mean_poolingを使用して文章全体の埋め込みを計算する。これは各トークンの埋め込みの平均を取ることで行う
            # "attention_mask": パディングされた部分を無視するためのマスクで、これを用いて正しい埋め込みを計算する
            sentence_embeddings = self._mean_pooling(
                model_output, encoded_input["attention_mask"]
            ).to("cpu")

            # 計算された各バッチの埋め込みをリストに追加。この処理がすべてのバッチに対して行われる（リストの中にフラットに追加）
            all_embeddings.extend(sentence_embeddings)

        # 全ての埋め込みをリストに追加し、"torch.stack"でテンソルとして返す（新しい次元で結合）
        return torch.stack(all_embeddings)


# 既存モデルの読み込み
MODEL_NAME = "sonoisa/sentence-luke-japanese-base-lite"
model = SentenceLukeJapanese(MODEL_NAME)

# 説明文を入れるリストを作成
sentences = []

# CSVファイルのパスを指定
csv_file_path = "output.csv"

# 読み込む列の名前を指定
target_column_name = "reviewComment"

# CSVファイルをDataFrameとして読み込む
data = pd.read_csv(csv_file_path)

# 指定した列のデータをリストに追加
sentences = data[target_column_name].tolist()

# 標準入力で、理想のビールのイメージを文章で受け取る
query = input("理想の旅行先のイメージを文章で入力してください。\n")
sentences.append(query)
# print("sentences\n", sentences)

# ビールの説明文、受け取った文章をエンコード（ベクトル表現に変換）
sentence_embeddings = model.encode(sentences, batch_size=8)

# 類似度上位5つを出力
closest_n = 5

# sentence_embeddings[-1]: ユーザーが入力したクエリに対応する文章の埋め込み
# scipy.spatial.distance.cdist: ２つの集合管のペアごとの距離を計算する
# metric="cosine": コサイン距離を計算することを指定（コサイン類似度の逆数にあたる）
# 入力した文章と他のすべての文章との間のコサイン距離が計算される
# cdistの結果は2次元配列で返されるが、入力した文章との距離のみを扱いたいため、最初の行を抽出
distances = scipy.spatial.distance.cdist(
    [sentence_embeddings[-1]], sentence_embeddings, metric="cosine"
)[0]
# print("distances\n", distances)

# インデックスと距離をペアにする
results = zip(range(len(distances)), distances)

# コサイン距離x[1]を基準にソート
results = sorted(results, key=lambda x: x[1])
# print("results\n", results)

print("\n\n======================\n\n")
print("Query:", query)
print("\nオススメの京都の旅行先は:")

# print(data.iloc[results[1][0]])

for idx, distance in results[1 : closest_n + 1]:
    print("旅行先\t\t", data.iloc[idx, 0])
    print("タイトル\t", data.iloc[idx, 1])
    print("評価\t\t", data.iloc[idx, 2])

    print("口コミ\t\t", sentences[idx].strip())
    print("類似度\t\t", 1 - distance, "\n")
