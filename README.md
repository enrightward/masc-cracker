# masc-cracker

## 1. Outline

This repo contains python 3 code for making and breaking monoalphabetic substitution ciphers (MASCs). The decryption algorithm makes two simplifying assumptions:

**(i)** Spaces are preserved in the ciphertext.

**(ii)** The language of the underlying plaintext message is known.

This code does three things:

**(i)** Key generation, handled by `generate_key`.

**(ii)** Encryption of plaintext into ciphertext, using a key, handled by the `masc_encrypter` script.

**(iii)** Attempt decryption of cipher- into plaintext, given the ciphertext and a training sample of plaintext from the same language as the underlying message, handled by the `masc_decrypter` script.

This repo also contains example plaintext files in several languages, in the `./docs` subdirectory. There are two files per language represented, so that one can be used as a plaintext to be encrypted, and the other as a training text from which the alphabet and character frequencies of the language are inferred, to aid decrpytion, with no knowledge of the plaintext message or encryption key. Typing e.g. 

```
./dropin.py french
```

will copy-paste the two french language files contained in `./docs` into the PWD as `plain_text.txt` and `train_text.txt`.

## 2. Usage

You can interact with the code using the three scripts `generate_key`, `masc_encrypter` and `masc_decrypter`. Each is documented. There are several possibilities:

**1.** (Quickest) The script `demo.sh` takes an argument `plain_text.txt` to be encrypted, encrypts it as `cipher_text.txt` with a randomly generated key, then uses the character frequency statistics contained in the text of a second argument, `train_text.txt`, to try and decrypt `cipher_text.txt`, without knowledge of either `plain_text.txt` or the key.

The `demo.sh` script works out of the box, provided the PWD contains two plaintext files: `plain_text.txt` and `train_text.txt`, both written in the same language. The `./docs` subdirectory contains examples of such files, in `(plain, train)` pairs, in several languages. As explained above, you can type e.g. 

```
./dropin.py french
```

to copy-paste the two french language files contained in `./docs` into the PWD as `plain_text.txt` and `train_text.txt`.

**2.** If you already have MASC-encrypted text, you can attempt to crack immediately using the `masc_decrypter` script.

**3.** If you have a plaintext message you wish to encrypt and already have an encryption key, saved as a text file, in the format:

```
a_1, c_1
a_2, c_2
.
.
.
a_n, c_n
```

where the `a_i` are plaintext characters and the `c_i` ciphertext, you can apply the `masc_encrypter` script to your message, using the key, then attempt to crack it with `masc_decrypter` as in **1.**.

**4.** If you have only the plaintext message, but no key, you can first create one using the `generate_key` script, then encrypt and attempt to crack it as in the previous two steps.


## 3. Alphabet

xxx

## 4. Dependencies

xxx
