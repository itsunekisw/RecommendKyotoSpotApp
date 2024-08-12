# pip install selenium：version4系を使用
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
import time

# chromedriver.exeがある場所
driver_path = "chromedriver.exe"

# webdriverの作成
service = Service(executable_path=driver_path)  # executable_pathを指定
driver = webdriver.Chrome(service=service)  # serviceを渡す

driver.get(
    "https://www.jalan.net/kankou/spt_guide000000179653/kuchikomi/page_2/?screenId=OUW2202&reviewRefineCompanion=all&reviewRefineMonth=all&resultSort=pd"
)
# 5秒待つ
time.sleep(5)

# webdriverの終了（ブラウザを閉じる）
driver.quit()
