# conda activate language

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

url = "https://www.jalan.net/kankou/260000/"
res = requests.get(url)
soup = BeautifulSoup(res.content, "html.parser")

# これしないと文字化け
soup = BeautifulSoup(res.content.decode("Shift-JIS", "ignore"), "html.parser")

# re.compile: href属性の中で引数を含むもののみ抽出
elems = soup.find_all(href=re.compile("/kuchikomi"))
pickup_links = [elem.attrs["href"] for elem in elems]
# print(pickup_links)

# csvファイル化するためのデータフレーム
df = pd.DataFrame()

# 一覧のリンクを順に処理--------------------
for elem, pickup_link in zip(elems, pickup_links):

    # 口コミ数20件以上なかったらスキップ--------
    if int(re.findall(r"\d+", elem.contents[0])[-1]) <= 20:
        continue

    # requests.get(): Pickupページへ遷移しページの情報を取得--------
    pickup_res = requests.get("https:" + pickup_link)
    pickup_soup = BeautifulSoup(pickup_res.text, "html.parser")
    pickup_soup = BeautifulSoup(
        pickup_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )

    # 観光地の名前-----------------------------
    spot_path = pickup_soup.find("p", class_="detailTitle")
    spot = spot_path.contents[0]
    print("\nSightseeingSpot: ", spot)

    # new_list: その観光地の名前、口コミをまとめたリスト---------
    new_list = [spot]

    # comments: 口コミ内容(ニュースのテキスト情報を取得し表示)-------------
    comments = pickup_soup.find_all("p", class_="reviewCassette__comment")
    if len(comments) == 0:
        comments = pickup_soup.find_all("div", class_="item-reviewTextInner")

    for comment in comments:
        new_list.append(comment.contents[0])

    # new_df: 現在のループの観光地の名前、口コミをまとめたデータフレーム------
    new_df = pd.DataFrame(data=[new_list])
    df = df._append(new_df)

    # 観光地が30か所集まったらスクレイピング終了
    if df.shape[0] == 30:
        print("break!")
        break
    print(df.shape)

df = df.reset_index()
df.to_csv("output.csv", index=False, encoding="utf-8")

print(df)
# df
