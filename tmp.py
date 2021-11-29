from bs4 import BeautifulSoup
import requests
import math

import pandas as pd
import re


RE_LATIN = re.compile(r'[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿm̄]+')
RE_NON_LATIN = re.compile(r'[^[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿm̄]')

def build_mapping_table(xlsx_path):
    df = pd.read_excel(xlsx_path)

    # this dict's key is latin, and the value is non-latin
    
    alpha2zh = {}    
    # rec could be both latin and non-latin
    for phonetic, rec, edu_rec in zip(df['音讀'], df['建議用字'], df['教育部推薦漢字']):
        # phonetic and rec are both latin, but we prefer to use phonetic instead of rec
        if type(phonetic) is str and RE_LATIN.match(phonetic):
            phonetic = phonetic.lower()
        elif type(rec) is str and RE_LATIN.match(rec):
            phonetic = rec.lower()
        else:
            continue

        # rec and edu_rec are both non_latin, and we prefer to use edu_rec
        if type(edu_rec) is str and RE_NON_LATIN.match(str(edu_rec)):  # 使用教育部推薦漢字
            alpha2zh[phonetic] = str(edu_rec)
        elif type(rec) is str and RE_NON_LATIN.match(str(rec)):  # 使用建議用字
            alpha2zh[phonetic] = str(rec)

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
            if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")):
                # append each URL to the list
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
   
    return article.lower()

def do_convert(article, mapping_table):
    shift = 0
    for match in RE_LATIN.finditer(article):
        phonetic = match.group(0).lower()
        start_idx, end_idx = match.span(0)

        if phonetic in mapping_table:
            article = article[0:start_idx-shift] + mapping_table[phonetic] + article[end_idx-shift:]
            shift += end_idx - start_idx - 1

    return article

def main():
    # build mapping table
    alpha2zh = build_mapping_table('table.xlsx')
    
    # execute
    article_list = []
    urls_list = get_all_urls()[10:11]
    for url in urls_list:
        article = get_article(url)
        if article:
            article_list.append(article)

    # translate all article in the article_list
    for article in article_list:
        new_article = do_convert(article, alpha2zh)

        # output each line for demostrate the difference
        for o , n in zip(article.split('\n'), new_article.split('\n')):
            print(o)
            print(n)
            print('')

if __name__=='__main__':
    main()
