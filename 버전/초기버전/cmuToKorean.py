# -*- coding: utf-8 -*-
from korean import Korean
import abc
import sys
import re
import importlib
import cmudict
importlib.reload(sys)


class CMUToKorean(object):
    class Condition(object):
        class Interface(object, metaclass=abc.ABCMeta):
            @abc.abstractmethod
            def test(self, map, map_index, lhs):
                pass

        class IsFirst(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                if map_index[0] == 0:
                    if map_index[1] == 0:
                        return True

                return False

        class IsLast(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                last_map_index = [len(map) - 1, len(map[len(map) - 1][0]) - 1]

                if map_index[0] == last_map_index[0]:
                    if map_index[1] == last_map_index[1]:
                        return True

                return False

        class IsLastGroup(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                if map_index[0] == len(map) - 1:
                    return True

                return False

        class IsNotExistsLastVowel(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                group_index = map_index[0]
                phonetic_index = map_index[1] + 1

                for token_list in map[group_index:len(map)]:
                    phonetic_list = token_list[0]
                    for phonetic in phonetic_list[phonetic_index:len(phonetic_list)]:
                        m = re.match(r'(\D+)(\d)?([!])?', phonetic)
                        symbol = m.groups()[0]
                        if symbol in CMUToKorean.vowel_to_korean_dict:
                            return False

                    phonetic_index = 0

                return True

        class IsExistsFrontInVowel(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                group_index = map_index[0]
                phonetic_index = map_index[1] + 1

                for token_list in map[group_index:len(map)]:
                    phonetic_list = token_list[0]
                    for phonetic in phonetic_list[phonetic_index:len(phonetic_list)]:
                        m = re.match(r'(\D+)(\d)?([!])?', phonetic)
                        symbol = m.groups()[0]
                        if symbol in CMUToKorean.vowel_to_korean_dict:
                            return True
                        else:
                            return False

                    phonetic_index = 0

                return False

        class IsExistsFrontInPhonetic(Interface):
            phonetic = None

            def __init__(self, phonetic):
                self.phonetic = phonetic

            def test(self, map, map_index, lhs):
                group_index = map_index[0]
                phonetic_index = map_index[1] + 1

                for token_list in map[group_index:len(map)]:
                    phonetic_list = token_list[0]
                    for phonetic in phonetic_list[phonetic_index:len(phonetic_list)]:
                        m = re.match(r'(\D+)(\d)?([!])?', phonetic)
                        symbol = m.groups()[0]

                        if symbol == self.phonetic or phonetic == self.phonetic:
                            return True
                        else:
                            return False

                    phonetic_index = 0

                return False

        class IsExistsBackInVowel(Interface):
            def __init__(self):
                pass

            def test(self, map, map_index, lhs):
                group_index = map_index[0]

                if map_index[1] == 0:
                    if group_index == 0:
                        return False

                    group_index -= 1
                    phonetic_index = len(map[group_index][0]) - 1
                else:
                    phonetic_index = map_index[1] - 1

                phonetic = map[group_index][0][phonetic_index]
                m = re.match(r'(\D+)(\d)?([!])?', phonetic)
                symbol = m.groups()[0]

                if symbol in CMUToKorean.vowel_to_korean_dict:
                    return True

                return False

        class IsExistsBackInPhonetic(Interface):
            phonetic = None

            def __init__(self, phonetic):
                self.phonetic = phonetic

            def test(self, map, map_index, lhs):
                group_index = map_index[0]

                if map_index[1] == 0:
                    if group_index == 0:
                        return False

                    group_index -= 1
                    phonetic_index = len(map[group_index][0]) - 1
                else:
                    phonetic_index = map_index[1] - 1

                phonetic = map[group_index][0][phonetic_index]
                m = re.match(r'(\D+)(\d)?([!])?', phonetic)
                symbol = m.groups()[0]

                if symbol == self.phonetic or phonetic == self.phonetic:
                    return True

                return False

        class IsExistsLatestKorean(Interface):
            korean = None

            def __init__(self, korean):
                self.korean = korean

            def test(self, map, map_index, lhs):
                found = False
                i = 0
                for i in range(1, len(lhs) + 1):
                    if re.search(str(r'[???-??????-??????-???]+'), lhs[-i]):
                        found = True
                        break

                if not found:
                    return False

                if lhs[-i] == self.korean:
                    return True

                return False

        class IsExistsMappingWord(Interface):
            alphabet = None

            def __init__(self, alphabet):
                self.alphabet = alphabet

            def test(self, map, map_index, lhs):
                group_index = map_index[0]

                if re.search(self.alphabet, map[group_index][1]):
                    return True

                return False

        class RegexPhoneticGroup(Interface):
            regex = None

            def __init__(self, regex):
                self.regex = regex

            def test(self, map, map_index, lhs):
                group_index = map_index[0]
                if re.search(self.regex, ''.join(map[group_index][0])):
                    return True

                return False

        class RegexWordGroup(Interface):
            regex = None

            def __init__(self, regex):
                self.regex = regex

            def test(self, map, map_index, lhs):
                group_index = map_index[0]
                if re.search(self.regex, ''.join(map[group_index][1])):
                    return True

                return False

        class RegexWordNextGroup(Interface):
            regex = None

            def __init__(self, regex):
                self.regex = regex

            def test(self, map, map_index, lhs):
                group_index = map_index[0] + 1

                if len(map) <= group_index:
                    return False

                if re.search(self.regex, ''.join(map[group_index][1])):
                    return True

                return False

    class Control(object):
        class IF(object):
            chain = []

            def __init__(self, condition, value):
                self.chain = [{'condition': condition, 'value': value}]

            def ELIF(self, condition, value):
                self.chain.append({'condition': condition, 'value': value})
                return self

            def ELSE(self, value):
                self.chain.append(value)
                return self

    vowel_to_korean_dict = {
        'AA': [
            Control
                .IF(Condition.IsExistsMappingWord('O'), ['???', '???', '???'])
                .ELIF(Condition.IsFirst(), '???')
                .ELIF(Condition.IsLast(), ['???', '???'])
                .ELSE(['???', '???'])
        ],

        'AO': ['???', '???'],
        'AE': ['???'],
        'AY': ['??????', '??????', '??????+', '??????+'],

        'AH': [
            Control
                .IF(Condition.IsFirst(),
                    Control
                    .IF(Condition.IsExistsMappingWord('AU'), '???')
                    .ELIF(Condition.IsExistsBackInPhonetic('Z'), ['???', '???', '???'])
                    .ELSE(['???', '???']))
                .ELIF(Condition.IsLast(), ['???', '???'])
                .ELIF(Condition.IsExistsMappingWord('EI'), ['??????', '???'])
                .ELIF(Condition.IsExistsMappingWord('IU'), ['???', '???'])
                .ELIF(Condition.IsExistsMappingWord('IO'), ['???', '???', '???'])
                .ELIF(Condition.IsExistsMappingWord('UA'), ['???', '???'])
                .ELSE(
                    Control
                    .IF(Condition.IsExistsMappingWord('A'),
                        Control
                        .IF(Condition.IsNotExistsLastVowel(),
                            Control
                            .IF(Condition.RegexWordNextGroup(r'.E'), ['???', '???'])
                            .ELSE(['???', '???']))
                        .ELSE(['???', '???']))
                    .ELIF(Condition.IsExistsMappingWord('E'),
                          Control
                          .IF(Condition.IsExistsFrontInPhonetic('N'), ['???', '???'])
                          .ELSE(['???', '???']))
                    .ELIF(Condition.IsExistsMappingWord('U'), ['???', '???'])
                    .ELIF(Condition.IsExistsMappingWord('O'), ['???', '???', '???'])
                    .ELIF(Condition.IsExistsMappingWord('I'),
                          Control
                          .IF(Condition.IsNotExistsLastVowel(), ['???', '???'])
                          .ELSE('???'))
                )
        ],

        'AW': ['??????', '??????', '??????+', '??????+'],

        'EH': ['???'],

        'ER': [
            Control
                .IF(Condition.IsLast(), ['???', '???'])
                .ELIF(Condition.IsExistsFrontInVowel(), '???/???')
                .ELSE('???'),

            Control
                .IF(Condition.IsExistsMappingWord('OR'),
                    Control
                    .IF(Condition.IsLast(), ['???', '???'])
                    .ELIF(Condition.IsExistsFrontInVowel(), '???/???')
                    .ELSE('???'))
        ],

        'EY': ['??????', '??????+', '???'],

        'EY2': ['??????', '??????+'],

        'IH': ['???'],

        'IY': ['???', '???+'],

        'UW': ['???', '???+'],

        'UH': [
            Control
                .IF(Condition.IsExistsMappingWord('EU'), '??????')
                .ELIF(Condition.IsExistsMappingWord('UE'), '???')
                .ELIF(Condition.IsExistsMappingWord('OO'), '???')
                .ELIF(Condition.IsExistsMappingWord('OU'),
                      Control
                      .IF(Condition.IsExistsBackInPhonetic('Y'), ['???', '???', '???'])
                      .ELIF(Condition.IsExistsBackInPhonetic('SH'), ['???', '???', '???'])
                      .ELSE(['???', '???', '???']))
                .ELIF(Condition.IsExistsMappingWord('U'),
                      Control
                      .IF(Condition.IsExistsBackInPhonetic('Y'), ['???', '???', '???'])
                      .ELIF(Condition.IsExistsBackInPhonetic('SH'), ['???', '???', '???'])
                      .ELSE(['???', '???']))
                .ELSE(['???', '???'])
        ],

        'OW': [
            Control
                .IF(Condition.IsExistsMappingWord('OW'),
                    Control
                    .IF(Condition.IsExistsFrontInVowel(), ['??????+', '???'])
                    .ELSE(['??????', '???']))
                .ELSE('???')
        ],

        'OY': ['??????', '??????+']
    }

    semivowel_to_korean_dict = {
        'W': ['/???+', '???+'],
        'Y': ['???+']
    }

    consonant_to_korean_dict = {
        'B': ['???'],
        'D': ['???'],
        'F': ['???'],
        'G': ['???'],
        'K': ['???'],
        'M': ['???'],
        'N': ['???'],
        'P': ['???'],
        'T': ['???'],
        'V': ['???'],
        'HH': ['/???'],

        'Z': [
            Control
                .IF(Condition.IsExistsLatestKorean('???'), '-/???')
                .ELIF(Condition.IsExistsLatestKorean('???'), '-/???')
                .ELIF(Condition.IsLast(), ['/???', '/???'])
                .ELSE('/???')
        ],

        'L': [
            Control
                .IF(Condition.IsLast(), '???')
                .ELSE('???^')    # ex) ??????
        ],

        'R': [
            Control
                .IF(Condition.IsExistsBackInVowel(),
                    Control
                    .IF(Condition.IsExistsFrontInVowel(), '/???')
                    .ELIF(Condition.IsLast(),
                          Control
                          .IF(Condition.IsExistsLatestKorean('???'),
                              Control
                              .IF(Condition.RegexWordGroup(r'^.*RE$'), '???')
                              .ELSE(['', '???']))
                          .ELIF(Condition.IsExistsLatestKorean('???'),
                                Control
                                .IF(Condition.RegexWordGroup(r'^.*RE$'), '???')
                                .ELSE(['', '???']))
                          .ELIF(Condition.IsExistsLatestKorean('???'), ['???', '???'])
                          .ELIF(Condition.IsExistsLatestKorean('???'), ['???', '???'])
                          .ELIF(Condition.IsExistsLatestKorean('???'), ['???', '???'])
                          .ELIF(Condition.IsExistsLatestKorean('???'), ['???', '???'])
                          .ELSE(['???', '???', '???']))
                    .ELIF(Condition.IsExistsLatestKorean('???'), ['', '???'])
                    .ELIF(Condition.IsExistsLatestKorean('???'), ['', '???'])
                    .ELIF(Condition.IsExistsLatestKorean('???'), ['', '???'])
                    .ELIF(Condition.IsExistsLatestKorean('???'), ['', '???'])
                    .ELSE(['???', '???', '???']))
                .ELSE('???')
        ],

        'S': [
            Control
                .IF(Condition.IsFirst(),
                    Control
                    .IF(Condition.IsExistsMappingWord('SS'), '/???')
                    .ELSE('/???'))
                .ELIF(
                    Condition.IsExistsBackInPhonetic('T'),
                    Control
                    .IF(Condition.IsExistsMappingWord('Z'), ['-/???', '/???'])    # ex) BLITZKRIEG ??????,??????
                    .ELIF(Condition.IsLast(), '-/???')
                    .ELIF(Condition.RegexPhoneticGroup(r'.+TS.+'), ['-/???', '-/???'])    # ex) FTSM ?????????, ?????????
                    .ELIF(
                        Condition.RegexPhoneticGroup(r'.+TS'),
                        Control
                            .IF(Condition.IsExistsFrontInVowel(), '-/???')  # ex) ACCOUNTANCY AH0 K AW1 N T AH0 N T S IY2
                            .ELSE('-/???')
                    )
                    .ELIF(Condition.IsExistsFrontInVowel(), ['/???', '-/???'])  # ex) BATSON ??????, ??????
                    .ELIF(Condition.IsExistsFrontInPhonetic('T'), '/???')    # ex) TST ?????????
                    .ELIF(Condition.RegexPhoneticGroup(r'TS.+'), ['-/???', '/???'])    # ex) TSM ??????,?????????
                    .ELSE('-/???')
                )

                .ELSE('/???')
        ],

        'NG': [
            Control
                .IF(Condition.IsExistsFrontInVowel(), '~??????')
                .ELSE('~???')
        ],

        'SH': ['/???#'],

        'CH': [
            Control
                .IF(Condition.IsLast(), '???')
                .ELIF(Condition.IsLastGroup(),
                      Control
                      .IF(Condition.RegexWordGroup(r'.*CHE.*'), '???')
                      .ELSE('/???'))
                .ELSE('/???')
        ],

        'DH': [
            Control
                .IF(Condition.IsFirst(), '???')
                .ELIF(Condition.RegexWordNextGroup(r'^A'), '/???')
                .ELIF(Condition.IsExistsBackInPhonetic('S'), '')  # ??????
                .ELIF(Condition.IsExistsBackInPhonetic('Z'), '')  # ??????
                .ELIF(Condition.IsExistsBackInPhonetic('ER'), '???')
                .ELIF(Condition.IsExistsBackInPhonetic('OW'), '???')
                .ELIF(Condition.IsExistsBackInPhonetic('AH'), '???')
                .ELIF(Condition.IsExistsBackInPhonetic('IY'), '???')
                .ELIF(Condition.IsExistsBackInPhonetic('IH'), '???')
                .ELIF(Condition.IsExistsBackInPhonetic('Y'), '???')
                .ELSE(['???', '/???'])
        ],

        'JH': [
            Control
                .IF(Condition.IsLast(), '???')
                .ELSE('/???')
        ],

        'TH': [
            Control
                .IF(Condition.IsFirst(), '/???')
                .ELIF(Condition.IsNotExistsLastVowel(), '/???')
                .ELSE(
                    Control
                      .IF(Condition.IsExistsBackInPhonetic('S'), '')
                      .ELIF(Condition.IsExistsBackInPhonetic('Z'), '')
                      .ELSE('/???')
                )
        ],

        'ZH': [
            Control
                .IF(Condition.IsFirst(),
                    Control
                    .IF(Condition.IsExistsMappingWord('X'), '/???#')
                    .ELSE('/???#'))
                .ELIF(Condition.IsExistsMappingWord('S'),
                      Control
                      .IF(Condition.RegexWordNextGroup(r'^IA'), '???')
                      .ELSE('/???#'))
                .ELSE('/???#')
        ],
    }

    operation_set = (
        '/', '~', '+', '-', '^', '#', '?'
    )

    alphabet_vowel_to_cmu_dict = {
        'A': 'AA',
        'E': 'EH',
        'I': 'IH',
        'O': 'AO',
        'U': 'UH',
        'W': 'W',
        'Y': 'Y',
    }

    alphabet_consonant_set = (
        'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
        'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'X', 'Z'
    )

    alphabet_vowel_set = (
        'A', 'E', 'I', 'O', 'U', 'W', 'Y'
    )

    korean_convert_sharp_dict = {
        '???': '???',
        '???': '???',
        '???': '???',
        '???': '???',
        '???': '???',
        '???': '???',
        '???': '???',
    }

    korean_coda_sound = {
        '???': '???', '???': '???',
        '???': '???',
        '???': '???', '???': '???', '???': '???',
        '???': '???', '???': '???', '???': '???',
        '???': '???',
        '???': '???',
        '???': '???', '???': '???',
        '???': '???',

        '???': '???',
        '???': '???',
    }

    @staticmethod
    def convert(word, **kwargs):
        try:
            phonetic = " ".join(cmudict.dict()[word][0])
        except:
            return word
        word = str(word).upper()
        phonetic = str(phonetic).upper()
        map = CMUToKorean._phonetic_word_mapping(word, phonetic)
        if not map:
            return None

        combination = []
        map_index = [0, 0]

        for group in map:
            if CMUToKorean._pattern_exception(map, map_index[0], combination):
                map_index[0] += 1
                map_index[1] = 0
                continue

            for phonetic in group[0]:
                m = re.match(r'(\D+)(\d)?([?])?', phonetic)
                regrp = m.groups()
                symbol = regrp[0]
                number = regrp[1]
                op = regrp[2]
                ref_dict = None
                print(0, phonetic, symbol, number)
                if symbol in CMUToKorean.consonant_to_korean_dict:
                    ref_dict = CMUToKorean.consonant_to_korean_dict
                elif symbol in CMUToKorean.semivowel_to_korean_dict:
                    ref_dict = CMUToKorean.semivowel_to_korean_dict
                elif symbol in CMUToKorean.vowel_to_korean_dict:
                    ref_dict = CMUToKorean.vowel_to_korean_dict
                print(-1, ref_dict)
                if not ref_dict:
                    if phonetic not in CMUToKorean.operation_set:
                        return None
                    value = phonetic

                elif number and (symbol + number) in ref_dict:
                    value = ref_dict[symbol + number]
                else:
                    value = ref_dict[symbol]

                # op code '?'??? ????????? ????????? ????????????
                if op == '?':
                    clone = []
                    clone.extend(value)
                    clone.append('')
                    value = clone

                # combination
                # combination = value_list * combination
                print(1, map,map_index, combination, value)
                combination = CMUToKorean._join_process(map, map_index, combination, value)
                print(2, combination)
                map_index[1] += 1

            map_index[0] += 1
            map_index[1] = 0
        print(3, combination)
        result = CMUToKorean._assembly(src_korean_list=combination, **kwargs)
        return result

    @staticmethod
    def _assembly(src_korean_list, **kwargs):
        def join(lhs, rhs):
            r1 = []

            if lhs and isinstance(lhs, list):
                for l in lhs:
                    r2 = join(l, rhs)
                    if isinstance(r2, list):
                        r1.extend(r2)
                    else:
                        r1.append(r2)

            elif rhs and isinstance(rhs, list):
                for r in rhs:
                    r2 = join(lhs, r)
                    if isinstance(r2, list):
                        r1.extend(r2)
                    else:
                        r1.append(r2)
            else:
                if not lhs:
                    lhs = ''

                if not rhs:
                    rhs = ''

                return [lhs + rhs]

            return r1

        def syllable_join(dest, src_onset, src_nucleus, src_coda):
            if not src_onset:
                src_onset = [None]
            if not src_nucleus:
                src_nucleus = [None]
            if not src_coda:
                src_coda = [None]

            if not isinstance(src_onset, list):
                src_onset = [src_onset]
            if not isinstance(src_nucleus, list):
                src_nucleus = [src_nucleus]
            if not isinstance(src_coda, list):
                src_coda = [src_coda]

            r = []
            for o in src_onset:
                for n in src_nucleus:
                    for c in src_coda:
                        r.append(str(Korean.Syllable(phoneme_onset=o, phoneme_nucleus=n, phoneme_coda=c)))

            return join(dest, r)

        # pass 1
        # ????????? ????????????
        pass1_result = []

        for text in src_korean_list:
            combination = []
            korean = Korean(text)
            korean_len = len(korean)
            carry_onset = None
            carry_nucleus = None
            carry_coda = None
            consonant_continuous = False
            op = None
            i = 0

            while i < korean_len:
                cur = korean[i]
                consonant_combined = False

                if isinstance(cur, Korean.Syllable):
                    # op code ??????
                    if op:
                        # ?????? ????????? ????????? ?????????
                        if op == '~':
                            # ????????? ??????
                            if not cur.is_completed() and not cur.phoneme_nucleus:
                                # ????????? ????????? ??????????????? ?????? ????????????
                                if not carry_onset and len(combination) == 0:
                                    carry_onset = str(cur)

                                # ????????? ??????, ????????? ?????? ????????????
                                if not carry_onset and not carry_nucleus:
                                    # ??? ????????? ???????????? ????????? ?????????
                                    for j in range(0, len(combination)):
                                        last_elem = Korean.Syllable(letter=combination[j][-1])
                                        last_elem.phoneme_coda = str(cur)
                                        last_elem.combine()
                                        combination[j] = combination[j][:-1]
                                        combination[j] += str(last_elem)

                                else:
                                    carry_coda = str(cur)
                            else:
                                # ????????? ???????????? ??????
                                # middle.exception
                                op = None
                                continue

                        # ??????+?????? ???????????? ????????? ????????? ?????? ??? ???????????? ??????
                        elif op == '^':
                            if not carry_coda:
                                # middle.exception
                                # ????????? ????????? ??????????????? ??????
                                op = None
                                continue

                            # ?????? ????????? ???????????? ??????
                            if not cur.is_completed() and cur.phoneme_onset:
                                # middle.exception
                                # ????????? ???????????? ??????
                                op = None
                                continue

                            # ?????? ??????+?????? ????????? ?????? ????????? '???' ??? ????????????
                            if cur.phoneme_onset and cur.phoneme_nucleus:
                                if cur.phoneme_onset != '???':
                                    op = None
                                    continue

                            tmp_coda = carry_coda

                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                            carry_onset = tmp_coda
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = cur.phoneme_coda

                        # ????????? ??????
                        elif op == '+':
                            # ?????? ????????? ????????????
                            if carry_nucleus and cur.phoneme_nucleus:
                                if carry_coda:
                                    # ????????? ????????? ???????????? ??????
                                    op = None
                                    continue

                                if cur.phoneme_onset and cur.phoneme_onset != '???':
                                    # ?????? ????????? ????????? ??????????????? '???' ??? ????????????
                                    op = None
                                    continue

                                if isinstance(carry_nucleus, list):
                                    for i in range(0, len(carry_nucleus)):
                                        # ????????? ????????? ????????? ????????? ???????????? ?????????
                                        if carry_nucleus[i] != cur.phoneme_nucleus:
                                            nucleus = carry_nucleus[i] + cur.phoneme_nucleus
                                            if nucleus not in Korean.phoneme_nucleus_phonetic_combine_dict:
                                                carry_nucleus[i] = cur.phoneme_nucleus
                                            else:
                                                carry_nucleus[i] = Korean.phoneme_nucleus_phonetic_combine_dict[nucleus]

                                # ????????? ????????? ????????? ????????? ???????????? ?????????
                                elif carry_nucleus != cur.phoneme_nucleus:
                                    nucleus = carry_nucleus + cur.phoneme_nucleus
                                    if nucleus not in Korean.phoneme_nucleus_phonetic_combine_dict:
                                        # ?????? ?????? ????????? ???????????? ????????????
                                        op = None
                                        continue

                                    carry_nucleus = Korean.phoneme_nucleus_phonetic_combine_dict[nucleus]

                                carry_coda = cur.phoneme_coda

                            else:
                                # ??????+????????? ???????????????
                                op = None
                                continue

                        # ???# -> ???,???, ???# -> ???,???
                        elif op == '#':
                            # ????????? ??????+?????? ????????????
                            if carry_onset and carry_nucleus and not carry_coda:
                                # ????????? ?????? ??????
                                combination = syllable_join(combination,
                                                            carry_onset,
                                                            carry_nucleus,
                                                            carry_coda)

                                carry_onset = None
                                carry_nucleus = None
                                carry_coda = None
                                continue

                            # ????????? ????????? ?????? ?????? ????????????
                            if not carry_onset:
                                carry_onset = '???'

                            # ????????? ????????? ???????????????
                            if carry_coda:
                                # ????????? ?????? ????????? ??????
                                tmp_coda = carry_coda
                                carry_coda = None

                                combination = syllable_join(combination,
                                                            carry_onset,
                                                            carry_nucleus,
                                                            carry_coda)

                                carry_onset = tmp_coda
                                carry_coda = None

                            # ?????? ????????? ???????????? ????????? '???' ??????
                            # ?????? ????????? ????????????
                            if (cur.phoneme_nucleus and cur.phoneme_onset == '???')\
                                    or (cur.phoneme_nucleus and not cur.phoneme_onset):

                                if cur.phoneme_nucleus in CMUToKorean.korean_convert_sharp_dict:
                                    carry_nucleus = CMUToKorean.korean_convert_sharp_dict[cur.phoneme_nucleus]
                                    carry_coda = cur.phoneme_coda
                                else:
                                    # middle.exception
                                    # ???????????? ????????? ??????
                                    op = None
                                    continue

                            # ?????? ????????? ????????????
                            elif cur.is_completed():
                                # ???#??? -> ??????
                                carry_nucleus = ['???', '???'] if len(combination) == 0 else '???'

                                combination = syllable_join(combination,
                                                            carry_onset,
                                                            carry_nucleus,
                                                            carry_coda)

                                carry_onset = cur.phoneme_onset
                                carry_nucleus = cur.phoneme_nucleus
                                carry_coda = cur.phoneme_coda

                            # ?????? ????????? ???????????????
                            else:
                                carry_nucleus = ['???', '???'] if len(combination) == 0 else '???'

                                # ????????? ?????? ?????????
                                if consonant_continuous:
                                    combination = syllable_join(combination,
                                                                carry_onset,
                                                                carry_nucleus,
                                                                carry_coda)

                                    carry_onset = cur.phoneme_onset
                                    carry_nucleus = cur.phoneme_nucleus
                                    carry_coda = cur.phoneme_coda
                                else:
                                    carry_coda = cur.phoneme_onset

                                consonant_combined = True

                        op = None

                    # ??????????????? ??????????????? ????????? '???' ??????
                    elif cur.is_completed() and cur.phoneme_onset == '???':

                        # ????????? ???????????? ?????????
                        if not carry_onset and not carry_nucleus and not carry_coda:
                            carry_onset = cur.phoneme_onset
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = cur.phoneme_coda

                        # ????????? ????????? ???????????????(?????? -> ???)
                        elif carry_onset and not carry_nucleus and not carry_coda:
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = cur.phoneme_coda

                        # ????????? ????????? ???????????? ??????
                        elif carry_coda:
                            # ????????? ?????? ????????? ??????
                            tmp_coda = carry_coda
                            carry_coda = None

                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                            carry_onset = tmp_coda
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = cur.phoneme_coda

                        # ?????? ????????? ????????? ????????? ?????????
                        elif carry_nucleus == cur.phoneme_nucleus:

                            # ????????? ??????????????? (??????, ?????? -> ???, ???)
                            carry_coda = cur.phoneme_coda

                        else:
                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                            carry_onset = cur.phoneme_onset
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = cur.phoneme_coda

                    # ??????????????? ????????? ???????????????
                    elif not cur.phoneme_onset and not cur.phoneme_coda and cur.phoneme_nucleus:
                        # middle.exception
                        # ????????? ???????????? ????????? ????????? ?????????

                        # ????????? ????????? ???????????? ?????????
                        if not carry_onset:
                            carry_onset = '???'

                        # ????????? ??????/????????? ???????????????
                        if carry_onset and carry_nucleus:

                            # ????????? ????????? ????????????
                            if carry_coda:
                                tmp_onset = carry_coda
                                carry_coda = None
                            else:
                                tmp_onset = '???'

                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                            carry_onset = tmp_onset
                            carry_nucleus = cur.phoneme_nucleus
                            carry_coda = None

                        # ????????? ????????? ????????????
                        elif carry_onset:
                            carry_nucleus = cur.phoneme_nucleus

                    # ??????????????? ????????? ???????????????
                    elif not cur.phoneme_nucleus:

                        # ?????? ????????? ????????? ???????????????
                        if carry_onset:

                            # ????????? ?????? ?????????
                            if consonant_continuous:

                                # ????????? ?????? ????????? ??????
                                tmp_onset = carry_coda
                                carry_coda = None

                                combination = syllable_join(combination,
                                                            carry_onset,
                                                            carry_nucleus,
                                                            carry_coda)

                                carry_onset = tmp_onset
                                carry_nucleus = '???'
                                carry_coda = cur.phoneme_onset
                                consonant_combined = True

                            elif carry_nucleus and carry_coda:
                                combination = syllable_join(combination,
                                                            carry_onset,
                                                            carry_nucleus,
                                                            carry_coda)

                                carry_onset = cur.phoneme_onset
                                carry_nucleus = cur.phoneme_nucleus
                                carry_coda = cur.phoneme_coda

                            elif carry_nucleus:
                                carry_coda = cur.phoneme_onset

                            else:
                                # '???' ????????? ????????? (T L -> ???)
                                carry_nucleus = '???'
                                carry_coda = cur.phoneme_onset
                                consonant_combined = True
                        else:
                            carry_onset = cur.phoneme_onset

                    else:
                        # ????????? ??????/????????? ???????????????
                        if carry_onset and carry_nucleus:
                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                        carry_onset = cur.phoneme_onset
                        carry_nucleus = cur.phoneme_nucleus
                        carry_coda = cur.phoneme_coda

                    if consonant_combined:
                        consonant_continuous = True
                    else:
                        consonant_continuous = False

                else:
                    # ????????? op code??? # ????????????
                    if op == '#':
                        # ????????? ????????? ?????????
                        if carry_onset and not carry_nucleus and not carry_coda:
                            carry_nucleus = ['???', '???'] if len(combination) == 0 else '???'

                    op = None

                    # ????????? ?????? ????????????
                    if cur == '/':
                        if carry_onset:
                            # ????????? ?????? ???????????????
                            if not carry_nucleus:
                                carry_nucleus = '???'

                            # ????????? ?????? ????????????
                            if not carry_onset:
                                carry_onset = '???'

                            combination = syllable_join(combination,
                                                        carry_onset,
                                                        carry_nucleus,
                                                        carry_coda)

                            carry_onset = None
                            carry_nucleus = None
                            carry_coda = None
                            consonant_continuous = False

                    # ?????? ????????? ?????????
                    elif cur == '-':
                        if carry_coda:
                            carry_coda = None
                        elif carry_nucleus:
                            carry_nucleus = None
                        elif carry_onset:
                            carry_onset = None

                    # ??????
                    elif cur == '?':
                        pass

                    # op code??? ??????
                    else:
                        op = cur

                i += 1

            # ?????? ?????? ??????
            if carry_onset or carry_nucleus or carry_coda:
                # ????????? ?????? ???????????????
                if not carry_nucleus:

                    # ????????? op code??? # ????????????
                    if op == '#':
                        carry_nucleus = ['???', '???'] if len(combination) == 0 else '???'
                    else:
                        carry_nucleus = '???'

                # ????????? ?????? ????????????
                if not carry_onset:
                    carry_onset = '???'

                combination = syllable_join(combination,
                                            carry_onset,
                                            carry_nucleus,
                                            carry_coda)

            pass1_result.extend(combination)

        # pass 2
        # ?????? ??????
        pass2_result = []

        for text in pass1_result:
            combination = []
            korean = Korean(text)
            korean_len = len(korean)

            for i in range(0, korean_len):
                cur = korean[i]

                if not isinstance(cur, Korean.Syllable):
                    continue

                # ????????? ???????????? ?????????
                if not cur.phoneme_coda:
                    combination = join(combination, str(cur))
                    continue

                # ?????? ??????
                if 'raw_coda' in kwargs and kwargs['raw_coda']:
                    sound_coda = cur.phoneme_coda
                else:
                    if cur.phoneme_coda in CMUToKorean.korean_coda_sound:
                        sound_coda = CMUToKorean.korean_coda_sound[cur.phoneme_coda]
                    else:
                        sound_coda = cur.phoneme_coda

                sound_syllable = Korean.Syllable(phoneme_onset=cur.phoneme_onset,
                                                 phoneme_nucleus=cur.phoneme_nucleus,
                                                 phoneme_coda=sound_coda)

                # ???,???,???,???,??? ??? ???????????? ?????????
                if cur.phoneme_coda in ('???', '???', '???', '???', '???'):
                    syllable1 = Korean.Syllable(phoneme_onset=cur.phoneme_onset,
                                                phoneme_nucleus=cur.phoneme_nucleus,
                                                phoneme_coda=None)

                    syllable2 = Korean.Syllable(phoneme_onset=cur.phoneme_coda,
                                                phoneme_nucleus='???',
                                                phoneme_coda=None)

                    value = str(syllable1) + str(syllable2)
                else:
                    prolonged = False

                    while True:
                        # ??????????????? ???????????? ??????
                        if cur.phoneme_coda in ('???', '???', '???', '???'):
                            break

                        next = korean[i + 1] if i + 1 < korean_len else None
                        if next:
                            # ????????? ??????????????? ????????? ????????? ???????????? ??????
                            if cur.phoneme_coda == next.phoneme_onset:
                                break

                            # ????????? ??? ?????? ?????? ????????? ??? ?????? ???????????? ??????
                            elif cur.phoneme_coda == '???' and next.phoneme_onset == '???':
                                break

                            # ?????? ???????????? ????????? ????????? ??????
                            elif i == (korean_len - 2):
                                # ????????? ??? ?????? ?????????
                                if cur.phoneme_coda == '???':
                                    if next.phoneme_onset == '???' and next.phoneme_coda == '???':
                                        break

                                # ????????? ??? ?????? ???,??? ??????
                                if cur.phoneme_coda == '???':
                                    if next.phoneme_onset == '???' and next.phoneme_coda == '???':
                                        break

                                    if next.phoneme_onset == '???' and next.phoneme_coda == '???':
                                        break

                                # ????????? ??? ?????? ??? ??????
                                if cur.phoneme_coda == '???':
                                    if next.phoneme_onset == '???' and next.phoneme_coda == '???':
                                        break

                                # ????????? ??? ?????? ??? ??????
                                if cur.phoneme_coda == '???':
                                    if next.phoneme_onset == '???' and next.phoneme_coda == '???':
                                        break

                        prolonged = True
                        break

                    if prolonged:
                        syllable1 = Korean.Syllable(phoneme_onset=cur.phoneme_onset,
                                                    phoneme_nucleus=cur.phoneme_nucleus,
                                                    phoneme_coda=None)

                        syllable2 = Korean.Syllable(phoneme_onset=cur.phoneme_coda,
                                                    phoneme_nucleus='???',
                                                    phoneme_coda=None)

                        value = [str(sound_syllable), str(syllable1) + str(syllable2)]
                    else:
                        value = str(sound_syllable)

                """
                # middle.comment
                # 160127 ???????????? ??????

                # ???????????? ???????????? ?????????
                if i == 0:
                    value = unicode(sound_syllable)

                # ???????????????
                # elif i == (korean_len - 1):
                else:
                    # ???????????? ???????????? ?????? ??????
                    # ???,???,???,???,??? ??? ???????????? ?????????
                    # ???,???,???,??? ??? ????????? ???????????? ??????

                    if cur.phoneme_coda in (u'???', u'???', u'???', u'???', u'???'):
                        syllable1 = Korean.Syllable(phoneme_onset=cur.phoneme_onset,
                                                    phoneme_nucleus=cur.phoneme_nucleus,
                                                    phoneme_coda=None)

                        syllable2 = Korean.Syllable(phoneme_onset=cur.phoneme_coda,
                                                    phoneme_nucleus=u'???',
                                                    phoneme_coda=None)

                        value = unicode(syllable1) + unicode(syllable2)
                    elif cur.phoneme_coda in (u'???', u'???', u'???', u'???'):
                        value = unicode(sound_syllable)
                    else:
                        syllable1 = Korean.Syllable(phoneme_onset=cur.phoneme_onset,
                                                    phoneme_nucleus=cur.phoneme_nucleus,
                                                    phoneme_coda=None)

                        syllable2 = Korean.Syllable(phoneme_onset=cur.phoneme_coda,
                                                    phoneme_nucleus=u'???',
                                                    phoneme_coda=None)

                        value = [unicode(sound_syllable), unicode(syllable1) + unicode(syllable2)]
                """

                combination = join(combination, value)

            pass2_result.extend(combination)

        result = sorted(set(pass2_result))
        return result

    @staticmethod
    def _pattern_exception(map, group_index, combination):
        group_len = len(map)
        group = map[group_index]

        word = group[1]
        word_vowel_count = 0
        word_consonant_count = 0
        word_type = ''

        for c in word:
            if c in CMUToKorean.alphabet_vowel_set:
                word_vowel_count += 1
                word_type += 'V'
            elif c in CMUToKorean.alphabet_consonant_set:
                word_consonant_count += 1
                word_type += 'C'
            else:
                # ????????????
                word_type += 'S'

        phonetic_list = group[0]
        phonetic_vowel_count = 0
        phonetic_consonant_count = 0
        phonetic_type = ''

        for c in phonetic_list:
            m = re.match(r'(\D+)(\d)?([?])?', c)
            symbol = m.groups()[0]

            if symbol in CMUToKorean.vowel_to_korean_dict:
                phonetic_vowel_count += 1
                phonetic_type += 'V'
            elif symbol in CMUToKorean.semivowel_to_korean_dict:
                phonetic_vowel_count += 1
                phonetic_type += 'V'
            elif symbol in CMUToKorean.consonant_to_korean_dict:
                phonetic_consonant_count += 1
                phonetic_type += 'C'

            else:
                # ????????????
                phonetic_type += 'S'

        # ????????? ???????????? ?????????
        # word type ??? C+V+C+ ???????????? (COL)
        # phonetic type ??? C+ ???????????? (K L)
        if group_index < group_len - 1 \
                and re.search(r'^C+V+C+$', word_type) and re.search(r'^C+$', phonetic_type):
            # word ????????? ????????? phonetic ?????? ????????? ????????? ???????????????
            for i in range(0, len(word_type)):
                if word_type[i] == 'V':
                    group[0].insert(i, CMUToKorean.alphabet_vowel_to_cmu_dict[word[i]])

        # word ??? .+E ???????????? (DLE)
        # phonetic type ??? C+V+C+ ???????????? (D AH L)
        elif re.search(r'^.+E$', word) and re.search(r'^C+VC+$', phonetic_type):
            # op '?' ??? ????????????(????????????)
            for i in range(0, len(phonetic_type)):
                if phonetic_type[i] == 'V':
                    group[0][i] += '?'

            # op '/' ??? ????????????
            group[0].insert(0, '/')

        # word type ??? CC ???????????? (SM)
        # phonetic type ??? CVC ???????????? (ZH AH M)
        elif re.search(r'^CC$', word_type) and re.search(r'^CVC$', phonetic_type):
            # op '?' ??? ????????????(????????????)
            for i in range(0, len(phonetic_type)):
                if phonetic_type[i] == 'V':
                    group[0][i] += '?'

            # op '/' ??? ????????????
            group[0].insert(0, '/')

        # word ???????????? ??????
        if re.search(r'^.+-$', word):
            group[0].append('/')
        elif re.search(r'^-.+$', word):
            group[0].insert(0, '/')

        return False

    @staticmethod
    def _join_process(map, map_index, lhs, rhs):
        #print(lhs,rhs,map_index)
        if lhs and isinstance(lhs, list):
            build_list = []
            for lv in lhs:
                result = CMUToKorean._join_process(map, map_index, lv, rhs)
                if result:
                    if isinstance(result, list):
                        build_list.extend(result)
                    else:
                        build_list.append(result)

            return build_list

        elif rhs and isinstance(rhs, list):
            build_list = []
            for rv in rhs:
                result = CMUToKorean._join_process(map, map_index, lhs, rv)
                if result:
                    if isinstance(result, list):
                        build_list.extend(result)
                    else:
                        build_list.append(result)

            return build_list

        elif isinstance(rhs, str):
            if not lhs:
                lhs = ''

            if not rhs:
                rhs = ''

            return [lhs + rhs]
        elif isinstance(rhs, CMUToKorean.Control.IF):
            for statement in rhs.chain:
                if isinstance(statement, dict):
                    if isinstance(statement['condition'], CMUToKorean.Condition.Interface):
                        if statement['condition'].test(map, map_index, lhs):
                            return CMUToKorean._join_process(map, map_index, lhs, statement['value'])
                    else:
                        # middle.error
                        return None
                else:
                    return CMUToKorean._join_process(map, map_index, lhs, statement)

        return None

    @staticmethod
    def _phonetic_word_mapping(word, phonetic):
        # ????????? C ????????? V

        if not word:
            return None
        elif not phonetic:
            return None

        # middle.comment
        # word??? ????????? ??????????????? ?????? ??????

        word = str(word)
        word.upper()
        word_type_list = []

        for c in word:
            if c in CMUToKorean.alphabet_vowel_set:
                word_type_list.append([c, 'V'])
            elif c in CMUToKorean.alphabet_consonant_set:
                word_type_list.append([c, 'C'])
            else:
                # ????????????
                # ???????????? ??????
                word_type_list.append([c, 'C'])

        # middle.comment
        # CMU ???????????? ???????????? ?????? ??????

        phonetic = str(phonetic)
        phonetic.upper()
        phonetic_list = phonetic.split()
        phonetic_type_list = []

        for c in phonetic_list:
            m = re.match(r'(\D+)(\d)?([?])?', c)
            symbol = m.groups()[0]

            # ????????? ????????? (EX. AA1, AH0..) ???????????? ?????????
            if symbol in CMUToKorean.vowel_to_korean_dict:
                phonetic_type_list.append([c, 'V'])
            elif symbol in CMUToKorean.semivowel_to_korean_dict:
                phonetic_type_list.append([c, 'V'])
            elif symbol in CMUToKorean.consonant_to_korean_dict:
                phonetic_type_list.append([c, 'C'])
            else:
                # ????????????
                # ???????????? ??????
                phonetic_type_list.append([c, 'C'])

        result = []
        phonetic_index = 0
        phonetic_len = len(phonetic_type_list)
        word_index = 0
        word_len = len(word_type_list)

        while phonetic_index < phonetic_len:
            add_vowel_group = False
            add_consonant_group = False
            add_group_continue = False
            vowel_r = False
            phonetic = phonetic_type_list[phonetic_index][0]
            type = phonetic_type_list[phonetic_index][1]

            # phonetic group
            count = 1
            index = phonetic_index + 1

            # middle.comment
            # ????????? ???????????? ???????????? ?????????
            # ?????? ?????? ???????????? ??? ??? ??????
            if phonetic_index == 0 and type != word_type_list[index - 1][1]:
                if type == 'V':
                    # ex) CABOK  AE1 B OW0
                    add_consonant_group = True
                    add_group_continue = True
                else:
                    add_vowel_group = True
                    add_group_continue = True

                    # phonetic ??? ???????????? ??????
                    while index < phonetic_len:
                        value = phonetic_type_list[index]
                        if type != 'V':
                            break

                        index += 1
                        count += 1

                        # middle.comment
                        # ????????? phonetic ?????? ER??? ???????????? ??????????????? ????????????
                        if re.search(r'ER\d', value[0]):
                            add_group_continue = True
                            break

            # middle.comment
            # ????????? vowel phonetic ?????? ER??? ???????????? ??????????????? ????????????
            # ER ??? VC??? ???????????? ??????
            elif re.search(r'ER\d', phonetic):
                add_consonant_group = True

            else:
                while index < phonetic_len:
                    value = phonetic_type_list[index]
                    if type != value[1]:
                        break

                    index += 1
                    count += 1

                    # middle.comment
                    # ????????? vowel phonetic ?????? ER??? ???????????? ??????????????? ????????????
                    if re.search(r'ER\d', value[0]):
                        add_consonant_group = True
                        break

            group = [phonetic_list[phonetic_index:index], None]
            phonetic_index = index

            # middle.comment
            # ????????? phonetic ?????? C ???????????? ????????? ER ??????, ????????? 'R'??? ?????????
            # R??? ???????????? ????????????
            if type == 'C' and count == 1 and group[0][0] != 'R':
                if phonetic_index < phonetic_len and re.search(r'ER\d', phonetic_list[phonetic_index]):
                    vowel_r = True

            # middle.comment
            # ????????? phonetic ?????? CC+ ????????????
            # word??? ????????? CV ???????????? ??????????????? ?????? ????????????
            # (CVVCCC, CVCCC, ...??????)
            if type == 'C' and count >= 2:
                if word_index + 1 < word_len \
                        and word_type_list[word_index][1] == 'C' \
                        and word_type_list[word_index + 1][1] == 'V':
                        add_vowel_group = True
                        add_group_continue = True

            # word group
            token = ''
            index = word_index

            if phonetic_index >= phonetic_len:
                if word_len - word_index >= 1:
                    for value in word_type_list[word_index:word_len]:
                        token += value[0]

                word_index = word_len

            else:
                while index < word_len:
                    value = word_type_list[index]

                    if vowel_r and value[0] == 'R':
                        # R??? ???????????? ??????
                        vowel_r = False
                        value[1] = 'V'

                    if value[1] != type:

                        # ?????? ????????? ???????????????
                        if add_vowel_group:
                            while index < word_len:
                                value = word_type_list[index]
                                if value[1] != 'V':
                                    break

                                token += value[0]
                                index += 1

                            add_vowel_group = False

                            # ??????
                            if add_group_continue:
                                add_group_continue = False
                                continue
                            else:
                                break

                        # ?????? ????????? ???????????????
                        elif add_consonant_group:
                            while index < word_len:
                                value = word_type_list[index]
                                if value[1] != 'C':
                                    break

                                token += value[0]
                                index += 1

                            add_consonant_group = False

                            # ??????
                            if add_group_continue:
                                add_group_continue = False
                                continue
                            else:
                                break

                        else:
                            break

                    token += value[0]
                    index += 1

                word_index = index

                # word??? ?????? ????????? ????????? ?????? ???????????????
                if word_index >= word_len:
                    if phonetic_len - phonetic_index >= 1:
                        type = phonetic_type_list[phonetic_index][1]

                        # ?????? ?????? ????????? ????????? ???????????????
                        # ??????????????? ????????? ????????? ????????? ????????? merge ??????
                        if type == 'C' and len(result) > 0:
                            group[1] = token

                            for value in phonetic_type_list[phonetic_index:phonetic_len]:
                                group[0].append(value[0])

                            for c in group[1]:
                                if c in CMUToKorean.alphabet_consonant_set:
                                    result.append(group)
                                    return result

                            count = len(result)
                            for merge_group in reversed(result):

                                if not merge_group[1]:
                                    merge_group[0] += group[0]
                                    merge_group[1] = '' + group[1]
                                    result = result[0:count]
                                    return result

                                for c in merge_group[1]:
                                    if c in CMUToKorean.alphabet_consonant_set:
                                        merge_group[0] += group[0]
                                        merge_group[1] += group[1]
                                        result = result[0:count]
                                        return result

                                merge_group[0] += group[0]
                                merge_group[1] += group[1]
                                group = merge_group
                                count -= 1

                            return result

                        # ????????? ??????????????? ??????
                        else:
                            for value in phonetic_type_list[phonetic_index:phonetic_len]:
                                group[0].append(value[0])

                            phonetic_index = phonetic_len

            if token == '':
                token = None

            # middle.comment
            # ????????? ???????????? ???????????? word??? ?????? ????????????
            # ??? ???????????? ????????????
            if not token:
                if word_index != 0 and word_index < word_len:
                    group_index = len(result) - 1
                    prev_token = result[group_index][1]

                    if len(prev_token) > 1:
                        token = prev_token[-1:]
                        result[group_index][1] = prev_token[:-1]

            # middle.comment
            # ????????? ????????? ???????????? ????????????
            # word??? VC??? ?????? ???????????? ?????? ??????????????? ????????? ??????
            if not token:
                group[1] = ''
                count = len(result)

                for merge_group in reversed(result):
                    merge_group[0] += group[0]
                    merge_group[1] += group[1]
                    group = merge_group

                    exists_vowel = False
                    exists_consonant = False

                    for w in merge_group[1]:
                        if w in CMUToKorean.alphabet_vowel_set:
                            exists_vowel = True
                        elif w in CMUToKorean.alphabet_consonant_set:
                            exists_consonant = True
                        else:
                            # ????????????
                            # ???????????? ??????
                            exists_consonant = True

                    if exists_vowel and exists_consonant:
                        break

                    count -= 1

                count = 1 if count <= 0 else count
                result = result[0:count]

            else:
                group[1] = token
                result.append(group)

        return result

