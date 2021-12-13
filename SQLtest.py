# import pymysql
from bs4 import BeautifulSoup
import re
import requests
    
# conn = pymysql.connect("140.109.23.160", "sebastian95", "kingdom0214", "Taigi", port=3307)
# cursor = conn.cursor() 
    #  '''可放到最上面'''
# sql = f"SELECT 漢字 FROM standard_dictionary WHERE `TL-標準` = '{Tailo}' "
# cursor.execute(sql)
# results = cursor.fetchall()

# '''我是台大醫科ê學生，讀冊hit-tsūn對做醫生並無特別'''
def get_all_urls():
    '''爬網址'''
    response = requests.get("https://tsbp.tgb.org.tw/") 
    soup = BeautifulSoup(response.text,"html.parser")
    urls = soup.find_all("a")                           

    '''反斜線判斷斜線 \d是指數字 不是字母d 正斜線=網址中的斜線'''
    url_list = []  # create a list
    for url in urls:
        try:
   
            if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")) or re.search('https:\/\/tsbp.tgb.org.tw\/search\/label\/\S+', url.get("href")) or re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+\.html', url.get("href")):  
                url_list.append(url.get("href"))
        except:
            pass

    return url_list 

def get_article(url):
    '''爬網址的文章''' 
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all("span", style="font-family: inherit; font-size: medium;")

    article = ''
    for temp in content:
        article += temp.getText() + '\n'
    
    return article




article_list = []
urls_list = get_all_urls()[0:500]  # 取得所有 URL
for url in urls_list:
    article = get_article(url)


text_file = open("OriginalArticles_inherit.txt", "w", encoding= 'utf-8')

for article in article_list:
    text_file.write(article)

text_file.close()