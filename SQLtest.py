from bs4 import BeautifulSoup
import requests
import pymysql
import pandas as pd
import re
from urllib.parse import quote,unquote
import syl_trans
from syl_trans import *
from tai_string import PojNumTrans

# conn = pymysql.connect(host="140.109.23.160", user="sebastian95", passwd="kingdom0214", db="Taigi", port=3307)
# cursor = conn.cursor() 
    #  '''可放到最上面'''

# 取得羅馬字
RE_LATIN = re.compile(r'[A-z0-9À-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]+')
# 取非羅馬字
RE_NON_LATIN = re.compile(r'[^[A-z0-9À-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]')

# tone_dict = {'á': ['a', '2'], 'à': ['a', '3'], 'â': ['a', '5'], 'ā': ['a', '7'], 'a̍': ['a', '8'], 'a̋': ['a', '9'],
#             'Á': ['A', '2'], 'À': ['A', '3'], 'Â': ['A', '5'], 'Ā': ['A', '7'], 'A̍': ['A', '8'], 'A̋': ['A', '9'],
#             'é': ['e', '2'], 'è': ['e', '3'], 'ê': ['e', '5'], 'ē': ['e', '7'], 'e̍': ['e', '8'], 'e̋': ['e', '9'],
#             'É': ['E', '2'], 'È': ['E', '3'], 'Ê': ['E', '5'], 'Ē': ['E', '7'], 'E̍': ['E', '8'], 'E̋': ['E', '9'],
#             'í': ['i', '2'], 'ì': ['i', '3'], 'î': ['i', '5'], 'ī': ['i', '7'], 'i̍': ['i', '8'], 'ı̍': ['i', '8'], 'i̋': ['i', '9'],
#             'Í': ['I', '2'], 'Ì': ['I', '3'], 'Î': ['I', '5'], 'Ī': ['I', '7'], 'I̍': ['I', '8'], 'I̋': ['I', '9'],
#             'ó': ['o', '2'], 'ò': ['o', '3'], 'ô': ['o', '5'], 'ō': ['o', '7'], 'o̍': ['o', '8'], 'ő': ['o', '9'],
#             'Ó': ['O', '2'], 'Ò': ['O', '3'], 'Ô': ['O', '5'], 'Ō': ['O', '7'], 'O̍': ['O', '8'], 'Ő': ['O', '9'],
#             'ú': ['u', '2'], 'ù': ['u', '3'], 'û': ['u', '5'], 'ū': ['u', '7'], 'u̍': ['u', '8'], 'ű': ['u', '9'],
#             'Ú': ['U', '2'], 'Ù': ['U', '3'], 'Û': ['U', '5'], 'Ū': ['U', '7'], 'U̍': ['U', '8'], 'Ű': ['U', '9'],
#             'ḿ': ['m', '2'], 'm̀': ['m', '3'], 'm̂': ['m', '5'], 'm̄': ['m', '7'], 'm̍': ['m', '8'], 'm̋': ['m', '9'],
#             'Ḿ': ['M', '2'], 'M̀': ['M', '3'], 'M̂': ['M', '5'], 'M̄': ['M', '7'], 'M̍': ['M', '8'], 'M̋': ['M', '9'],
#             'ń': ['n', '2'], 'ǹ': ['n', '3'], 'n̂': ['n', '5'], 'n̄': ['n', '7'], 'n̍': ['n', '8'], 'n̋': ['n', '9'],
#             'Ń': ['N', '2'], 'Ǹ': ['N', '3'], 'N̂': ['N', '5'], 'N̄': ['N', '7'], 'N̍': ['N', '8'], 'N̋': ['N', '9']}

def build_mapping_table():
    # df_csv = pd.read_csv("standard_dictionary.csv")
    df = pd.read_excel("table.xlsx")

    # sql = f"SELECT 漢字 FROM standard_dictionary WHERE `TL-標準` = '{Tailo}' "
    # sql = "SELECT `TL-標準`,`漢字`  FROM standard_dictionary;"
    # cursor.execute(sql)
    # results = cursor.fetchall()
    alpha2zh = {}
    # lst=[alpha2zh.get()]
    for phonetic, rec, edu_rec in zip(df['音讀'], df['建議用字'], df['教育部推薦漢字']):
        # 空值為 float('nan')
        if type(phonetic) is not float and RE_LATIN.match(str(phonetic)):
            phonetic = PojNumTrans(str(phonetic)).lower()
        elif type(rec) is not float and RE_LATIN.match(str(rec)):
            phonetic = PojNumTrans(str(rec).lower())
        else:
            continue

        if RE_NON_LATIN.match(str(rec)):  # 使用建議用字
            alpha2zh[PojNumTrans(phonetic)] = str(rec)
        elif RE_NON_LATIN.match(str(edu_rec)):  # 使用教育部推薦漢字
            alpha2zh[PojNumTrans(phonetic)] = str(edu_rec)
        # 空值為 float('nan')
    # for phonetic, kanji in results: 
    # for phonetic, kanji in zip(df_csv['TL-標準'], df_csv['漢字']):    
        # if type(phonetic) is not float and RE_LATIN.match(str(phonetic)):
            # phonetic = str(phonetic).lower()
        # elif type(kanji) is not float and RE_LATIN.match(str(kanji)):
            # phonetic = str(kanji).lower()
        # else:
            # continue

        # if RE_NON_LATIN.match(str(kanji)):  # 用漢字欄
            # alpha2zh[phonetic] = str(kanji)
            # alpha2zh[phonetic].append(str(kanji))
            # alpha2zh[phonetic].append(lst)

            # [幹 ,淦 ,旰 ,ㄍㄢˋ]
        # elif RE_NON_LATIN.match(str(kanji)):  # 使用教育部推薦漢字
            # alpha2zh[phonetic] = str(kanji)

    return alpha2zh


    # Max to str (article)
# def get_sub_urls(url_):

#     response = requests.get(url_)
#     soup = BeautifulSoup(response.text,"html.parser")
#     urls = soup.find_all("h3", class_='post-title entry-title')

    
#     url_list = {}
#     for url in urls:
#         try:
#             url_list[(url.a.get("href"))]=0
#         except:
#             pass
#     return url_list

# def get_all_urls(main_html):
#     '''爬網址'''
#     response = requests.get(main_html) 
#     soup = BeautifulSoup(response.text,"html.parser")
#     urls = soup.find_all("a", dir='ltr')
#     # '''反斜線判斷斜線 \d是指數字 不是字母d 正斜線=網址中的斜線'''
#     url_list = []  # create a list
#     all_url_list = {}
#     for url in urls:
#         url = (url.get("href"))
#         url = unquote(url, "utf-8")
#         url_list.append(url)
#         all_url_list.update(get_sub_urls(url))

#     return [url_list, (all_url_list.keys())]

# def seach_url():
#     html = "https://tsbp.tgb.org.tw/"
#     [url_list, all_url_list] = get_all_urls(main_html)  # 取得所有 URL
#     with open("tsbp_url.txt", "w") as url_f:
#         for url in all_url_list:
#             url = unquote(url, "utf-8")
#             url_f.write(url+"\n")
           

# def get_article(url):
#     print(url)

#     '''爬網址的文章''' 
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text,"html.parser")
#     content = soup.find_all("div", style="text-align: justify;",)
#     content += soup.find_all("div", class_='post-body entry-content')
#     content += soup.find_all("span", style="font-family: inherit;")

#     title_ = soup.title.string.strip()

#     article = title_+'\n'
#     for temp in content:
#         article += (temp.getText().strip()) + '\n'
#     return str(article)



'''轉換'''

alpha2zh = build_mapping_table()

def do_convert(article):
    converted_list = []
    last_e_idx = 0
    for match in RE_LATIN.finditer(article):
        phonetic = match.group(0).lower()
        start_idx, end_idx = match.span(0)
        # kan2 -> [幹]  one element
        # if phonetic in alpha2zh and len(alpha2zh[phonetic])==1:
        if PojNumTrans(phonetic) in alpha2zh:
            print(phonetic,"\n")
            converted_list.append(article[last_e_idx: start_idx])
            converted_list.append(alpha2zh[PojNumTrans(phonetic)])
            last_e_idx = end_idx

    converted_list.append(article[last_e_idx:])
    return ''.join(converted_list)
    


# lines = ["bē記得我小學ê時tsūn看--ê是佗一个版本ê《小王子》--ah，m̄-koh每一个版本ê封面lóng有寫hit句：「真正重要ê mi̍h件是用目睭看bē著--ê。"]
lines = ["m7-koh4尪姨ui3頭到尾long2 teh4 敆祖靈溝通對話，是一个神聖的 khang1-khue3，be7-sai2 共伊攪擾，所以無法度請教伊相關的細節。M7-koh4，阮感受著伊是阿姆祖敆族人中間穿針引線的人。ti7嘉臘埔，阿姆祖敆尪姨是Makatao1族人的精神寄託。"]
# lines = ["Hiann5-hue2 si7 kuann5-thinn1--lang5 siong7 un1-luan2 e5 tai7-tsi3 . Hue2 tiam2 toh8 liau2-au7 , ka7 tua7-khoo1 tsha5 lok4 ti7 hue2-loo5 lai7-te2 , hoo7 un5-un5-a2 sio1 , m7-koh4 ai3 tsim1-tsiok4 i5-tshi5 tsit4 pha1 hue2 mai3"]
# str = "bē記得我小學ê時tsūn看--ê是佗一个版本ê《小王子》--ah，m̄-koh每一个版本ê封面lóng有寫hit句：「真正重要ê mi̍h件是用目睭看bē著--ê。」"
# new_article = PojNumTrans(str)
# print(new_article)

# urls_list = get_all_urls()[13:14]  # 取得所有 URL
# for url in urls_list:
    # article = get_article(url)
    # if article:
        # article_list.append(article)
        # testing string below
for article in lines:
    # new_article = do_convert(PojNumTrans(article))
    # new_article = PojNumTrans(article)
    new_article = do_convert(article)
    
#     '''印出原版及轉換後的版本做比較'''

    for o , n in zip(article.split('\n'), new_article.split('\n')):

        print(o)
        print("\n")
        print(n)
        print('')

# max TXT FILE
# c= 0
# with open("tsbp_url.txt", "r") as r_f:
#     for line in r_f:
#         c+=1
#         line=(line.strip().split()[0])
#         article = get_article(line)
#         new_article = PojNumTrans(article)
#         # new_article = (article)

#         with open("TransToNum/"+str(c)+".txt", "w", encoding='utf-8') as txt_f:
#             txt_f.write(str(new_article))