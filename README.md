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

1. Type e.g. 
```
./dropin.py french
```
to copy-paste the two french language files contained in `./docs` into the PWD as `plain_text.txt` and `train_text.txt`. 

2. Type 
```
./demo.sh
```
This script firstly infers the alphabet of `plain_text.txt`, then randomly generate a key on this alphabet, then encrypts `plain_text.txt` and saves the resulting ciphertext to disk as `cipher_text.txt`, also saving the encryption key to disk as `encryption_key.csv`. Finally, it attempts to break the cipher without looking at the plaintext or the encryption key, saving to disk its best-guess decipherment as `deciphered_text.txt`, and best-guess decryption key as `decryption_key.csv`. 

3. Running:
```
./clear.sh
```
deletes the encryption and decryption keys from disk, as well as the ciphertext and attempted deciphered text. It does not delete the train- and plaintext files.

## 3. Usage in more detail

You can interact with the code using the three scripts `generate_key`, `masc_encrypter` and `masc_decrypter`. Each is documented. There are several possibilities:

1. (Quickest) The script `demo.sh` takes an argument `plain_text.txt`, encrypts it as `cipher_text.txt` with a randomly generated key, then uses the character frequency statistics contained in the text of a second argument, `train_text.txt`, to try and decrypt `cipher_text.txt`. The decryption algorithm does not cheat: It has access neither to the original `plain_text.txt`, nor to the encryption key. The `demo.sh` script works out of the box, provided the PWD contains two plaintext files: `plain_text.txt` and `train_text.txt`, both written in the same language. The `./docs` subdirectory contains examples of such files, in `(plain, train)` pairs, in several languages. As explained above, you can type e.g. 
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

Here is a high level description of the decryption algorithm. 

1. Generate a random `current_decryption_key`, and apply this to the ciphertext to create a `current_deciphered_text`. Since it is the output of the `current_decryption_key`, `current_deciphered_text` will be written in the plaintext alphabet. However, since the `current_decryption_key` is initially chosen at random, `current_deciphered_text` will be garbled to begin with.

2. Compute all character bigram frequencies in the training text, and save these to an `N` x `N` array `F(TT)`, where `N` is the size of the plaintext alphabet. We assume that the bigram frequencies in the training text approximate the bigram probabilities of the underlying language.

3. Compute the `N` x `N` array `C(DT)` of bigram counts of the `current_deciphered_text`. Compute also the sum `L(DT)` over all entries of the entrywise product `P(DT) := C(DT) * F(TT)` of `C(DT)` and `F(TT)`. The entries of `F(TT)` approximate the plaintext bigram probabilities for the underlying plaintext language, and the entries of `C(DT)` are exactly the bigram counts in `current_deciphered_text` so the `(a_i, a_j)`-th entry in `P(DT)` is roughly probability that the `current_deciphered_text` contains the given number of instances of the bigram `a_i, a_j`. Hence `L(DT)` is roughly the likelihood of seeing all bigrams in the `current_deciphered_text` together, treating each bigram appearance as an independent event.

The idea is now to make successive small, random modifications to the `current_decryption_key` (which in turn modifies the `current_deciphered_text`, which in turn modifies `C(DT)`, which in turn modifies `L(DT)`), and check if each modification increases `L(DT)`. Informally, such an increase would mean that the modified `current_deciphered_text` is more likely than its predecessor, so in this case we keep the modification to the `current_decryption_key`. Otherwise, if `L(DT)` does not increase, we discard the modification, and try a new one in its place. More precisely:

4. For a fixed number of iterations specified by the user:

      (i) Swap two randomly chosen letters in the deciphered text (corresponding to a swap in `current_decryption_key`).

      (ii) Recompute `C(DT)` and `L(DT)`.

      (iii) If `L(DT)` has increased, keep the change to `current_decryption_key`. If `L(DT)` has not increased, discard the change.

5. Return the `current_decryption_key` and `current_deciphered_text`.

## 5. Inferring the alphabet, handling non-alphabetic characters

The alphabets of plain- and cipertext of characters understood by the en- and decryption algorithms are defined by the en- and decryption keys. Here we explain how each of the scripts `generate_key`, `masc_encrypter` and `masc_decrypter` handles characters outside the alphabets, and how the alphabet is inferred from a text file by `generate_key`.

1. The `generate_key` script creates an encryption key by choosing a random permutation of the alphabet it infers from a plaintext file argument `--alphabet`. This alphabet is defined to be the set of all non blank, non punctuation characters in the file. 

2. The `masc_encrypter` script can apply any encryption key to any plaintext file. If the script encounters a character outside the encryption key's alphabet, it is replaced with a blank space.

3. The `masc_decrypter` script can attempt to crack any ciphertext file. It infers plain- and ciphertext alphabets from two text file arguments `--plainalpha` and `--cipheralpha`, then builds a key from these. It refines these key using character frequency statistics from a plaintext file `--training`, by hypothesis written in the same language as the underlying plaintext message. A user may believe that only certain ciphertext characters contain information, and therefore define `--cipheralpha` to be some file other than the ciphertext. In this case, frequency statistics of characters in the ciphertext not belonging to the ciphertext alphabet are ignored.

## 6. Dependencies

The code is written in python 3. It uses the following non-standard libraries: 

1. `numpy`:   http://www.numpy.org/

2. `curses`:   https://docs.python.org/3/howto/curses.html

3. `colr`:   https://pypi.python.org/pypi/Colr/0.8.1
