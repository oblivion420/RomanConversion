#!/bin/bash

DICT="taigiE"
# DICT="tailo"
# DICT="mandarinE"

cp ../get_ipa_dictionary/output/taigi_dictionary.txt lang/lexicon/taigi/lexicon.txt
cp ../get_ipa_dictionary/output/taigiE_dictionary.txt lang/lexicon/taigiE/lexicon.txt
cp ../static/taigi/lexicon_tailo.txt lang/lexicon/taigiE/lexicon_tailo.txt
cp ../static/taigi/lexicon_tailo.txt lang/lexicon/tailo/lexicon.txt
cp ../get_ipa_dictionary/output/mandarinE_dictionary.txt lang/lexicon/mandarinE/lexicon.txt

for dict in $DICT; do
    echo "Prepare dict ${dict}..."
    . local/prepare_dict.sh lang/lexicon/${dict}/lexicon.txt lang/dict/${dict}
    vocab_num=`cat lang/lexicon/${dict}/lexicon.txt | wc -l`
    echo "Vocab: ${vocab_num}"
done

cp ../get_ipa_dictionary/output/taigi_dictionary.joblib lang/dict/taigi/syl_info.joblib
cp ../get_ipa_dictionary/output/taigi_dictionary.joblib lang/dict/taigiE/syl_info.joblib
cp ../get_ipa_dictionary/output/mandarin_dictionary.joblib lang/dict/mandarinE/syl_info.joblib
cp ../get_ipa_dictionary/output/mandarin_varient2normal.joblib lang/dict/mandarinE/varient2normal.joblib
