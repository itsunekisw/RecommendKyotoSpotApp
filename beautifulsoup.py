# conda activate language
# conda install transformers
# conda install sentencepiece
# pip install torch
# pip install scipy

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

# csvファイル化するためのデータフレーム
df = pd.DataFrame()

# 一覧のリンクを順に処理-------------
for elem, pickup_link in zip(elems, pickup_links):

    # 口コミ数20件以上なかったらスキップ------------
    if int(re.findall(r"\d+", elem.contents[0])[-1]) <= 20:
        continue

    # requests.get(): Pickupリンクへ移動してページ１の情報取得の準備-----
    page1_res = requests.get("https:" + pickup_link)
    page1_soup = BeautifulSoup(page1_res.text, "html.parser")
    page1_soup = BeautifulSoup(
        page1_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )
    # ページ２へ移動して、情報取得の準備--------------
    page2_elem = page1_soup.find(href=re.compile("/page_2/"))
    page2_link = page2_elem.attrs["href"]
    page2_res = requests.get(page2_link)
    page2_soup = BeautifulSoup(page2_res.text, "html.parser")
    page2_soup = BeautifulSoup(
        page2_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )
    # ページ３へ移動して、情報取得の準備----------
    page3_elem = page1_soup.find(href=re.compile("/page_3/"))
    page3_link = page3_elem.attrs["href"]
    page3_res = requests.get("https://www.jalan.net" + page3_link)
    page3_soup = BeautifulSoup(page3_res.text, "html.parser")
    page3_soup = BeautifulSoup(
        page3_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )
    # 各ページのsoupを格納---------------
    soups = [page1_soup, page2_soup, page3_soup]

    # 観光地の名前----------------
    spot_path = page1_soup.find("p", class_="detailTitle")
    spot = spot_path.contents[0]
    # print("\nSightseeingSpot: ", spot)

    # その観光地の名前、タイトル・スコア・口コミをまとめたリスト----
    new_list = [[spot], [spot], [spot]]

    # 各ページについてスクレイピング
    for page_soup in soups[:-1]:
        # titles: 口コミタイトル----------
        titles = page_soup.find_all("p", class_="reviewCassette__title", limit=10)
        if len(titles) == 0:
            titles = page_soup.find_all("p", class_="item-title", limit=10)
            for title in titles:
                new_list[0].append(title.contents[0].contents[0])
                # print(title.contents[0].contents[0])
        else:
            for title in titles:
                new_list[0].append(title.contents[0])
                # print(title.contents[0])

        # scores: 口コミスコア----------
        scores = page_soup.find_all(class_="reviewPoint", limit=11)
        for score in scores[1:]:
            new_list[1].append(score.contents[0])

        # comments: 口コミ内容-------------
        comments = page_soup.find_all("p", class_="reviewCassette__comment", limit=10)
        if len(comments) == 0:
            comments = page_soup.find_all("div", class_="item-reviewTextInner")
        for comment in comments:
            new_list[2].append(comment.contents[0])

    # new_df: 現在のループの観光地の名前、口コミをまとめたデータフレーム------
    new_df = pd.DataFrame(data=new_list)
    df = df._append(new_df)

    # 観光地が30か所集まったらスクレイピング終了
    if df.shape[0] == 90:
        print("break!")
        break

df = df.reset_index()
del df["index"]
df.to_csv("output.csv", index=False, encoding="utf-8")

print(df)
