import requests
from bs4 import BeautifulSoup

# url = "https://www.jalan.net/kankou/260000/"


# --------selectorで取得(yomiuri.co.jp)--------
# url = "https://www.yomiuri.co.jp"
# res = requests.get(url)
# print(res.text)

# soup = BeautifulSoup(res.text, "html.parser")

# for i in range(2, 12):

#     # cssセレクタ
#     selector = f"body > div.uni-home > div > main > div.home-l-main__primary > section.home-headline > div.home-headline__contents > div > div:nth-child({str(i)}) > h3 > a"

#     # 指定したセレクタの箇所の情報を取得する
#     elems = soup.select(selector)
#     print(i, elems[0].contents[0], end=" ")
#     print(elems[0].attrs["href"])

# ------find_all()で取得(yahoo.co.jp)----------
url = "https://www.yahoo.co.jp/"
res = requests.get(url)

# parser: 解析器といい、解析に利用
soup = BeautifulSoup(res.text, "html.parser")

# # find_all: aタグの部分を全て拾ってくる
# elems = soup.find_all("a")
# print(elems)

# ----------re.compile()で取得-------------
import re

# re.compile: href属性の中で引数を含むもののみ抽出
elems = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup"))
pickup_links = [elem.attrs["href"] for elem in elems]
print(pickup_links)

# 一覧のリンクを順に処理
for elem, pickup_link in zip(elems, pickup_links):
    print(
        f"\n\n\tcontent: { elem.contents[0].contents[0].contents[0].contents[0].contents[0] }"
    )
    # print("href:\t\t\t", elem.attrs["href"])
    # print("data-ual-gotocontent:\t", elem.attrs["data-ual-gotocontent"])

    # requests.get(): Pickupページへ遷移しページの情報を取得
    pickup_res = requests.get(pickup_link)
    pickup_soup = BeautifulSoup(pickup_res.text, "html.parser")

    # ニュースページへのリンクを取得
    pickup_elem = pickup_soup.find("div", class_="sc-gdv5m1-8")
    news_link = pickup_elem.contents[0].attrs["href"]

    # ニュースページの情報を取得
    news_res = requests.get(news_link)
    news_soup = BeautifulSoup(news_res.text, "html.parser")

    # タイトルとURLを表示
    print(news_soup.title.text, end="\n\n")
    # print(news_link)

    # ニュースのテキスト情報を取得し表示
    detail_text = news_soup.find(class_=re.compile("highLightSearchTarget"))
    print(detail_text.text if hasattr(detail_text, "text") else "")
