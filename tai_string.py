import pandas as pd
import re
import syl_trans
from syl_trans import *

# 取得羅馬字
RE_LATIN = re.compile(r'[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]+')
# 取非羅馬字
RE_NON_LATIN = re.compile(r'[^[A-zÀ-ÖØ-öø-įĴ-őŔ-žǍ-ǰǴ-ǵǸ-țȞ-ȟȤ-ȳɃɆ-ɏḀ-ẞƀ-ƓƗ-ƚƝ-ơƤ-ƥƫ-ưƲ-ƶẠ-ỿa̍ám̄\-]')

tone_dict = {'á': ['a', '2'], 'à': ['a', '3'], 'â': ['a', '5'], 'ā': ['a', '7'], 'a̍': ['a', '8'], 'a̋': ['a', '9'],
            'Á': ['A', '2'], 'À': ['A', '3'], 'Â': ['A', '5'], 'Ā': ['A', '7'], 'A̍': ['A', '8'], 'A̋': ['A', '9'],
            'é': ['e', '2'], 'è': ['e', '3'], 'ê': ['e', '5'], 'ē': ['e', '7'], 'e̍': ['e', '8'], 'e̋': ['e', '9'],
            'É': ['E', '2'], 'È': ['E', '3'], 'Ê': ['E', '5'], 'Ē': ['E', '7'], 'E̍': ['E', '8'], 'E̋': ['E', '9'],
            'í': ['i', '2'], 'ì': ['i', '3'], 'î': ['i', '5'], 'ī': ['i', '7'], 'i̍': ['i', '8'], 'ı̍': ['i', '8'], 'i̋': ['i', '9'],
            'Í': ['I', '2'], 'Ì': ['I', '3'], 'Î': ['I', '5'], 'Ī': ['I', '7'], 'I̍': ['I', '8'], 'I̋': ['I', '9'],
            'ó': ['o', '2'], 'ò': ['o', '3'], 'ô': ['o', '5'], 'ō': ['o', '7'], 'o̍': ['o', '8'], 'ő': ['o', '9'],
            'Ó': ['O', '2'], 'Ò': ['O', '3'], 'Ô': ['O', '5'], 'Ō': ['O', '7'], 'O̍': ['O', '8'], 'Ő': ['O', '9'],
            'ú': ['u', '2'], 'ù': ['u', '3'], 'û': ['u', '5'], 'ū': ['u', '7'], 'u̍': ['u', '8'], 'ű': ['u', '9'],
            'Ú': ['U', '2'], 'Ù': ['U', '3'], 'Û': ['U', '5'], 'Ū': ['U', '7'], 'U̍': ['U', '8'], 'Ű': ['U', '9'],
            'ḿ': ['m', '2'], 'm̀': ['m', '3'], 'm̂': ['m', '5'], 'm̄': ['m', '7'], 'm̍': ['m', '8'], 'm̋': ['m', '9'],
            'Ḿ': ['M', '2'], 'M̀': ['M', '3'], 'M̂': ['M', '5'], 'M̄': ['M', '7'], 'M̍': ['M', '8'], 'M̋': ['M', '9'],
            'ń': ['n', '2'], 'ǹ': ['n', '3'], 'n̂': ['n', '5'], 'n̄': ['n', '7'], 'n̍': ['n', '8'], 'n̋': ['n', '9'],
            'Ń': ['N', '2'], 'Ǹ': ['N', '3'], 'N̂': ['N', '5'], 'N̄': ['N', '7'], 'N̍': ['N', '8'], 'N̋': ['N', '9']}
#lines = ["m̄-koh尪姨uì頭到尾lóng teh kap祖靈溝通對話，是一个神聖ê khang-khuè，bē-sái kā伊攪擾，所以無法度請教伊相關ê細節。M̄-koh，阮感受著伊是阿姆祖kap族人中間穿針引線ê人。Tī嘉臘埔，阿姆祖kap尪姨是Makatao族人ê精神寄託。"]
#def mapping_table():
#        # alpha2zh = {}
#
#    for phonetic, kanji in tone_dict.items:    
#        if type(phonetic) is not float and RE_LATIN.match(str(phonetic)):
#            phonetic = str(phonetic).lower()
#        elif type(kanji) is not float and RE_LATIN.match(str(kanji)):
#            phonetic = str(kanji).lower()
#        else:
#            continue
#
#        if RE_NON_LATIN.match(str(kanji)): 
#            lines[phonetic] = str(kanji)
#    return mapping_table


#for match in RE_LATIN.finditer(str(lines)):
#        phonetic = match.group(0).lower()
#        phonetic = syl_trans(phon
# 0etic)
#        print(phonetic)
#        
str = "磕一ti̍oh chhùi-o͘ bīn-thó͘"


sign = ['，', '。']
t_str = []
type = []
seg_label=[]
seg_temp = ""
seg = []
#社每character的label 漢字、拉丁字母、標點符號
for i in range(len(str)):
    if not (u'\u4e00' <= str[i] <= u'\u9fff'):
        if str[i] in sign:
            type.append("S")
        else:
            type.append("L")
    else:
        type.append('H')
type.append('E')
# print(type)        

#str 分成漢字段與非漢字段與標點符號
for i in range(len(str)):
    c_label = type[i]
    f_label = type[i+1]
    seg_temp = seg_temp + str[i]
    if c_label != f_label:
        seg.append(seg_temp)
        seg_temp = ""
        seg_label.append(type[i])
# print(seg_label)
# print(seg)
# 產生漢羅字串
for i in range(len(seg)):
    if (seg_label[i] == 'H') or (seg_label[i] == 'S') :
        # print(seg[i])
        for j in range(len(seg[i])):
            t_str.append(seg[i][j])
            
    elif seg_label[i] == 'L':
        seg_sp = seg[i].split(' ')
        print(seg_sp)
        # mine
        seg_sp=syl_trans(seg[i]) 
        
        for k in range(len(seg_sp)):
            t_str.append(seg_sp[k])
print('' .join(t_str))