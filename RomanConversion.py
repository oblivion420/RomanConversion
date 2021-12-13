from bs4 import BeautifulSoup
import requests
import math

import pandas as pd
import re


# 取得羅馬字
RE_LATIN = re.compile(r'[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄]+')
# 取非羅馬字
RE_NON_LATIN = re.compile(r'[^[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄]')

def build_mapping_table():
    df = pd.read_excel("table.xlsx")

    alpha2zh = {}
    for phonetic, rec, edu_rec in zip(df['音讀'], df['建議用字'], df['教育部推薦漢字']):
        # 空值為 float('nan')
        if type(phonetic) is not float and RE_LATIN.match(str(phonetic)):
            phonetic = str(phonetic).lower()
        elif type(rec) is not float and RE_LATIN.match(str(rec)):
            phonetic = str(rec).lower()
        else:
            continue

        if RE_NON_LATIN.match(str(rec)):  # 使用建議用字
            alpha2zh[phonetic] = str(rec)
        elif RE_NON_LATIN.match(str(edu_rec)):  # 使用教育部推薦漢字
            alpha2zh[phonetic] = str(edu_rec)

    return alpha2zh


def get_all_urls():
    '''爬網址'''
    response = requests.get("https://tsbp.tgb.org.tw/") 
    soup = BeautifulSoup(response.text,"html.parser")
    urls = soup.find_all("a")                           

    '''反斜線判斷斜線 \d是指數字 不是字母d 正斜線=網址中的斜線'''
    url_list = []  # create a list
    for url in urls:
        try:
            # if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")):  
            if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")) or re.search('https:\/\/tsbp.tgb.org.tw\/search\/label\/\S+', url.get("href")) or re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+\.html', url.get("href")):  
            # if re.search ('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")) :
                    #  url_list.append(url.get("href"))
            # elif re.search('https:\/\/tsbp.tgb.org.tw\/search\/label\/\S+', url.get("href")):
                     url_list.append(url.get("href"))
            # elif re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+\.html', url.get("href")):

                # append each URL to the list
                    # url_list.append(url.get("href"))
        except:
            pass

    return url_list 


def get_article(url):
    '''爬網址的文章''' 
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all(text=True)
    # content.append(soup.find_all("span", style="font-family: arial  , helvetica , sans-serif;" ))
    # content.append(soup.find_all("span", face=" arial  , helvetica , sans-serif ; style = font-size: xx-small;"))
    # content.append(soup.find_all("span", style="font-family: arial"))
    # content_list = []
    # content_list.append(soup.find_all("span", style="font-family: inherit; font-size: medium;" ))
    # content_list.append(soup.find_all("span", style="font-family: arial  , helvetica , sans-serif;" ))
    # content_list.append(soup.find_all("span", face=" arial  , helvetica , sans-serif ; style = font-size: xx-small;" ))
    # content_list.append(soup.find_all("span", style="font-family: arial" ))


    article = ''
    for temp in content:
        article += temp.getText() + '\n'
    # for content in content_list:
        # for temp in content:    
            # article += temp.getText() + '\n'
    
    return article

'''轉換'''
'''alpha2zh = build_mapping_table()
def do_convert(article):
    shift = 0
    for match in RE_LATIN.finditer(article):
        phonetic = match.group(0).lower()
        start_idx, end_idx = match.span(0)

        if phonetic in alpha2zh:        
            article = article[0:start_idx-shift] + alpha2zh[phonetic] + article[end_idx-shift:]
            shift += end_idx - start_idx - 1

    return article'''

'''執行'''
article_list = []
# file_list = []
urls_list = get_all_urls()[0:500]  # 取得所有 URL
for url in urls_list:
    article = get_article(url)
    # with open("file_list.txt","w",encoding='utf-8') as f:
        # f.write(article)

    # file_list.append.split("")
    # f.close()
    if article:
        article_list.append(article)

text_file = open("Original_All_Text.txt", "w", encoding= 'utf-8')

for article in article_list:
    text_file.write(article)
    # new_article = do_convert(article)


    '''印出原版及轉換後的版本做比較'''
    # for o , n in zip(article.split('\n'), new_article.split('\n')):
        # print(o)
        # print(n)
        # print('')
text_file.close()