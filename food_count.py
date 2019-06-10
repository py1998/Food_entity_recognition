#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 11:44:22 2019

@author: porush
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from pprint import pprint
#sefrom file_read import statements_opt2

def count(sentence):
    pos = ((pos_tag(word_tokenize(sentence))))
    cnt = 1
    check_list = ["and", ",", "with"]
    cnt_list = []
    for idx in range(len(pos)):
        if pos[idx][1] == "CD":
            cnt = int(pos[idx][0])
        if (pos[idx][1] == "CC" or pos[idx][1] == "," or (pos[idx][0] in check_list)) :
            cnt_list.append(cnt)
            cnt = 1
        if idx == len(pos) - 1:
            cnt_list.append((cnt))
    return cnt_list