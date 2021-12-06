from bs4 import BeautifulSoup
import requests
import math
'''import pymysql'''
import pandas as pd
import re
# import syl_trans
from syl_trans import *


# 取得羅馬字
RE_LATIN = re.compile(r'[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]+')
# 取非羅馬字
RE_NON_LATIN = re.compile(r'[^[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]')

def build_mapping_table():
    df_excel = pd.read_excel("table.xlsx")
    # df_csv = pd.read_csv("standard_dictionary.csv")

    alpha2zh = {}
    for phonetic, rec, edu_rec in zip(df_excel['音讀'], df_excel['建議用字'], df_excel['教育部推薦漢字']):
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


# def get_all_urls():
    '''爬網址'''
    response = requests.get("https://tsbp.tgb.org.tw/") 
    soup = BeautifulSoup(response.text,"html.parser")
    urls = soup.find_all("a")                           

    '''反斜線判斷斜線 \d是指數字 不是字母d 正斜線=網址中的斜線'''
    url_list = []  # create a list
    for url in urls:
        try:
            if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")):  
                # append each URL to the list
                url_list.append(url.get("href"))
        except:
            pass

    return url_list


# def get_article(url):
    '''爬網址的文章''' 
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all("span", style="font-family: inherit; font-size: medium;")

    article = ''
    for temp in content:
        article += temp.getText() + '\n'
    
    return article

'''轉換'''

alpha2zh = build_mapping_table()
alpha2zh = {"hit4-tsun7" : "彼陣", "e5" : "的"}

def do_convert(article):
    shift = 0
    for match in RE_LATIN.finditer(article):
        phonetic = match.group(0).lower()
        phonetic = syl_trans(phonetic)
        print(phonetic + '\n')
        start_idx, end_idx = match.span(0)
        if phonetic in alpha2zh:                                                                               
            article = article[0:start_idx-shift] + alpha2zh[phonetic] + article[end_idx-shift:] 
            shift += end_idx - start_idx - 1

    return article
'''換database search去select line78 if phonetic in alpha2zh: '''
'''執行'''
lines = ["我是台大醫科ê學生，讀冊hit-tsūn對做醫生並無特別"]
# file = open('test.txt', encoding="big5") as f 
# with open('test.txt', encoding="utf-8") as f:
    # lines = f.readlines()
'''
count = 0
for line in lines:
    count += 1
    print(f'line {count}: {line}')    '''
# urls_list = get_all_urls()[13:14]  # 取得所有 URL

# for url in urls_list:
    # article = get_article(url)
    # if article:
        # article_list.append(article)
out = open('outfile.txt', 'w', encoding= 'utf-8')
for article in lines:
    new_article = do_convert(article)

    '''印出原版及轉換後的版本做比較'''

    for o , n in zip(article.split('\n'), new_article.split('\n')):
        out.writelines(o + '\n')
        out.writelines(n + '\n')
        out.writelines(''+ '\n')

        print(o)
        print(n)
        print('')
