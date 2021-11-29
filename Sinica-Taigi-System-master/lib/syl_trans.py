import os
import re
import argparse

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

o_repeat_tone_dict = {'o͘': ['oo', '1'], 'ó͘': ['oo', '2'], 'ò͘': ['oo', '3'], 'ô͘': ['oo', '5'], 'ō͘': ['oo', '7'], 'o̍͘': ['oo', '8'],
                    'O͘': ['Oo', '1'], 'Ó͘': ['Oo', '2'], 'Ò͘': ['Oo', '3'], 'Ô͘': ['Oo', '5'], 'Ō͘': ['Oo', '7'], 'O̍͘': ['Oo', '8']}

code2tone_dict = {'&aacute;': 'á', '&agrave;': 'à', '&acirc;': 'â',
                '&Aacute;': 'Á', '&Agrave;': 'À', '&Acirc;': 'Â',
                '&eacute;': 'é', '&egrave;': 'è', '&ecirc;': 'ê',
                '&Eacute;': 'É', '&Egrave;': 'È', '&Ecirc;': 'Ê',
                '&iacute;': 'í', '&igrave;': 'ì', '&icirc;': 'î',
                '&Iacute;': 'Í', '&Igrave;': 'Ì', '&Icirc;': 'Î',
                '&oacute;': 'ó', '&ograve;': 'ò', '&ocirc;': 'ô',
                #'&oacute;': 'ó͘', '&ograve;': 'ò͘', '&ocirc;': 'ô͘',
                '&Oacute;': 'Ó', '&Ograve;': 'Ò', '&Ocirc;': 'Ô',
                '&uacute;': 'ú', '&ugrave;': 'ù', '&ucirc;': 'û',
                '&Uacute;': 'Ú', '&Ugrave;': 'Ù', '&Ucirc;': 'Û',
                '&macute;': 'ḿ', '&mgrave;': 'm̀', '&mcirc;': 'm̂',
                '&Macute;': 'Ḿ', '&Mgrave;': 'M̀', '&Mcirc;': 'M̂',
                '&nacute;': 'ń', '&ngrave;': 'ǹ', '&ncirc;': 'n̂',
                '&Nacute;': 'Ń', '&Ngrave;': 'Ǹ', '&Ncirc;': 'N̂'}

poj2tailo_dict = {'ch': 'ts', 'Ch': 'Ts',
                'chh': 'tsh', 'Chh': 'Tsh',
                'oe': 'ue', 'Oe': 'Ue',
                'oa': 'ua', 'Oa': 'Ua',
                'ou': 'oo', 'Ou': 'Oo',
                'eng': 'ing', 'Eng': 'Ing',
                'ek': 'ik', 'Ek': 'Ik'}

tone_dict_1 = ['a', 'e', 'i', 'o', 'u', 'm', 'n', 'A', 'E', 'I', 'O', 'U', 'M', 'N']
tone_dict_4_1 = ['gh']
tone_dict_4_2 = ['h', 'k', 't', 'p']

#insert_sign_list = set(['-', '\u3000', '※', '」', '$', ',', '|', '﹑', '‧', '『', '=', '－', '<', '！', '（', '”', '＄', '◘', '〉', '《', '\uf04a', '、', '̀', 'Ⅳ', '●', '︰', '\x0b', '﹚', '\uf06d', '\t', '♩', '㏄', '!', '＋', 'Ⅰ', '%', '；', '\uf06c', '》', '＜', '“', '’', '，', '╳', '。', '﹙', '＞', 'Ⅵ', '̂', '＝', '*', '̍', '｜', '+', '[', '~', '‘', '）', '?', '〃', '`', 'Ⅲ', '̄', '℃', '#', '゛', '.', '△', '^', '？', '「', '─', '﹕', '_', 'Ⅱ', '】', '﹖', ';', '：', '～', '◎', '﹔', '\uf071', ')', ']', ':', '○', '．', '"', '』', '／', "'", '＊', '@', '﹗', '(', '―', '\uf06a', '\uf070', '【', '￥', '\\', '/', '▲', 'Ⅴ', '\uf06e', '〈', '>', '︱', '}', '{', '͘', '\uf06b', '&'])
insert_sign_list = set(['\u3000', '※', '」', '$', ',', '|', '﹑', '‧', '『', '=', '－', '<', '！', '（', '”', '＄', '◘', '〉', '《', '\uf04a', '、', 'Ⅳ', '●', '︰', '\x0b', '﹚', '\uf06d', '\t', '♩', '㏄', '!', '＋', 'Ⅰ', '%', '；', '\uf06c', '》', '＜', '“', '’', '，', '╳', '。', '﹙', '＞', 'Ⅵ', '＝', '*', '｜', '+', '[', '~', '‘', '）', '?', '〃', '`', 'Ⅲ', '℃', '#', '゛', '.', '△', '^', '？', '「', '─', '﹕', '_', 'Ⅱ', '】', '﹖', '：', '～', '◎', '﹔', '\uf071', ')', ']', ':', '○', '．', '"', '』', '／', "'", '＊', '@', '﹗', '(', '―', '\uf06a', '\uf070', '【', '￥', '\\', '/', '▲', 'Ⅴ', '\uf06e', '〈', '>', '︱', '}', '{', '\uf06b'])

def add_space(in_str):
    #insert_sign_list = [',', '.', '(', ')', ':', '"', "'", '?', '？', '！', '!']
    temp_cha_list = []
    for cha in in_str:
        if cha in insert_sign_list:
            temp_cha_list.append(' ')
            temp_cha_list.append(cha)
            temp_cha_list.append(' ')
        elif cha == '&':
            temp_cha_list.append(' ')
            temp_cha_list.append(cha)
        elif cha == ';':
            temp_cha_list.append(cha)
            temp_cha_list.append(' ')
        else:
            temp_cha_list.append(cha)
    return ''.join(temp_cha_list)

def trans_poj2tailo(in_str):
    in_str_sp = in_str.split()
    out_str = []
    for seg in in_str_sp:
        temp_syl_list = []
        seg_sp = seg.split('-')
        for syl in seg_sp:
            temp_syl = syl
            for key, value in poj2tailo_dict.items():
                if key in syl:
                    temp_syl = temp_syl.replace(key, value)
            match = re.search("(Nh?)([0-9])", temp_syl)
            if match:
                temp_syl = temp_syl[:match.start(0)] + match.group(1).replace("N", "nn") + match.group(2)

            temp_syl_list.append(temp_syl)
        out_str.append('-'.join(temp_syl_list))
    return ' '.join(out_str)

def trans_code2tone(in_str):
    out_str = in_str
    for key, value in code2tone_dict.items():
        out_str = out_str.replace(key, value)

    return out_str

def check_if_syl(in_str):
    count_dict = {'.': 0, '/': 0, ':': 0}
    for cha in in_str:
        if cha in count_dict:
            count_dict[cha] += 1

    for key, value in count_dict.items():
        if value > 1:
            return False
    else:
        return True

def rm_not_syl(in_str):
    in_str_sp = in_str.split()
    out_str = []
    for seg in in_str_sp:
        if not check_if_syl(seg):
            continue
        else:
            out_str.append(seg)
    return ' '.join(out_str)

def syl_trans(in_str):
    in_str_sp = add_space(in_str).replace('ⁿ', 'nn').split()
    out_seg_list = []
    for seg in in_str_sp:
        seg_sp = seg.split('-')
        out_syl_list = []
        for syl in seg_sp:
            for key, value in o_repeat_tone_dict.items():
                if key in syl:
                    out_syl_list.append(syl.replace(key, value[0]) + value[1])
                    break
            else:
                for key, value in tone_dict.items():
                    if key in syl:
                        out_syl_list.append(syl.replace(key, value[0]) + value[1])
                        break
                else:
                    for cha in syl:
                        if cha in tone_dict_1 or syl.endswith('gh'):
                            if syl.endswith('gh'):
                                out_syl_list.append(syl + '4')
                                break
                            elif cha in tone_dict_1 and syl[-1] in tone_dict_4_2:
                                out_syl_list.append(syl + '4')
                                break
                            else:
                                out_syl_list.append(syl + '1')
                                break
                    else:
                        out_syl_list.append(syl)
        out_seg_list.append('-'.join(out_syl_list))
        #print(out_seg_list)
    return ' '.join(out_seg_list)

"""
in_file_name = argv
input_string = 'Tân Khé-chheng ê Sió-toān (Lâu Chùn-sîn kì).'
print(syl_trans(input_string))
"""

if __name__ == '__main__':
    line = """
Tsò-lâng nā pîn-tuānn, tsi̍t-sì-lâng bē khuìnn-ua̍h.
"""
    line_rm_not_syl = rm_not_syl(line)
    transformed_str_poj = syl_trans(line_rm_not_syl)
    print(transformed_str_poj + '\n')

    # transformed_str_poj = "Ngou5-khun-ju5 chit8-tiuN5 aiNh4"
    transformed_str_tailo = trans_poj2tailo(transformed_str_poj)
    print(transformed_str_tailo + '\n')
