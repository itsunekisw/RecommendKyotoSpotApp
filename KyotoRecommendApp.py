import tkinter
from model import recommendSpot


class RecommendApp(tkinter.Frame):
    def __init__(self, root=None):
        super().__init__(root, width=800, height=830, borderwidth=4, relief="groove")
        self.root = root
        self.pack()
        self.results = None

        self.pack_propagate(0)
        self.create_widgets()

    def create_widgets(self):
        # 入力指示文
        self.message = tkinter.Message(self)
        self.message["width"] = 600
        self.message["text"] = (
            "\nInput a description of your ideal travel destination in Japanese.\n"
        )
        self.message.pack()
        # テキストボックス
        self.text_box = tkinter.Entry(self)
        self.text_box["width"] = 50
        self.text_box.pack()
        # 実行ボタン
        submit_btn = tkinter.Button(self)
        submit_btn["text"] = "EXECUTE"
        submit_btn["command"] = self.recommend
        submit_btn.pack()
        # Enterキーを押しても実行できる
        root.bind("<Return>", lambda event: submit_btn.invoke())

        closest_n = 5
        self.result_spots = []
        self.result_titles = []
        self.result_comments = []
        for _ in range(closest_n):
            # 観光地出力
            self.result_spot = tkinter.Message(self)
            self.result_spot["width"] = 600
            self.result_spot.pack()
            self.result_spots.append(self.result_spot)
            # レビュータイトル出力
            self.result_title = tkinter.Message(self)
            self.result_title["width"] = 600
            self.result_title.pack()
            self.result_titles.append(self.result_title)
            # レビューコメント出力
            self.result_comment = tkinter.Message(self)
            self.result_comment["width"] = 600
            self.result_comment.pack()
            self.result_comments.append(self.result_comment)
        # 終了ボタン
        quit_btn = tkinter.Button(self)
        quit_btn["text"] = "QUIT"
        quit_btn["command"] = self.root.destroy
        quit_btn.pack(side="bottom")

    # 実行ボタンが押された時の処理
    def recommend(self):
        text = self.text_box.get()
        closest_n = 5
        self.results, self.data = recommendSpot(text, closest_n)
        i = 0
        for idx, distance in self.results:
            review = self.data.iloc[idx]
            self.result_spots[i]["text"] = "\n" + review["Spot"]
            self.result_titles[i]["text"] = review["reviewTitle"]
            self.result_comments[i]["text"] = review["reviewComment"]
            i += 1
        self.text_box.delete(0, tkinter.END)


root = tkinter.Tk()
root.title("Kyoto Recommend App")
root.geometry("850x850")
app = RecommendApp(root=root)
root.mainloop()
