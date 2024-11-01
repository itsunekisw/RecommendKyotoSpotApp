import tkinter

from model import SentenceLukeJapanese


class RecommendApp(tkinter.Frame):

    def __init__(self, root=None):
        super().__init__(root, width=420, height=320, borderwidth=4, relief="groove")
        self.root = root
        self.pack()

        self.MODEL_NAME = "sonoisa/sentence-luke-japanese-base-lite"
        self.model = SentenceLukeJapanese(self.MODEL_NAME)

        csv_file_path = "output.csv"
        target_column_name = "reviewComment"
        self.model.read_csv(csv_file_path, target_column_name)

        self.pack_propagate(0)
        self.create_widgets()

    def create_widgets(self):
        self.message = tkinter.Message(self)
        self.message["width"] = 600
        self.message["text"] = (
            "\nInput a description of your ideal travel destination in Japanese.\n"
        )
        self.message.pack()

        self.text_box = tkinter.Entry(self)
        self.text_box["width"] = 50
        self.text_box.pack()

        submit_btn = tkinter.Button(self)
        submit_btn["text"] = "Recommend"
        submit_btn["command"] = self.recommend
        submit_btn.pack()

        self.message = tkinter.Message(self)
        self.message["width"] = 600
        self.message.pack()

        self.result_message = tkinter.Message(self)
        self.result_message["width"] = 600
        self.result_message.pack()

        quit_btn = tkinter.Button(self)
        quit_btn["text"] = "QUIT"
        quit_btn["command"] = self.root.destroy
        quit_btn.pack(side="bottom")

    def recommend(self):
        text = self.text_box.get()
        self.message["text"] = "\nWait A Moment...  Encoding sentences..."
        results = self.model.recommend(text)
        self.results = results
        self.result_message["text"] = self.model.data.iloc[results[1], 0]
        closest_n = 5
        print("======================")
        print("Your ideal travel distination:", text)
        print("\nオススメの京都の旅行先は:")
        for idx, distance in results[1 : closest_n + 1]:
            print("旅行先\t\t", self.model.data.iloc[idx, 0])
            print("タイトル\t", self.model.data.iloc[idx, 1])
            print("評価\t\t", self.model.data.iloc[idx, 2])
            print("口コミ\t\t", self.model.sentences[idx].strip())
            print("類似度\t\t", 1 - distance, "\n")


root = tkinter.Tk()
root.title("Kyoto Recommend App")
root.geometry("400x300")
app = RecommendApp(root=root)
root.mainloop()
