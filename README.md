# masc-cracker

## 1. Outline

This repo contains python 3 code for making and breaking monoalphabetic substitution ciphers (MASCs). The decryption algorithm makes two simplifying assumptions:

1. Spaces are preserved in the ciphertext.

2. We know the language of the underlying plaintext message.

This code does three things:

1. Key generation, handled by `generate_key`.

2. Encryption of plaintext into ciphertext, using a key, handled by the `masc_encrypter` script.

3. Attempted decryption of cipher- into plaintext, given only the ciphertext and a training sample of plaintext from the same language as the underlying message. This is handled by the `masc_decrypter` script.

This repo also contains example plaintext files in several languages, in the `./docs` subdirectory. There are two files per language represented: One to be used as a plaintext to be encrypted, and the other as a training text from which the alphabet and character frequencies of the underlying language are inferred, to aid decryption of the cipher, with no knowledge of the plaintext message or encryption key. Typing e.g. 

```
./dropin.py french
```

will copy-paste the two french language files contained in `./docs` into the PWD as `plain_text.txt` and `train_text.txt`.

## 2. Quickstart

In the `./masc-cracker` directory:

**1.** Type e.g. 

```
./dropin.py french
```

to copy-paste the two french language files contained in `./docs` into the PWD as `plain_text.txt` and `train_text.txt`. 

**2.** Type 

```
./demo.sh
```

This script firstly infers the alphabet of `plain_text.txt`, then randomly generate a key on this alphabet, then encrypts `plain_text.txt` and saves the resulting ciphertext to disk as `cipher_text.txt`, also saving the encryption key to disk as `encryption_key.csv`. Finally, it attempts to break the cipher without looking at the plaintext or the encryption key, saving to disk its best-guess decipherment as `deciphered_text.txt`, and best-guess decryption key as `decryption_key.csv`. Running:

```
./clear.sh
```

deletes the encryption and decryption keys from disk, as well as the ciphertext and attempted deciphered text. It does not delete the plain and train text files.

## 3. Usage in more detail

You can interact with the code using the three scripts `generate_key`, `masc_encrypter` and `masc_decrypter`. Each is documented. There are several possibilities:

1. (Quickest) The script `demo.sh` takes an argument `plain_text.txt`, encrypts it as `cipher_text.txt` with a randomly generated key, then uses the character frequency statistics contained in the text of a second argument, `train_text.txt`, to try and decrypt `cipher_text.txt`. The decryption algorithm does not cheat: It has access neither to the original `plain_text.txt`, nor to the encryption key.

The `demo.sh` script works out of the box, provided the PWD contains two plaintext files: `plain_text.txt` and `train_text.txt`, both written in the same language. The `./docs` subdirectory contains examples of such files, in `(plain, train)` pairs, in several languages. As explained above, you can type e.g. 

```
./dropin.py french
```

to copy-paste the two french language files contained in `./docs` into the PWD, naming them `plain_text.txt` and `train_text.txt`.

2. If you already have MASC-encrypted ciphertext, you can attempt to crack it immediately using the `masc_decrypter` script.

3. If you have a plaintext message you wish to encrypt and already have an encryption key, saved as a text file, in the format:

```
a_1, c_1
a_2, c_2
.
.
.
a_n, c_n
```

where the `a_i` are plaintext characters and the `c_i` ciphertext, you can apply the `masc_encrypter` script to your message, using the key, then attempt to crack it with `masc_decrypter` as in **1.**

4. If you have only the plaintext message, but no key, you can first create one using the `generate_key` script, then encrypt your message and attempt to crack it, ignoring your key, as in the previous two steps.

## 4. The decryption algorithm

xxx


## 5. Inferring the alphabet, handling non-alphabetic characters 

xxx

## 6. Dependencies

The code is written in python 3. It uses the following non-standard libraries: `numpy`, `curses`, `colr`.
