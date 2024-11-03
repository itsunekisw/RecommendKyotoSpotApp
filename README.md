# Recommend Kyoto Spot App
## Environment
- python = 3.11.7
- transformers
- pytorch
- scipy
- (conda activate language)

## Input
『理想の旅行先のイメージを文章で入力してください』という指示に従って、日本語で希望の旅行先のイメージを入力
### 入力例
「家族で楽しめる」

## Algorithm
1. じゃらんのWebページからBeautifulSoup.pyでスクレイピングした結果をoutput.csvに保存
2. model.pyのSentencLukeJapaneseクラス内のupdata_csv関数を用いて、レビューのコメントをベクトル化
    1. コメントをトークン化
    2. `sonoisa/sentence-luke-japanese-base-lite`の学習済みモデルを用いて、各トークンについてベクトル化
    3. 各トークンのベクトルの平均を、レビューのベクトルとして算出
  4. 各レビューについて算出したベクトルをoutput.csvに追加して更新
3. 入力された文章について、上記と同様にベクトル化して、ベクトルのコサイン類似度が大きい順に返す
4. コサイン類似度が大きいレビューについて出力して、ユーザーにレコメンド
### スクレイピング内容
- 観光地
- レビューのタイトル
- レビューの評価
- レビューのコメント

## Output Image
![image](prompt.png)
