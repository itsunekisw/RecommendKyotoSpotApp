import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime
import time


def create_csv(num_spot=30):
    # じゃらんのURLにアクセス
    url = "https://www.jalan.net/kankou/260000/"
    res = requests.get(url)
    time.sleep(1)

    # これしないと文字化け
    soup = BeautifulSoup(res.content.decode("Shift-JIS", "ignore"), "html.parser")

    # レビューリンクを取得
    review_links = soup.find_all(href=re.compile("/kuchikomi"))
    pickup_links = [link.attrs["href"] for link in review_links]

    df = pd.DataFrame()
    count = 0

    # 一覧のリンクを順に処理-
    for elem, pickup_link in zip(review_links, pickup_links):
        # 口コミ数20件以上なかったらスキップ
        try:
            if int(re.findall(r"\d+", elem.contents[0])[-1]) <= 20:
                continue
        except:
            continue

        # レビュー2ページ分のsoupオブジェクトを作成、格納
        soups = create_soups(pickup_link)

        # 観光地の名前を取得
        spot_path = soups[0].find("p", class_="detailTitle")
        spot = spot_path.contents[0]
        print(f"\nNo.{count + 1}: Scraping from {spot}...")

        # その観光地の名前、タイトル・スコア・口コミをまとめたリスト
        review_list = [[spot] * 20]
        titles = []
        scores = []
        comments = []
        for page_soup in soups:
            titles = scraping_target("title", page_soup, output_list=titles)
            scores = scraping_target("score", page_soup, output_list=scores)
            comments = scraping_target("comments", page_soup, output_list=comments)
        review_list.extend([titles, scores, comments])

        # new_df: 現在のレビューをまとめたデータフレーム
        new_df = pd.DataFrame(data=review_list).T
        df = df._append(new_df)

        # 観光地が30か所集まったらスクレイピング終了
        count += 1
        if count == num_spot:
            break

    df = df.reset_index()
    del df["index"]
    df.columns = ["Spot", "reviewTitle", "reviewScore", "reviewComment"]
    current_data = datetime.datetime.now()
    data_str = current_data.strftime("%Y%m%d")
    df.to_csv(f"review_data/output{data_str}.csv", index=False, encoding="utf-8")


def scraping_target(target, page_soup, output_list):
    if target == "title":
        titles = page_soup.find_all("p", class_="reviewCassette__title", limit=10)
        if len(titles) == 0:
            titles = page_soup.find_all("p", class_="item-title", limit=10)
            for title in titles:
                output_list.append(title.contents[0].contents[0])
        else:
            for title in titles:
                output_list.append(title.contents[0])
        return output_list

    elif target == "score":
        scores = page_soup.find_all(class_="reviewPoint", limit=11)
        for score in scores[1:]:
            output_list.append(score.contents[0])
        return output_list

    elif target == "comments":
        comments = page_soup.find_all("p", class_="reviewCassette__comment", limit=10)
        if len(comments) == 0:
            comments = page_soup.find_all("div", class_="item-reviewTextInner")
        for comment in comments:
            try:
                text = comment.contents[0].strip()
            except:
                text = comment.contents[0].contents[0].strip()
            output_list.append(text)
        return output_list


def create_soups(pickup_link):
    # requests.get(): ページ1のsoupオブジェクト作成
    page1_res = requests.get("https:" + pickup_link)
    time.sleep(1)
    page1_soup = BeautifulSoup(
        page1_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )

    # ページ2のsoupオブジェクト作成
    page2_elem = page1_soup.find(href=re.compile("/page_2/"))
    page2_link = page2_elem.attrs["href"]
    page2_res = requests.get(page2_link)
    time.sleep(1)
    page2_soup = BeautifulSoup(
        page2_res.content.decode("Shift-JIS", "ignore"), "html.parser"
    )
    return [page1_soup, page2_soup]


if __name__ == "__main__":
    create_csv()
