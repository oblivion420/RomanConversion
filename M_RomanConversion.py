from bs4 import BeautifulSoup
import requests
import math
from urllib.parse import quote,unquote

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

def get_sub_urls(url_):

    response = requests.get(url_)
    soup = BeautifulSoup(response.text,"html.parser")
    urls = soup.find_all("h3", class_='post-title entry-title')

    
    url_list = {}
    for url in urls:
        try:
            url_list[(url.a.get("href"))]=0
        except:
            pass
    return url_list

def get_all_urls(main_html):
    '''爬網址'''
    response = requests.get(main_html) 
    soup = BeautifulSoup(response.text,"html.parser")
    urls = soup.find_all("a", dir='ltr')
    # '''反斜線判斷斜線 \d是指數字 不是字母d 正斜線=網址中的斜線'''
    url_list = []  # create a list
    all_url_list = {}
    for url in urls:
        url = (url.get("href"))
        url = unquote(url, "utf-8")
        url_list.append(url)
        all_url_list.update(get_sub_urls(url))

    return [url_list, (all_url_list.keys())]




def seach_url():
    html = "https://tsbp.tgb.org.tw/"
    [url_list, all_url_list] = get_all_urls(main_html)  # 取得所有 URL
    with open("tsbp_url.txt", "w") as url_f:
        for url in all_url_list:
            url = unquote(url, "utf-8")
            url_f.write(url+"\n")
           

def get_article(url):
    print(url)

    '''爬網址的文章''' 
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all("div", style="text-align: justify;",)
    content += soup.find_all("div", class_='post-body entry-content')
    content += soup.find_all("span", style="font-family: inherit;")

    title_ = soup.title.string.strip()

    article = title_+'\n'
    for temp in content:
        article += (temp.getText().strip()) + '\n'
    return str(article)
        
    
    

'''轉換'''
alpha2zh = build_mapping_table()
def do_convert(article):
    shift = 0
    for match in RE_LATIN.finditer(article):
        phonetic = match.group(0).lower()
        start_idx, end_idx = match.span(0)

        if phonetic in alpha2zh:        
            article = article[0:start_idx-shift] + alpha2zh[phonetic] + article[end_idx-shift:]
            shift += end_idx - start_idx - 1

    return article

'''執行'''
'''
# seach_url()
c= 0
with open("tsbp_url.txt", "r") as r_f:
    for line in r_f:
        c+=1
        line=(line.strip().split()[0])
        
        article = get_article(line)
        with open("output/"+str(c)+".txt", "w", encoding='utf-8') as txt_f:
            txt_f.write(str(article))
        
'''
# seach_url()
c= 0
with open("tsbp_url.txt", "r") as r_f:
    for line in r_f:
        c+=1
        line=(line.strip().split()[0])
        article = get_article(line)
        new_article = do_convert(article)
        with open("ConversionOutput/"+str(c)+".txt", "w", encoding='utf-8') as txt_f:
            txt_f.write(str(new_article))
    
# if article:
  # article_list.append(article)

# text_file = open("OriginalArticles.txt", "w", encoding= 'utf-8')

# for article in article_list:
#     text_file.write(article)
#     new_article = do_convert(article)


#     '''印出原版及轉換後的版本做比較'''
#     for o , n in zip(article.split('\n'), new_article.split('\n')):
#         print(o)
#         print(n)
#         print('')
# text_file.close()