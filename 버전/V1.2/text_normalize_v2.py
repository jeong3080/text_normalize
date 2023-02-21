# -*- coding: utf-8 -*-
# Copyright 2020 TensorFlowTTS Team, Jaehyoung Kim(@crux153) and Taehoon Kim(@carpedm20)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Code based on https://github.com/carpedm20/multi-speaker-tacotron-tensorflow
"""Korean related helpers."""

import ast
import json
import os
import re

from jamo import h2j, hangul_to_jamo, j2h, jamo_to_hcj
from unicode import join_jamos 
import json
import time
with open('tn_dic_v2.json', 'r') as f:
    tn_dic = json.load(f)


"""
초성과 종성은 같아보이지만, 다른 character이다.
'_-!'(),-.:;? ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑ하ᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ~'
'_': 0, '-': 7, '!': 2, "'": 3, '(': 4, ')': 5, ',': 6, '.': 8, ':': 9, ';': 10,
'?': 11, ' ': 12, 'ᄀ': 13, 'ᄁ': 14, 'ᄂ': 15, 'ᄃ': 16, 'ᄄ': 17, 'ᄅ': 18, 'ᄆ': 19, 'ᄇ': 20,
'ᄈ': 21, 'ᄉ': 22, 'ᄊ': 23, 'ᄋ': 24, 'ᄌ': 25, 'ᄍ': 26, 'ᄎ': 27, 'ᄏ': 28, 'ᄐ': 29, 'ᄑ': 30,
'ᄒ': 31, 'ᅡ': 32, 'ᅢ': 33, 'ᅣ': 34, 'ᅤ': 35, 'ᅥ': 36, 'ᅦ': 37, 'ᅧ': 38, 'ᅨ': 39, 'ᅩ': 40,
'ᅪ': 41, 'ᅫ': 42, 'ᅬ': 43, 'ᅭ': 44, 'ᅮ': 45, 'ᅯ': 46, 'ᅰ': 47, 'ᅱ': 48, 'ᅲ': 49, 'ᅳ': 50,
'ᅴ': 51, 'ᅵ': 52, 'ᆨ': 53, 'ᆩ': 54, 'ᆪ': 55, 'ᆫ': 56, 'ᆬ': 57, 'ᆭ': 58, 'ᆮ': 59, 'ᆯ': 60,
'ᆰ': 61, 'ᆱ': 62, 'ᆲ': 63, 'ᆳ': 64, 'ᆴ': 65, 'ᆵ': 66, 'ᆶ': 67, 'ᆷ': 68, 'ᆸ': 69, 'ᆹ': 70,
'ᆺ': 71, 'ᆻ': 72, 'ᆼ': 73, 'ᆽ': 74, 'ᆾ': 75, 'ᆿ': 76, 'ᇀ': 77, 'ᇁ': 78, 'ᇂ': 79, '~': 80
"""

_pad = "pad"
_eos = "eos"
_punctuation = "!'(),-.:;? "
_special = "-"

_jamo_leads = [chr(_) for _ in range(0x1100, 0x1113)]
_jamo_vowels = [chr(_) for _ in range(0x1161, 0x1176)]
_jamo_tails = [chr(_) for _ in range(0x11A8, 0x11C3)]

_letters = _jamo_leads + _jamo_vowels + _jamo_tails

symbols = [_pad] + list(_special) + list(_punctuation) + _letters + [_eos]

_symbol_to_id = {c: i for i, c in enumerate(symbols)}
_id_to_symbol = {i: c for i, c in enumerate(symbols)}

quote_checker = """([`"'＂“‘])(.+?)([`"'＂”’])"""


def is_lead(char):
    return char in _jamo_leads


def is_vowel(char):
    return char in _jamo_vowels


def is_tail(char):
    return char in _jamo_tails


def get_mode(char):
    if is_lead(char):
        return 0
    elif is_vowel(char):
        return 1
    elif is_tail(char):
        return 2
    else:
        return -1


def _get_text_from_candidates(candidates):
    if len(candidates) == 0:
        return ""
    elif len(candidates) == 1:
        return jamo_to_hcj(candidates[0])
    else:
        return j2h(**dict(zip(["lead", "vowel", "tail"], candidates)))


def jamo_to_korean(text):
    text = h2j(text)

    idx = 0
    new_text = ""
    candidates = []

    while True:
        if idx >= len(text):
            new_text += _get_text_from_candidates(candidates)
            break

        char = text[idx]
        mode = get_mode(char)

        if mode == 0:
            new_text += _get_text_from_candidates(candidates)
            candidates = [char]
        elif mode == -1:
            new_text += _get_text_from_candidates(candidates)
            new_text += char
            candidates = []
        else:
            candidates.append(char)

        idx += 1
    return new_text


def compare_sentence_with_jamo(text1, text2):
    return h2j(text1) != h2j(text2)


def tokenize(text, as_id=False):
    # jamo package에 있는 hangul_to_jamo를 이용하여 한글 string을 초성/중성/종성으로 나눈다.
    text = normalize(text)
    tokens = list(
        hangul_to_jamo(text)
    )  # '존경하는'  --> ['ᄌ', 'ᅩ', 'ᆫ', 'ᄀ', 'ᅧ', 'ᆼ', 'ᄒ', 'ᅡ', 'ᄂ', 'ᅳ', 'ᆫ', '~']

    if as_id:
        return join_jamos([_symbol_to_id[token] for token in tokens])
    else:
        return join_jamos([token for token in tokens])


def tokenizer_fn(iterator):
    return (token for x in iterator for token in tokenize(x, as_id=False))


def normalize(text):
    start = time.time()
    text = text.strip()

    text = re.sub("\(\d+일\)", "", text)
    text = re.sub("\([⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+\)", "", text)

    text = normalize_with_dictionary(text, tn_dic["etc_dictionary"])
    text = normalize_english(text)
    text = normalize_quote(text)
    text = normalize_number(text)
    text = re.sub("[a-zA-Z]+", normalize_upper, text)
    return text+"<br>"+str(round(time.time()-start,4))+"초"


def normalize_with_dictionary(text, dic):
    if any(key in text for key in dic.keys()):
        pattern = re.compile("|".join(re.escape(key) for key in dic.keys()))
        return pattern.sub(lambda x: dic[x.group()], text)
    else:
        return text


def normalize_english(text):
    def fn(m):
        word = m.group()
        if word in tn_dic["english_dictionary"]:
            return tn_dic["english_dictionary"].get(word)
        else:
            return word

    text = re.sub("([A-Za-z]+)", fn, text)
    return text

#대문자에 해당되는 부분 치환하기
def normalize_upper(text):
    text = text.group(0)

    if all([char.isupper() for char in text]): #전부 대문자일 때
        return "".join(tn_dic["upper_to_kor"][char] for char in text)
    else:
        return text

def normalize_quote(text):
    def fn(found_text):
        from nltk import sent_tokenize  # NLTK doesn't along with multiprocessing

        found_text = found_text.group()
        unquoted_text = found_text[1:-1]

        sentences = sent_tokenize(unquoted_text)
        return " ".join(["'{}'".format(sent) for sent in sentences])

    return re.sub(quote_checker, fn, text)


number_checker = "([+-]?\d[\d,]*)[\.]?\d*"
count_checker = tn_dic["unit"]["unit_list"]#"(시|명|가지|살|마리|포기|송이|수|톨|통|점|개|벌|척|채|다발|그루|자루|줄|켤레|그릇|잔|마디|상자|사람|곡|병|판|번째)"


def normalize_number(text):
    text = normalize_with_dictionary(text, tn_dic["unit_to_kor1"])
    text = normalize_with_dictionary(text, tn_dic["unit_to_kor2"])
    text = re.sub(
        number_checker + count_checker, lambda x: number_to_korean(x, True), text
    )
    text = re.sub(number_checker, lambda x: number_to_korean(x, False), text)
    return text


num_to_kor1 = [""] + list("일이삼사오육칠팔구")
num_to_kor2 = [""] + list("만억조경해")
num_to_kor3 = [""] + list("십백천")

# count_to_kor1 = [""] + ["하나","둘","셋","넷","다섯","여섯","일곱","여덟","아홉"]
count_to_kor1 = [""] + ["한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]

count_tenth_dict = {
    "십": "열",
    "두십": "스물",
    "세십": "서른",
    "네십": "마흔",
    "다섯십": "쉰",
    "여섯십": "예순",
    "일곱십": "일흔",
    "여덟십": "여든",
    "아홉십": "아흔",
}


def number_to_korean(num_str, is_count=False):
    if is_count:
        num_str, unit_str = num_str.group(1), num_str.group(2)
    else:
        num_str, unit_str = num_str.group(), ""

    num_str = num_str.replace(",", "")
    
    try: 
        num = ast.literal_eval(num_str)
    except SyntaxError:
        kor = ""
        kor += re.sub("\d", lambda x: tn_dic["num_to_kor"][x.group()], num_str)
        if num_str.startswith("+"):
            kor = " 플러스 " + kor[1:]
        elif num_str.startswith("-"):
            kor = " 마이너스 " + kor[1:]
        return kor
    
    if num == 0:
        if num_str.startswith("+"):
            return " 플러스 영"
        elif num_str.startswith("-"):
            return " 마이너스 영"

    check_float = num_str.split(".")
    if len(check_float) == 2:
        digit_str, float_str = check_float
    elif len(check_float) >= 3:
        raise Exception(" [!] Wrong number format")
    else:
        digit_str, float_str = check_float[0], None

    if is_count and float_str is not None:
        raise Exception(" [!] `is_count` and float number does not fit each other")

    digit = int(digit_str)
    if digit_str.startswith("-"):
        digit, digit_str = abs(digit), str(abs(digit))

    kor = ""
    size = len(str(digit))
    tmp = []
    for i, v in enumerate(digit_str, start=1):
        v = int(v)

        if v != 0:
            if is_count:
                tmp += count_to_kor1[v]
            else:
                tmp += num_to_kor1[v]

            tmp += num_to_kor3[(size - i) % 4]

        if (size - i) % 4 == 0 and len(tmp) != 0:
            kor += "".join(tmp)
            tmp = []
            kor += num_to_kor2[int((size - i) / 4)]
    if is_count:
        if kor.startswith("한") and len(kor) > 1:
            kor = kor[1:]

        if any(word in kor for word in count_tenth_dict):
            kor = re.sub(
                "|".join(count_tenth_dict.keys()),
                lambda x: count_tenth_dict[x.group()],
                kor,
            )
    if not is_count and kor.startswith(("일십", "일백","일천","일만")) and len(kor) > 1:
        kor = kor[1:]

    if float_str is not None:
        kor += "쩜 "
        kor += re.sub("\d", lambda x: tn_dic["num_to_kor"][x.group()], float_str)
    if num_str.startswith("+"):
        kor = "플러스 " + kor
    elif num_str.startswith("-"):
        kor = "마이너스 " + kor
    return kor + unit_str