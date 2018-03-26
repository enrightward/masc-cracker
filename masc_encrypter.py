from utils import apply_masc, apply_homophonic_masc, anagramify_text, _sumlist


class MASCEncrypter(object):

    def __init__(self, encryption_key, anagram=False):
        self.anagram = anagram
        self.encryption_key = encryption_key
        self.decryption_key = {v: k for k, v in encryption_key.items()}

    def encrypt(self, plaintext):
        ciphertext = apply_masc(plaintext, self.encryption_key)

        if self.anagram:
            ciphertext = anagramify_text(ciphertext)

        return ciphertext

    def decrypt(self, ciphertext):
        plaintext = apply_masc(ciphertext, self.decryption_key)
        return plaintext


class MASCHomophonicEncrypter(object):

    def __init__(self, encryption_key, anagram=False):
        self.anagram = anagram
        self.encryption_key = encryption_key
        self.decryption_key = dict(_sumlist([[(c, a) for c in clist] for a, clist in encryption_key.items()]))

    def encrypt(self, plaintext):
        ciphertext = apply_homophonic_masc(plaintext, self.encryption_key)

        if self.anagram:
            ciphertext = anagramify_text(ciphertext)

        return ciphertext

    def decrypt(self, ciphertext):
        plaintext = apply_masc(ciphertext, self.decryption_key)
        return plaintext
