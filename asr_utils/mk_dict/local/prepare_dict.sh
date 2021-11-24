#!/bin/bash
# e.g. ./prepare_dict.sh ../lang/lexicon/ky92k_ipa_diphthong_tone/lexicon.txt ../lang/dict/ky92k_ipa_diphthong_tone

src_lexicon=$1
dict_dir=$2

rm -rf $dict_dir
mkdir -p $dict_dir


rm -f $dict_dir/lexicon.txt
touch $dict_dir/lexicon.txt
cat <(echo -e "<SIL> sil\n<UNK> spn") $src_lexicon > $dict_dir/lexicon.txt


src_lexicon_tailo=`dirname $src_lexicon`/lexicon_tailo.txt
if [ -f $src_lexicon_tailo ]; then
    rm -f $dict_dir/lexicon_tailo.txt
    touch $dict_dir/lexicon_tailo.txt
    cp $src_lexicon_tailo $dict_dir/lexicon_tailo.txt
fi


rm -f $dict_dir/silence_phones.txt
touch $dict_dir/silence_phones.txt
echo -e "sil\nspn" > $dict_dir/silence_phones.txt

#
# find nonsilence phones
#
rm -f $dict_dir/nonsilence_phones.txt
touch $dict_dir/nonsilence_phones.txt

python3 local/prepare_nonsilience.py $dict_dir $dict_dir/nonsilence_phones.txt
# cat $src_lexicon | grep -v -F -f $dict_dir/silence_phones.txt | \
#     perl -ane 'print join("\n", @F[1..$#F]) . "\n"; ' > $dict_dir/nonsilence_phones.txt
#
# python3 local/sort_phone.py $dict_dir/nonsilence_phones.txt $dict_dir/nonsilence_phones.txt.tmp
# uniq $dict_dir/nonsilence_phones.txt.tmp > $dict_dir/nonsilence_phones.txt
# rm $dict_dir/nonsilence_phones.txt.tmp

#
# add optional silence phones
#

rm -f $dict_dir/optional_silence.txt
touch $dict_dir/optional_silence.txt
echo "sil"      > $dict_dir/optional_silence.txt

#
# extra questions
#
rm -f $dict_dir/extra_questions.txt

python3 local/prepare_extra_questions.py default $dict_dir/nonsilence_phones.txt $dict_dir/extra_questions.txt
# python3 local/prepare_extra_questions.py same_vowel_same_tone $dict_dir/nonsilence_phones.txt $dict_dir/extra_questions_base_vowel_base_tone.txt

# rm -f $dict_dir/extra_questions_vowel_1_tone_1.txt
# touch $dict_dir/extra_questions_vowel_1_tone_1.txt
#
# rm -f $dict_dir/extra_questions_vowel_0_tone_1.txt
# touch $dict_dir/extra_questions_vowel_0_tone_1.txt
#
# rm -f $dict_dir/extra_questions_vowel_1_tone_0.txt
# touch $dict_dir/extra_questions_vowel_1_tone_0.txt
# # cat $dict_dir/silence_phones.txt    | awk '{printf("%s ", $1);} END{printf "\n";}'  > $dict_dir/extra_questions.txt || exit 1;
#
# # 同 tone 不同音
# cat $dict_dir/nonsilence_phones.txt | awk 'match($0, /([^0-9]+)([0-9]+)/, a) {print a[2], a[1], $0}' | sort | cut -d' ' -f 3 | awk 'BEGIN{prev="";} {curr=$0; tone=substr($0,length($0),1); if (prev == tone || prev == "") printf("%s ", curr); else printf("\n%s ", curr); prev=tone;} END{printf "\n";}' > $dict_dir/extra_questions_vowel_0_tone_1.txt || exit 1;
# # 同音不同 tone
# cat $dict_dir/nonsilence_phones.txt | awk 'match($0, /([^0-9]+)([0-9]+)/, a) {print $0}' | awk 'BEGIN{prev="";} {curr=$0; sub(/[0-9]+/,"",$0); if (prev == $0 || prev == "") printf("%s ", curr); else printf("\n%s ", curr); prev=$0;} END{printf "\n";}' > $dict_dir/extra_questions_vowel_1_tone_0.txt || exit 1;
# # 兩者都有
# cat $dict_dir/extra_questions_vowel_0_tone_1.txt > $dict_dir/extra_questions_vowel_1_tone_1.txt || exit 1;
# cat $dict_dir/extra_questions_vowel_1_tone_0.txt >> $dict_dir/extra_questions_vowel_1_tone_1.txt || exit 1;

echo "Dictionary preparation succeeded"
