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

# ------------------------------------------------------------
# # 最上位層からのルート指定
# print(soup.html.head.title)
# # html.headの省略
# print(soup.title)
# --------------------------------------
# # クラスで指定した場合、当てはまる最初の要素が取得される
# print(soup.body.p)
# find_all(): 全ての要素を取得
# for p in soup.body.find_all("p"):
#     print(p, end="\n\n")
# ---------------------------------------
# # string: 要素に含まれるテキストの抽出
# print(soup.title.string)
# # get_text(): 全てのテキスト
# print(soup.get_text())
# ---------------------------------------
# # ["class"] or get(): 要素に含まれる属性の値を表示
# print(soup.body.p["class"])
# print(soup.body.p.get("class"))
# ----------------------------------------
# # body配下の2つめのp要素に含まれるclass属性を表示
# print(soup.body.p.next_sibling.next_sibling["class"])
# # prettify(): htmlを綺麗にフォーマットした状態で表示
print(soup.prettify())
# ---------------------------------------
# # contentsとchildrenの違いはよくわからない
# # contents: 子要素の取得（indexを指定して各要素にアクセス可能）
# print("contents")
# for i, child in enumerate(soup.body.contents):
#     print(i, child, end="\n\n")
# # children: 子要素の取得（各要素に順序通りにアクセス）
# print("children")
# for i, child in enumerate(soup.body.children):
#     print(i, child, end="\n\n")
# # descendants: 子孫要素の取得（階層の深いところまで全て表示、リストの要素数が多い）
# print("descendants")
# for i, child in enumerate(soup.body.descendants):
#     print(i, child, end="\n\n")
# -----------------------------------------------
# # parent: 親要素の取得
# print("parent")
# print(soup.title.parent)
# # parents: 先祖要素の取得（先祖の属性名を表示）
# print("parents")
# for i, parent in enumerate(soup.a.parents):
#     print(i, parent.name)
# ------------------------------------------------
# # next_sibling: 一つ目の要素基準にして隣のものを指定
# print(f"p:\n{soup.body.p}\n")
# print(f"p.next_sibling:\n{soup.body.p.next_sibling}\n")
# print(f"p.next_sibling.next_sibling:\n{soup.body.p.next_sibling.next_sibling}\n")
# for i, sibling in enumerate(soup.body.p.next_siblings):
#     print(i, sibling if sibling != "\n" else "", end="\n\n")
# -------------------------------------------------
# previous_sibling: 一つ前の兄弟要素を取得
print(soup.body.previous_sibling.previous_sibling)
# pタグのclassが一致するものを抽出
for i, sibling in enumerate(soup.body.find("p", class_="end").previous_siblings):
    print(i, sibling["class"] if sibling != "\n" else "", end="\n\n")
