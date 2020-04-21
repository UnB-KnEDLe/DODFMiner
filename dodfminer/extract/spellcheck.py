"""Module created using Peter Novings code.
http://norvig.com/spell-correct.html
and UFMG word list:
https://homepages.dcc.ufmg.br/~camarao/cursos/pc/2016a/Lista-de-Palavras.txt
"""
import re
import tqdm
from collections import Counter

class SpellChecker:

    def __init__(self):
        """."""
        self.WORDS = Counter(self._words(open('data/dict_ptbr.txt').read()))

    def _words(self, text):
        return re.findall(r'\w+', text.lower())

    def _P(self, word):
        """Probability of `word`."""
        N = sum(self.WORDS.values())
        return self.WORDS[word] / N

    def text_correction(self, text):
        """."""
        fixed_text = ''
        fixes = 0
        text = text.split()
        for word in tqdm.tqdm(text):
            if len(word) > 1:
                correct_word = self.correction(word)
                fixed_text += correct_word
                if correct_word != word:
                    fixes += 1
            else:
                fixed_text += word
            fixed_text += ' '

        print(fixed_text)
        print(f"[SpellChecker] {fixes} palavras corrigidas")
        return fixed_text[:-1]

    def correction(self, word):
        """Most probable spelling correction for word."""
        return max(self._candidates(word), key=self._P)

    def _candidates(self, word):
        """Generate possible spelling corrections for word."""
        c1 = self._known([word]) or self._known(self._edits1(word))
        c2 = self._known(self._edits2(word)) or [word]
        return (c1 or c2)

    def _known(self, words):
        """Subset of `words` that appear in the dictionary of WORDS."""
        return set(w for w in words if w in self.WORDS)

    def _edits1(self, word):
        """All edits that are one edit away from `word`."""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def _edits2(self, word):
        """All edits that are two edits away from `word`."""
        return (e2 for e1 in self._edits1(word) for e2 in self._edits1(e1))
