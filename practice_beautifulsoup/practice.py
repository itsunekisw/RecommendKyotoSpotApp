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
print(pickup_links[29])
pickup_link = pickup_links[29]
info = soup.find("div", class_="item-info")

df = pd.DataFrame()
df_list = {}
spots = []
# 一覧のリンクを順に処理


# requests.get(): Pickupページへ遷移しページの情報を取得
pickup_res = requests.get("https:" + pickup_links[29])
pickup_soup = BeautifulSoup(pickup_res.text, "html.parser")
pickup_soup = BeautifulSoup(
    pickup_res.content.decode("Shift-JIS", "ignore"), "html.parser"
)

# ニュースページへの情報を取得-----------------
comments = pickup_soup.find_all("p", class_="reviewCassette__comment")
if len(comments) == 0:
    comments = pickup_soup.find_all("div", class_="item-reviewTextInner")
# print(comments)---------------------------

# ニュースのテキスト情報を取得し表示
for i, comment in enumerate(comments):
    print(i, comment.contents[0] if comment is not None else "")
    if i > 20:
        break
