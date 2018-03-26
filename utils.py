from functools import reduce
import os, time, re, numpy as np, random as rd, string, curses


_sumlist = lambda llist: reduce(lambda x, y: x + y, llist) if llist != [] else []
tokenizer = re.compile(r'(?u)\b[^(\W|\d|_)]{1,}\w*\b')
WHITESPACE_LIST = list(string.whitespace)
EPSILON = 10**-5


def start_screen():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()

    for i in range(0, curses.COLORS):
        curses.init_pair(i+1, i, -1)

    return stdscr


def exit_screen(stdscr):
    stdscr.getch()
    curses.echo()
    curses.nocbreak()
    curses.endwin()


def clean_text(decoded):

    try:
        decoded = decoded.lower()
        tokens = tokenizer.findall(decoded)
        cleaned = ' '.join(tokens)
        result = cleaned

    except ValueError:

        result = ''

    return result


def standard_alphabet():
    return list(string.ascii_lowercase)


def cipher_char(char, key):

    if char in key.keys():
        result = key[char]

    else:
        result = char

    return result


def apply_masc(plaintext, key):
    plainchars = list(plaintext)
    ciphertext = ''.join([cipher_char(pchar, key) for pchar in plainchars])
    return ciphertext


def homophonic_cipher_char(char, key):

    if char in key.keys():
        result = rd.choice(key[char])

    else:
        result = char

    return result


def apply_homophonic_masc(plaintext, key):
    plainchars = list(plaintext)
    ciphertext = ''.join([homophonic_cipher_char(pchar, key) for pchar in plainchars])
    return ciphertext


def simple_random_masc_key(alphabet, num):
    sample = rd.sample(alphabet, 2 * num)
    pairs = list(zip(sample[:num], sample[num:]))
    initial = dict(zip(alphabet, alphabet))
    result = {**initial}

    for pair in pairs:
        c1, c2 = pair
        result[c1] = initial[c2]
        result[c2] = initial[c1]

    return (result, pairs)


def random_derangement(n):

    while True:
        v = list(range(n))

        for j in range(n-1, -1, -1):
            p = rd.randint(0, j)

            if v[p] == j:
                break

            else:
                v[j], v[p] = v[p], v[j]
        else:

            if v[0] != 0:

                return tuple(v)


def random_masc_key(alphabet):
    cipher = list(np.random.permutation(alphabet))
    return {k: v for k, v in zip(alphabet, cipher)}


def identity_key(alphabet, alphabet2=None):

    if alphabet2 is None:
        alphabet2 = alphabet

    return {k: v for k, v in zip(alphabet, alphabet2)}


def alphagramify_word(word):
    return ''.join(sorted(word))


def alphagramify_text(text):
    words = text.split()
    return ' '.join([alphagramify_word(word) for word in words])


def anagramify_word(word):
    letters = [c for c in word]
    return ''.join(np.random.permutation(letters))


def anagramify_text(text):
    words = text.split()
    return ' '.join([anagramify_word(word) for word in words])


def get_word_bigram_counts(bigram_counts, alpha_to_idx, word):
    chars = list(word)
    char_pairs = zip(chars, chars[1:])

    for c1, c2 in char_pairs:
        idx_1 = alpha_to_idx[c1]
        idx_2 = alpha_to_idx[c2]
        bigram_counts[idx_1][idx_2] += 1.0


def get_text_bigram_counts(text, alphabet):
    alpha_to_idx = dict(zip(alphabet, range(len(alphabet))))
    bigram_counts = np.zeros((len(alphabet), len(alphabet)))
    words = text.split()

    for word in words:
        _get_word_bigram_counts(bigram_counts, alpha_to_idx, word)

    return bigram_counts


def get_text_bigram_freqs(text, alphabet):
    bigram_counts = _get_text_bigram_counts(text, alphabet)
    total = bigram_counts.sum(axis=1).sum(axis=0)
    return bigram_counts/total


def monogram_freqs(text, alphabet):
    counts = np.array([text.count(char) for char in alphabet])
    freqs = counts/counts.sum()
    return list(zip(alphabet, freqs))


def alphabet_from_text(text):
    alphabet = list([a for a in set(text) if a not in WHITESPACE_LIST])
    alphabet.sort()
    return alphabet


def word_bigram_counts(bigram_counts, alpha_to_idx, word):
    chars = list(word)
    char_pairs = zip(chars, chars[1:])

    for c1, c2 in char_pairs:
        idx_1 = alpha_to_idx[c1]
        idx_2 = alpha_to_idx[c2]
        bigram_counts[idx_1][idx_2] += 1.0


def array_l1_normalise(array):
    return array/array.sum(axis=None)


def text_bigram_counts(text, alpha_to_idx):
    length = len(alpha_to_idx)
    bigram_counts = np.zeros((length, length))
    words = text.split()

    for word in words:
        word_bigram_counts(bigram_counts, alpha_to_idx, word)

    return bigram_counts


def text_bigram_freqs(text, alpha_to_idx):
    bigram_counts = text_bigram_counts(text, alpha_to_idx)
    return array_l1_normalise(bigram_counts)


def conjugate_transposition(x, transposition):
    a, b = transposition
    y = np.copy(x)
    y[[a, b], :] = y[[b, a], :]
    y[:, [a, b]] = y[:, [b, a]]
    return y


def bigram_likelihood(observed_counts, ground_probs):
    observed_probs = observed_counts * ground_probs
    np.place(observed_probs, observed_probs==0, EPSILON)
    log_likelihood = np.log(observed_probs).sum(axis=None)
    return log_likelihood


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
