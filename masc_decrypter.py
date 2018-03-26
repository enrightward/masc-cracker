import random as rd, numpy as np, string, curses, time, itertools
from functools import reduce
from utils import apply_masc, identity_key, monogram_freqs
from utils import alphabet_from_text, WHITESPACE_LIST
from utils import text_bigram_counts, text_bigram_freqs, bigram_likelihood
from utils import conjugate_transposition, array_l1_normalise, start_screen, exit_screen
from utils import random_homophonic_masc_encryption_key, _sumlist
from colour_print import hmap_display_bigrams, rgb_heatmap, print_block

CHAR_LIMIT = 100
NUM_COLOURS = 50
HMAP = rgb_heatmap(NUM_COLOURS)

#_sumlist = lambda llst: reduce(lambda x, y: x + y, llst) if llst != [] else []

class MASCDecrypter(object):

    def __init__(self, ciphertext, traintext,
                 plaintext_alphabet=None,
                 ciphertext_alphabet=None):
        self.traintext = traintext
        self.ciphertext = ciphertext

        if plaintext_alphabet:
            self.plaintext_alphabet = plaintext_alphabet

        else:
            self.plaintext_alphabet = alphabet_from_text(traintext)

        if ciphertext_alphabet:
            self.ciphertext_alphabet = ciphertext_alphabet

        else:
            self.ciphertext_alphabet = alphabet_from_text(ciphertext)

        self.encryption_key = identity_key(self.plaintext_alphabet, self.ciphertext_alphabet)
        self.decryption_key = {**self.encryption_key}
        self.deciphered_text = self.ciphertext

    def train(self):
        train_mono_freqs = monogram_freqs(self.traintext, self.plaintext_alphabet)
        cipher_mono_freqs = monogram_freqs(self.ciphertext, self.ciphertext_alphabet)
        train_mono_freqs.sort(key=lambda x: x[1], reverse=True)
        cipher_mono_freqs.sort(key=lambda x: x[1], reverse=True)
        keys, _ = zip(*train_mono_freqs)
        vals, _ = zip(*cipher_mono_freqs)
        self.encryption_key = {k: v for k, v in zip(keys, vals)}
        self.decryption_key = {v: k for k, v in zip(keys, vals)}
        self.deciphered_text = apply_masc(self.ciphertext, self.decryption_key)

    def encrypt(self, plaintext):
        ciphertext = apply_masc(plaintext, self.encryption_key)
        return ciphertext

    def decrypt(self, ciphertext):
        plaintext = apply_masc(ciphertext, self.decryption_key)
        return plaintext


class MASCBigramDecrypter(MASCDecrypter):

    def __init__(self, ciphertext, traintext,
                 plaintext_alphabet=None,
                 ciphertext_alphabet=None):

        super().__init__(ciphertext, traintext, plaintext_alphabet, ciphertext_alphabet)
        idxs = range(len(self.ciphertext_alphabet))
        self.alpha_to_idx = dict(zip(self.ciphertext_alphabet, idxs))
        self.idx_to_alpha = {v: k for k, v in self.alpha_to_idx.items()}
        self.training_bigram_freqs = text_bigram_freqs(self.traintext, self.alpha_to_idx)

    def select_transposition(self):
        idxs = range(len(self.ciphertext_alphabet))
        return tuple(rd.sample(idxs, 2))

    def is_improvement(self, transposition):
        self.trial_ciphertext_bigram_counts = conjugate_transposition(np.copy(self.ciphertext_bigram_counts), transposition)
        self.trial_ciphertext_likelihood = bigram_likelihood(self.trial_ciphertext_bigram_counts, self.training_bigram_freqs)
        return (self.trial_ciphertext_likelihood > self.ciphertext_likelihood)

    def update(self, transposition):
        a, b = transposition
        c, d = self.idx_to_alpha[a], self.idx_to_alpha[b]
        self.ciphertext_likelihood = self.trial_ciphertext_likelihood
        self.ciphertext_bigram_counts = self.trial_ciphertext_bigram_counts
        self.ciphertext_bigram_freqs = array_l1_normalise(self.ciphertext_bigram_counts)
        dct = self.encryption_key
        dct[c], dct[d] = dct[d], dct[c]
        self.decryption_key = {v: k for k, v in self.encryption_key.items()}

    def print_progress(self, transposition, i, stdscr):
        a, b = transposition
        c, d = self.idx_to_alpha[a], self.idx_to_alpha[b]
        self.deciphered_text = apply_masc(self.ciphertext, self.decryption_key)
        line1 = '%i: deciphered_text_likelihood = %f' % (i, self.ciphertext_likelihood)
        line2 = 'transposition = (%s, %s)' % (c, d)
        line3 = 'deciphered text:'
        line4 = self.deciphered_text[:CHAR_LIMIT]
        freq_diff = np.abs(self.training_bigram_freqs - self.ciphertext_bigram_freqs)
        hmap_bigrams = hmap_display_bigrams(freq_diff, HMAP, self.idx_to_alpha)
        lines = [line1, line2, line3, line4]
        blanks = [''] * len(lines)
        lines = list(itertools.chain(*zip(lines, blanks))) + hmap_bigrams
        print_block(lines, stdscr)
        time.sleep(0.02)

    def train(self, iterations, verbose, mode):

        if mode in ['monogram', 'both']:
            super().train()

        if mode in ['bigram', 'both']:
            self.ciphertext_bigram_counts = text_bigram_counts(self.deciphered_text, self.alpha_to_idx)
            self.ciphertext_bigram_freqs = array_l1_normalise(self.ciphertext_bigram_counts)
            self.ciphertext_likelihood = bigram_likelihood(self.ciphertext_bigram_counts, self.training_bigram_freqs)

            for i in range(iterations):
                transposition = self.select_transposition()

                if self.is_improvement(transposition):
                    self.update(transposition)

                    if verbose:
                        stdscr = start_screen()
                        self.print_progress(transposition, i, stdscr)

        if verbose:
            exit_screen(stdscr)

        self.deciphered_text = apply_masc(self.ciphertext, self.decryption_key)


"""
def random_homophonic_masc_encryption_key(plaintext_alphabet, ciphertext_alphabet):
    #The ciphertext alphabet cannot be smaller than the plaintext alphabet.
    plain_len, cipher_len = len(plaintext_alphabet), len(ciphertext_alphabet)
    assert(cipher_len >= plain_len)
    injective_image = rd.sample(ciphertext_alphabet, plain_len)
    injective_part = [(a, injective_image[i]) for i, a in enumerate(plaintext_alphabet)]
    non_image = [c for c in ciphertext_alphabet if c not in injective_image]
    non_injective_part = [(rd.choice(plaintext_alphabet), c) for c in non_image]
    encryption_key = injective_part + non_injective_part
    encryption_key.sort(key=lambda x: x[0])
    decryption_key = dict([(b, a) for a, b in encryption_key])
    encryption_key = dict([(x, [b for a, b in encryption_key if a == x]) for x in plaintext_alphabet])
    return (encryption_key, decryption_key)
"""

class HomophonicMASCDecrypter(MASCDecrypter):

    def __init__(self, ciphertext, traintext,
                 plaintext_alphabet=None,
                 ciphertext_alphabet=None):

        super().__init__(ciphertext, traintext, plaintext_alphabet, ciphertext_alphabet)
        plain_idxs = range(len(self.plaintext_alphabet))
        cipher_idxs = range(len(self.ciphertext_alphabet))
        self.plain_alpha_to_idx = dict(zip(self.plaintext_alphabet, plain_idxs))
        self.plain_idx_to_alpha = {v: k for k, v in self.plain_alpha_to_idx.items()}
        self.cipher_alpha_to_idx = dict(zip(self.ciphertext_alphabet, cipher_idxs))
        self.cipher_idx_to_alpha = {v: k for k, v in self.cipher_alpha_to_idx.items()}
        self.training_bigram_freqs = text_bigram_freqs(self.traintext, self.plain_alpha_to_idx)
        self.ciphertext_bigram_counts = text_bigram_counts(self.ciphertext, self.cipher_alpha_to_idx)

        self.encryption_key, self.decryption_key = random_homophonic_masc_encryption_key(self.plaintext_alphabet,
                                                                    self.ciphertext_alphabet)
        self.trial_encryption_key = {**self.encryption_key}

    def create_conjugators(self):
        basis = np.identity(len(self.ciphertext_alphabet))
        data = [sum([basis[self.cipher_alpha_to_idx[c]] for c in self.trial_encryption_key[a]]) for a in self.plaintext_alphabet]
        left_conjugator = np.array(data)
        right_conjugator = left_conjugator.transpose()
        return (left_conjugator, right_conjugator)

    def compute_deciphered_text_bigram_counts(self):
        left_conjugator, right_conjugator = self.create_conjugators()
        return left_conjugator.dot(self.ciphertext_bigram_counts.dot(right_conjugator))

    def is_improvement(self):
        self.trial_deciphered_text_bigram_counts = self.compute_deciphered_text_bigram_counts()
        self.trial_deciphered_text_likelihood = bigram_likelihood(self.trial_deciphered_text_bigram_counts, self.training_bigram_freqs)
        return (self.trial_deciphered_text_likelihood > self.deciphered_text_likelihood)

    def update(self):
        self.encryption_key = self.trial_encryption_key
        self.decryption_key = dict(_sumlist([[(w, k) for w in v] for k, v in self.encryption_key.items()]))
        self.deciphered_text_likelihood = self.trial_deciphered_text_likelihood
        self.deciphered_text_bigram_counts = self.trial_deciphered_text_bigram_counts
        self.deciphered_text_bigram_freqs = array_l1_normalise(self.deciphered_text_bigram_counts)

    def swap_letters(self, one_to_one):
        # Exchange two plaintext characters each having exactly one ciphertext character
        # in the preimage w.r.t. current encryption key.
        chars = rd.sample(one_to_one, 2)
        a, b = chars
        dct = self.trial_encryption_key
        dct[a], dct[b] = dct[b], dct[a]

    def move_letters(self, one_to_multi):
        # Choose random plaintext char 'a' and ciphertext char 'c' s.t. 'c' in im(a).
        a = rd.choice(one_to_multi)
        c = rd.choice(self.trial_encryption_key[a])
        # Remove 'c' from im(a) and assign to im(b), with b != a.
        self.trial_encryption_key[a] = [d for d in self.trial_encryption_key[a] if d != c]
        b = rd.choice([k for k, v in self.trial_encryption_key.items() if k != a])
        self.trial_encryption_key[b] = self.trial_encryption_key[b] + [c]

    def modify_encryption_key(self):
        one_to_one = [k for k, v in self.encryption_key.items() if len(v) == 1]
        one_to_multi = [k for k, v in self.encryption_key.items() if len(v) > 1]
        self.trial_encryption_key = {**self.encryption_key}

        if len(one_to_one) > 1 and len(one_to_multi) > 0:

            if rd.random() > 0.5:
                self.swap_letters(one_to_one)

            else:
                self.move_letters(one_to_multi)

        if len(one_to_one) <= 1:
            self.move_letters(one_to_multi)

        if len(one_to_multi) == 0:
            self.swap_letters(one_to_one)

    def print_progress(self, i, stdscr):
        self.deciphered_text = apply_masc(self.ciphertext, self.decryption_key)
        line1 = '%i: deciphered_text_likelihood = %f' % (i, self.deciphered_text_likelihood)
        line2 = 'deciphered text:'
        line3 = self.deciphered_text[:CHAR_LIMIT]
        #"""
        freq_diff = np.abs(self.training_bigram_freqs - self.deciphered_text_bigram_freqs)
        hmap_bigrams = hmap_display_bigrams(freq_diff, HMAP, self.plain_idx_to_alpha)
        #"""
        lines = [line1, line2, line3]
        blanks = [''] * len(lines)
        lines = list(itertools.chain(*zip(lines, blanks))) + hmap_bigrams
        print_block(lines, stdscr)
        time.sleep(0.002)

    def train(self, iterations, verbose):
        self.deciphered_text_bigram_counts = self.compute_deciphered_text_bigram_counts()
        self.deciphered_text_bigram_freqs = array_l1_normalise(self.deciphered_text_bigram_counts)
        self.deciphered_text_likelihood = bigram_likelihood(self.deciphered_text_bigram_counts, self.training_bigram_freqs)

        for i in range(iterations):
            self.modify_encryption_key()

            if self.is_improvement():
                self.update()

                if verbose:
                    stdscr = start_screen()
                    self.print_progress(i, stdscr)

        if verbose:
            exit_screen(stdscr)

        self.deciphered_text = apply_masc(self.ciphertext, self.decryption_key)
