#!/usr/bin/python3
# parolottero-languages
# Copyright (C) 2021-2022 Salvo "LtWorf" Tomaselli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

from sys import argv, exit
from math import log
from typing import NamedTuple, Iterable
from pathlib import Path
from zipfile import ZipFile


class Language(NamedTuple):
    letters: set[str]
    vowels: set[str]
    substitutions: set[tuple[str, str]]
    wordlist: Path
    name: str
    encoding: str = 'utf-8'


def readwords(language: Language):

    wordlist = 'dict' / language.wordlist

    if wordlist.name.endswith('.xpi'):
        z = ZipFile(wordlist, 'r')
        dicfiles = [i for i in z.filelist if i.filename.endswith('.dic')]
        assert len(dicfiles) == 1
        with z.open(dicfiles.pop(), 'r') as f:
            f.readline() # Skip first line
            for i in f:
                if b'/' in i:
                    i = i.split(b'/', 1)[0]
                yield i
    else:
        with open(wordlist, 'rb') as f:
            yield from f


def scan_language(language: Language) -> set[str]:
    '''
    Load a language, returns a set of playable words
    '''
    words = set()

    for binaryword in readwords(language):
        try:
            word = binaryword.decode(language.encoding)
        except Exception:
            print(f'Decoding error for word {binaryword!r}. Skipping')
            continue

        word = word.strip()

        if not word:
            # Empty word
            continue
        if word.upper() == word:
            # All uppercase word, probably not a real word
            continue

        word = word.lower()

        for find, replace in language.substitutions:
            word = word.replace(find, replace)

        if set(word).difference(language.letters):
            # unknown symbols in the word, skipping
            continue

        words.add(word)
    return words


def print_letterlist(ll: Iterable[tuple[str, int]], title: str):
    '''
    Pretty print a letter list
    '''
    print(title)
    print('=' * len(title))

    for letter, count in ll:
        print(f'{letter}: {count}')
    print()


def letter_frequency(words: Iterable[str]) -> list[tuple[str, int]]:
    '''
    Calculates the frequency of the letters in the
    given set of words
    '''
    frequency = {}

    for word in words:
        for letter in word:
            frequency[letter] = frequency.get(letter, 0) + 1

    freqs = [(k, v) for k, v in frequency.items()]
    freqs.sort(key=lambda x: x[1])
    return freqs


def letter_score(freqs: list[str]) -> list[tuple[str, int]]:
    '''
    Assigns scores for letters.

    More common letters are worth less points.

    Score is done on a log scale.
    '''
    score = 1.1
    r = []

    while len(freqs):
        letter = freqs.pop()
        points = 2 + score
        r.append((letter, round(log(points))))
        score *= 2
    return r


def gen_language(language: Language, dest: Path, wordlist: Path) -> None:
    '''
    Generates the language file data and writes it to
    dest
    '''
    print(f'Generating language file for {language.name}')
    words = scan_language(language)
    print(f'Language has {len(words)} words')
    frequencies = letter_frequency(words)

    print_letterlist(frequencies, 'Frequencies')

    scores = letter_score([i[0] for i in frequencies])

    print_letterlist(scores, 'Scores')

    with dest.open('wt') as f:
        print(language.name, file=f)
        for letter, score in scores:
            vowel = 'v' if letter in language.vowels else ''
            print(f'{letter} {score} {vowel}', file=f)
    with wordlist.open('wt') as f:
        for word in words:
            print(word, file=f)


languages = {
     'sicilian': Language(
        name='Sicilianu',
        letters=set('abcdefghilmnopqrstuvzj'),
        vowels=set('aeiou'),
        substitutions={
            ('??', 'a'),
            ('??', 'e'),
            ('??', 'i'),
            ('??', 'o'),
            ('??', 'u'),
        },
        wordlist=Path('sicilian'),
    ),
    'italian': Language(
        name='Italiano',
        letters=set('abcdefghilmnopqrstuvz'),
        vowels=set('aeiou'),
        substitutions={
            ('??', 'a'),
            ('??', 'e'),
            ('??', 'e'),
            ('??', 'i'),
            ('??', 'o'),
            ('??', 'u'),
        },
        wordlist=Path('italian'),
    ),
    'swedish': Language(
        name='Svenska',
        letters=set('abcdefghjkilmnopqrstuvwxyz??????'),
        vowels=set('aeiou??????'),
        substitutions=set(),
        wordlist=Path('swedish.xpi'),
    ),
    'american': Language(
        name='US English',
        letters=set('abcdefghilmnopqrstuvzwxyjk'),
        vowels=set('aeiou'),
        substitutions=set(),
        wordlist=Path('american.xpi'),
        encoding='iso-8859-15',
    ),
    'english': Language(
        name='English',
        letters=set('abcdefghilmnopqrstuvzwxyjk'),
        vowels=set('aeiou'),
        substitutions=set(),
        wordlist=Path('english.xpi'),
    ),
}


def help(retcode: int, msg: str) -> None:
    if msg:
        print(msg)
    print(f'Usage: {argv[0]} language destfile wordlistfile\n')
    print('Known languages are:\n' + '\n'.join(languages.keys()))
    exit(retcode)


def main() -> None:
    if len(argv) >= 2 and argv[1] in ('-h', '--help'):
        help(0, '')

    if len(argv) != 4:
        help(1, 'Incorrect number of parameters')

    try:
        language = languages[argv[1]]
    except KeyError:
        help(1, 'Unknown language')

    try:
        gen_language(language, Path(argv[2]), Path(argv[3]))
    except Exception as e:
        help(1, str(e))


if __name__ == '__main__':
    main()
