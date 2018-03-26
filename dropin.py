#!/usr/bin/env python3


import glob, os, argparse
from shutil import copy


SOURCEFOLDER = './docs'


def dropin(sourcefolder, prefix):
    matchstring = '%s*.txt' % prefix
    sources = glob.glob(os.path.join(sourcefolder, matchstring))
    targets = ['./train_text.txt', 'plain_text.txt']

    for f, g in zip(sources, targets):
        copy(f, g)


HELP_STR = """Given a prefix common to exactly two files in ./docs, copies
           these files into the current directory, naming them train_text.txt
           and plain_text.txt, respectively, in alphabetical order."""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=HELP_STR)
    #parser.add_argument('--prefix', help='a prefix common to exactly two files in ./docs/', type=str, required=True)
    parser.add_argument('prefix', help='a prefix common to exactly two files in ./docs/', type=str)
    args = parser.parse_args()
    dropin(SOURCEFOLDER, args.prefix)
