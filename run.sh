#!/bin/bash

PLAINTEXT='plain_text.txt'
TRAINING='train_text.txt'
ITER=10000
MODE='bigram'

./generate_key --method random --alphabet $PLAINTEXT
./masc_encrypter --input $PLAINTEXT
./masc_decrypter --training $TRAINING --iterations $ITER --mode $MODE
