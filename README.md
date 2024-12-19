# Recommend Kyoto Spot App
## Environment
- python = 3.11.7
- transformers = 4.17.0
- pytorch = 2.4.0
- scipy = 1.11.4
- (conda activate language)
- pandas = 2.2.3
- sentensepiece = 0.2.0

## Desktop App
### 1. Execute KyotoRecommendApp.py.
- `python KyotoRecommendApp.py`
### 2. Input a description of your Ideal Travel Destination in Japanese.
- For example, "家族で楽しめる", "綺麗な景色", "歴史的な街並み", stc.

<img src="images/input_image.png">

### 3. Click Enter button, or "EXECUTE" button.
### 4. You will see recommended Tourist spots in Kyoto.

<img src="images/output_image.png">

## Algorithm
1. じゃらんのWebページからBeautifulSoup.pyでスクレイピングした結果をoutput{%Y%m%d}.csvに保存
2. model.pyのSentencLukeJapaneseクラス内のupdate_csv関数を用いて、レビューのコメントをベクトル化
    1. コメントをトークン化
    2. `sonoisa/sentence-luke-japanese-base-lite`の学習済みモデルを用いて、各トークンについてベクトル化
    3. 各トークンのベクトルの平均を、レビューのベクトルとして算出
    4. 各レビューについて算出したベクトルをoutput{%Y%m%d}_encoded.csvに追加して更新
3. 入力された文章についても上記と同様にベクトル化して、ベクトルのコサイン類似度が大きい順に返す
4. コサイン類似度が大きいレビューを出力
### スクレイピング内容
- 観光地
- レビューのタイトル
- レビューの評価
- レビューのコメント

## Input
『理想の旅行先のイメージを文章で入力してください』という指示に従って、日本語で希望の旅行先のイメージを入力
### 入力例
「家族で楽しめる」

## Output Prompt
- 入力されたユーザーの希望に近いレビューを探索して、上位の結果を出力してくれる

![image](images/prompt.png)
