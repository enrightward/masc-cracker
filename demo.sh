#!/bin/bash

# This script runs a live demo for the monoalphabetic substitution cipher cracking
# algorithm in masc_decrypter.py. It wraps three steps:
#
# (i) Key generation,
# (ii) Encryption of plaintext, and
# (iii) An attempt to crack the ciphertext, using character frequency statistics.
#
# The cracking algorithm needs training text from the same language as the plaintext
# message to compute character frequencies.
#
# You can copy the train and plaining texts into the PWD using 'dropin.py', if you like.
#
# See the docstrings of the three scripts below for further details.

PLAINTEXT='plain_text.txt'
TRAINING='train_text.txt'
ITER=10000
PAUSE=0.002
MODE='bigram'

./generate_key --method random --alphabet $PLAINTEXT
./masc_encrypter --input $PLAINTEXT
./masc_decrypter --training $TRAINING --iterations $ITER --mode $MODE --pause $PAUSE
