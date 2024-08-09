from bs4 import BeautifulSoup

html = """
<html>
    <head>
        <title>清水義孝の著書</title>
    </head>
    <body>
        <p class="title">
            <b>清水義孝の最新の著書には、次の本があります。</b>
        </p>
        <p class="recent books">
            <a class="book" href="https://www.amazon.co.jp/dp/B07TN4D3HG" id="link1">
                Python3によるビジネスに役立つデータ分析入門
            </a>
            <a class="book" href="http://www.amazon.co.jp/dp/B07SRLRS4M" id="link2">
                よくわかるPython3入門2.NumPy・Matplotlib編
            </a>
            <a class="book" href="http://www.amazon.co.jp/dp/B07T9SZ96B" id="link3">
                よくわかるPython3入門4.Pandasでデータ分析編
            </a>
        </p>
        <p class="end">
            <b>そして、これらの本は好評発売中です。</b>
        </p>
    </body>
</html>
"""
soup = BeautifulSoup(html, "html.parser")
print(soup.prettify())
# ------------------------------------------------
# print("title:", soup.find_all("title"))
# for i, elem in enumerate(soup.find_all(["a", "b"])):
#     print(i, elem)
# -----------------------------------------------
import re

# # ^b: 文字列の先頭からパターンに一致するかを判定
# for tag in soup.find_all(re.compile("^b")):
#     print(tag.name)
# print("\n")
# # find_all(True): name引数にTrueを返すと、Tagオブジェクトのすべての子孫要素を取得
# for tag in soup.body.find_all(True):
#     print(tag.name)


# -------------------------------------------------
# class属性があり、id属性はない場合にTrueを返す関数
def has_class_but_no_id(tag):
    return tag.has_attr("class") and not tag.has_attr("id")


for i, elem in enumerate(soup.find_all(has_class_but_no_id)):
    print(i, elem)
# -------------------------------------------------
# href属性に"http://"を含むもの取得
print(soup.find_all(href=re.compile("http://")))
# id属性に値が入っているタグ取得
print(soup.find_all(id=True))
