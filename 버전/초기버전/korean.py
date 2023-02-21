# -*- coding: utf-8 -*-
import abc
import sys
import copy
import collections
import re
import imp

imp.reload(sys)
#sys.setdefaultencoding('utf-8')


class Korean(object):
    unicode_base_code, unicode_onset_offset, unicode_nucleus_offset = 44032, 588, 28

    # 초성(19)
    phoneme_onset_list = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ',
        'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ',
        'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ',
        'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ',
        'ㅌ', 'ㅍ', 'ㅎ']

    phoneme_onset_list_len = len(phoneme_onset_list)
    phoneme_onset_dict = {v: i for i, v in enumerate(phoneme_onset_list)}

    # 중성(21)
    phoneme_nucleus_list = [
        'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ',
        'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ',
        'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ',
        'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ',
        'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
        'ㅣ']

    phoneme_nucleus_list_len = len(phoneme_nucleus_list)
    phoneme_nucleus_dict = {v: i for i, v in enumerate(phoneme_nucleus_list)}

    # 종성(28)
    phoneme_coda_list = [
        ' ', 'ㄱ', 'ㄲ', 'ㄳ',
        'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ',
        'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ',
        'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
        'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
        'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ',
        'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    phoneme_coda_list_len = len(phoneme_coda_list)
    phoneme_coda_dict = {v: i for i, v in enumerate(phoneme_coda_list)}

    # 쌍자음/된소리
    phoneme_double_consonant_dict = {
        'ㄲ': ['ㄱ', 'ㄱ'], 'ㄳ': ['ㄱ', 'ㅅ'],
        'ㄵ': ['ㄴ', 'ㅈ'], 'ㄶ': ['ㄴ', 'ㅎ'],
        'ㄸ': ['ㄷ', 'ㄷ'],
        'ㄺ': ['ㄹ', 'ㄱ'], 'ㄻ': ['ㄹ', 'ㅁ'],
        'ㄼ': ['ㄹ', 'ㅂ'], 'ㄽ': ['ㄹ', 'ㅅ'],
        'ㄾ': ['ㄹ', 'ㅌ'], 'ㄿ': ['ㄹ', 'ㅍ'], 'ㅀ': ['ㄹ', 'ㅎ'],
        'ㅃ': ['ㅂ', 'ㅂ'], 'ㅄ': ['ㅂ', 'ㅅ'],
        'ㅆ': ['ㅅ', 'ㅅ'],
        'ㅉ': ['ㅈ', 'ㅈ']
    }

    phoneme_lenis_to_fortis_dict = {
        'ㄱ': 'ㄲ',
        'ㄷ': 'ㄸ',
        'ㅂ': 'ㅃ',
        'ㅅ': 'ㅆ',
        'ㅈ': 'ㅉ'
    }

    phoneme_lenis_to_asprite_dict = {
        'ㄱ': 'ㅋ',
        'ㄷ': 'ㅌ',
        'ㅂ': 'ㅍ',
        'ㅈ': 'ㅊ'
    }

    # 중성 발음 합성
    phoneme_nucleus_phonetic_combine_dict = {
        'ㅣㅏ': 'ㅑ',
        'ㅣㅓ': 'ㅕ',
        'ㅣㅐ': 'ㅒ',
        'ㅣㅔ': 'ㅖ',
        'ㅣㅜ': 'ㅠ',
        'ㅣㅗ': 'ㅛ',
        'ㅡㅣ': 'ㅢ',
        'ㅜㅣ': 'ㅟ',
        'ㅜㅏ': 'ㅘ',
        'ㅜㅓ': 'ㅝ',
        'ㅜㅐ': 'ㅙ',
        'ㅜㅔ': 'ㅞ',
        'ㅗㅣ': 'ㅚ',
        'ㅗㅏ': 'ㅘ',
        'ㅗㅓ': 'ㅝ',
        'ㅗㅐ': 'ㅙ',
        'ㅗㅔ': 'ㅞ'
    }

    # 중성 합성
    phoneme_nucleus_combine_dict = {
        'ㅡ+ㅣ': 'ㅢ',
        'ㅜ+ㅣ': 'ㅟ',
        'ㅜ+ㅓ': 'ㅝ',
        'ㅜ+ㅔ': 'ㅞ',
        'ㅗ+ㅣ': 'ㅚ',
        'ㅗ+ㅏ': 'ㅘ',
        'ㅗ+ㅐ': 'ㅙ',
    }

    # 문자셋
    phoneme_set = set(phoneme_onset_list + phoneme_nucleus_list + phoneme_coda_list)

    text = None
    character_list = None

    # Exceptions
    class TypeErrorException(Exception):
        pass

    class SyllableFailedException(Exception):
        pass

    # Filters
    class Filter(object, metaclass=abc.ABCMeta):
        def pre(self, sequence):
            pass

        def post(self, sequence):
            pass

        @abc.abstractmethod
        def do(self, sequence, character, index):
            pass

    # Syllable
    class Syllable(object):
        letter = None
        phoneme_onset = None
        phoneme_nucleus = None
        phoneme_coda = None

        def __init__(self, **kwargs):
            letter = kwargs.get('letter', None)
            phoneme_onset = kwargs.get('phoneme_onset', None)
            phoneme_nucleus = kwargs.get('phoneme_nucleus', None)
            phoneme_coda = kwargs.get('phoneme_coda', None)

            # nuclues combine
            if isinstance(phoneme_nucleus, str):
                phoneme_nucleus = str(phoneme_nucleus)

                # nuclues combine
                if re.search(r'.\+.', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

                # nuclues phonetic combine
                elif re.search(r'..', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_phonetic_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_phonetic_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

            if kwargs.get('check', True):
                if letter != None:
                    if not isinstance(letter, str):
                        raise Korean.SyllableFailedException()

                    letter = letter if isinstance(letter, str) else str(letter)
                    if len(letter) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean(letter, include_phoneme=False):
                        raise Korean.SyllableFailedException()

                if phoneme_onset != None:
                    if not isinstance(phoneme_onset, str):
                        raise Korean.SyllableFailedException()

                    phoneme_onset = phoneme_onset \
                        if isinstance(phoneme_onset, str) else str(phoneme_onset)
                    if len(phoneme_onset) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean_phoneme(phoneme_onset):
                        raise Korean.SyllableFailedException()

                if phoneme_nucleus != None:
                    if not isinstance(phoneme_nucleus, str):
                        raise Korean.SyllableFailedException()

                    phoneme_nucleus = phoneme_nucleus \
                        if isinstance(phoneme_nucleus, str) else str(phoneme_nucleus)
                    if len(phoneme_nucleus) != 1:
                        raise Korean.SyllableFailedException()

                    if not Korean.is_korean_phoneme(phoneme_nucleus):
                        raise Korean.SyllableFailedException()

                if phoneme_coda != None:
                    if not isinstance(phoneme_coda, str):
                        raise Korean.SyllableFailedException()

                    phoneme_coda = phoneme_coda \
                        if isinstance(phoneme_coda, str) else str(phoneme_coda)
                    if len(phoneme_coda) != 1:
                        raise Korean.SyllableFailedException()

                    # space include
                    if not Korean.is_korean_phoneme(phoneme_coda, include_space=True):
                        raise Korean.SyllableFailedException()

            self.letter = letter
            self.phoneme_onset = phoneme_onset if phoneme_onset != '' else None
            self.phoneme_nucleus = phoneme_nucleus if phoneme_nucleus != '' else None
            self.phoneme_coda = phoneme_coda if phoneme_coda != '' else None

            if self.phoneme_onset or self.phoneme_nucleus or self.phoneme_coda:
                self.combine()
            else:
                self.decompose()

        def __deepcopy__(self, memo):
            return Korean.Syllable(letter=self.letter)

        def __str__(self):
            return str(self.letter)

        def __unicode__(self):
            return str(self.letter)

        def combine(self):
            phoneme_onset = self.phoneme_onset if self.phoneme_onset != ' ' else 'ㅇ'
            phoneme_nucleus = self.phoneme_nucleus if self.phoneme_nucleus != ' ' else None
            phoneme_coda = self.phoneme_coda

            # nuclues combine
            if isinstance(phoneme_nucleus, str):
                phoneme_nucleus = str(phoneme_nucleus)

                # nuclues combine
                if re.search(r'.\+.', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

                # nuclues phonetic combine
                elif re.search(r'..', phoneme_nucleus):
                    if phoneme_nucleus in Korean.phoneme_nucleus_phonetic_combine_dict:
                        phoneme_nucleus = Korean.phoneme_nucleus_phonetic_combine_dict[phoneme_nucleus]
                    else:
                        raise Korean.SyllableFailedException()

            if self.letter != None:
                self.decompose()
                phoneme_onset = phoneme_onset if phoneme_onset != None else self.phoneme_onset  #
                phoneme_nucleus = phoneme_nucleus if phoneme_nucleus != None else self.phoneme_nucleus  #
                phoneme_coda = phoneme_coda if phoneme_coda != None else self.phoneme_coda

            # phoneme only exists
            elif phoneme_onset is None or phoneme_nucleus is None:

                    if phoneme_onset:
                        if phoneme_coda is None or phoneme_coda == ' ':
                            # onset only
                            self.letter = phoneme_onset
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return
                        else:
                            # onset + coda
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return

                    elif phoneme_nucleus:
                        if phoneme_coda is None or phoneme_coda == ' ':
                            # nucleus only
                            self.letter = phoneme_nucleus
                            if self.letter is None:
                                raise Korean.SyllableFailedException()
                            return
                        else:
                            # nucleus + coda
                            phoneme_onset = 'ㅇ'

            try:
                # if exists only onset
                if phoneme_onset and not phoneme_nucleus and not phoneme_coda:
                    self.letter = phoneme_onset

                else:
                    onset_index = Korean.phoneme_onset_dict[phoneme_onset]
                    nucleus_index = Korean.phoneme_nucleus_dict[phoneme_nucleus]
                    coda_index = Korean.phoneme_coda_dict[phoneme_coda] if phoneme_coda != None else 0

                    nucleus_size = Korean.phoneme_nucleus_list_len
                    coda_size = Korean.phoneme_coda_list_len

                    code = (onset_index * nucleus_size * coda_size) + (nucleus_index * coda_size) + coda_index
                    self.letter = chr(code + Korean.unicode_base_code)

            except KeyError:
                raise Korean.SyllableFailedException()

            self.phoneme_onset = phoneme_onset
            self.phoneme_nucleus = phoneme_nucleus
            self.phoneme_coda = phoneme_coda

            if self.phoneme_coda == ' ':
                self.phoneme_coda = None

        def decompose(self):
            if self.letter is None and self.letter == ' ':
                raise Korean.SyllableFailedException()

            self.phoneme_onset = None
            self.phoneme_nucleus = None
            self.phoneme_coda = None

            base_code = ord(self.letter) - Korean.unicode_base_code

            if base_code < 0:
                if self.letter in Korean.phoneme_onset_dict:
                    self.phoneme_onset = self.letter
                    return
                elif self.letter in Korean.phoneme_nucleus_dict:
                    self.phoneme_nucleus = self.letter
                    return
                elif self.letter in Korean.phoneme_coda_dict:
                    self.phoneme_coda = self.letter
                    return
                else:
                    raise Korean.SyllableFailedException()

            c1 = int(base_code / Korean.unicode_onset_offset)
            self.phoneme_onset = Korean.phoneme_onset_list[c1]

            c2 = int((base_code - (Korean.unicode_onset_offset * c1)) / Korean.unicode_nucleus_offset)
            self.phoneme_nucleus = Korean.phoneme_nucleus_list[int(c2)]
            c3 = int((base_code - (Korean.unicode_onset_offset * c1) - (Korean.unicode_nucleus_offset * c2)))

            self.phoneme_coda = Korean.phoneme_coda_list[int(c3)]

            # blank check
            if self.phoneme_coda == ' ':
                self.phoneme_coda = None

        def is_completed(self):
            if not self.phoneme_onset:
                return False

            return self.phoneme_nucleus

        def has_double_onset(self):
            if not self.phoneme_onset:
                return False

            return self.phoneme_onset in Korean.phoneme_double_consonant_dict

        def has_double_coda(self):
            if not self.phoneme_coda:
                return False

            return self.phoneme_coda in Korean.phoneme_double_consonant_dict

    def __init__(self, text):
        if isinstance(text, str):
            self.text = str(text)
        elif isinstance(text, str):
            self.text = text
        else:
            raise Korean.TypeErrorException()

        self.parse()

    def __getitem__(self, key):
        return self.character_list[key]

    def __iter__(self):
        for x in self.character_list:
            yield x

    def __len__(self):
        return len(self.character_list)

    def __str__(self):
        return str(self.text)

    def __unicode__(self):
        return str(self.text)

    def parse(self):
        if isinstance(self.text, str):
            self.text = str(self.text)

        self.character_list = []

        for i in self.text:
            if Korean.is_korean(i, include_space=False):
                self.character_list.append(Korean.Syllable(letter=i, check=False))
            else:
                self.character_list.append(i)

        return self.character_list

    def join(self):
        self.text = ''

        for character in self.character_list:
            self.text += str(character)

        if not self.text:
            self.text = None

    def _tokenization(self, **kwargs):
        clone = kwargs.get('clone', False)
        token_list = []
        token = []

        for character in self.character_list:
            if isinstance(character, Korean.Syllable):
                token.append(copy.deepcopy(character) if clone else character)
            else:
                token_list.append(token)
                token = []

        if token:
            token_list.append(token)

        return token_list

    @staticmethod
    def transform(sequence, filters):
        if isinstance(sequence, str):
            sequence = Korean(sequence)

        if not hasattr(sequence, '__iter__') and not isinstance(sequence, collections.Sequence):
            return None

        if not filters:
            return None

        if not isinstance(filters, list):
            filters = [filters]

        # pre
        for filter in filters:
            if isinstance(filter, Korean.Filter):
                filter.pre(sequence=sequence)

        index = 0
        for c in sequence:
            for filter in filters:
                if isinstance(filter, Korean.Filter):
                    filter.do(sequence=sequence, character=c, index=index)
                elif hasattr(filter, '__call__'):
                    list(filter(sequence=sequence, character=c, index=index))

            index += 1

        # post
        for filter in filters:
            if isinstance(filter, Korean.Filter):
                filter.post(sequence=sequence)

        # combine
        if isinstance(sequence, Korean):
            sequence.join()

        return sequence

    @staticmethod
    def is_korean(text, **kwargs):
        src = text
        include_legacy = kwargs.get('include_legacy', False)
        include_space = kwargs.get('include_space', False)
        include_phoneme = kwargs.get('include_phoneme', True)

        if not isinstance(text, str):
            src = str(text)

        range_syllable_max = 0xD7AF if include_legacy else 0xD7A3
        range_phoneme_max = 0x3131 if include_legacy else 0x3163

        for i in src:
            if i == ' ':
                if include_space:
                    continue
                else:
                    return False

            value = ord(i)

            # syllable range(AC00~D7AF)
            if 0xAC00 <= value <= range_syllable_max:
                pass
            # phoneme range(3131~318E)
            elif include_phoneme and 0x3131 <= value <= range_phoneme_max:
                pass
            # != korean
            else:
                return False

        return True

    @staticmethod
    def is_korean_phoneme(text, **kwargs):
        src = text
        include_legacy = kwargs.get('include_legacy', False)
        include_space = kwargs.get('include_space', False)

        if not isinstance(text, str):
            src = str(text)

        range_phoneme_max = 0x3131 if include_legacy else 0x3163

        for i in src:
            if i == ' ':
                if include_space:
                    continue
                else:
                    return False

            value = ord(i)

            # phoneme range(3131~318E)
            if 0x3131 <= value <= range_phoneme_max:
                pass
            # != phoneme
            else:
                return False

        return True


