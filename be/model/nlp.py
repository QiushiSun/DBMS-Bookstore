import jieba.analyse as ana
import jieba
import re
import hashlib

def get_keyword(text):
    if isinstance(text,str) == False:
        return []
    summary_rate = 0.008
    text = re.sub(r"\n+", '\n', text)
    text = re.sub(r"\s+", ' ', text)
    text = text.replace(" ","，")
    text = text.replace("\n","。")
    l = len(text)
    k = int(l * summary_rate)
    if k < 1 :
        k = 1
    keywords = ana.textrank(text)
    return keywords

def get_preffix(text):
    if isinstance(text,str) == False:
        return []
    l = len(text)
    pre = []
    for i in range(1,l+1):
        pre.append(text[:i])
    return pre

def get_middle_ffix(text):
    if isinstance(text,str) == False:
        return []
    word_list = list(jieba.cut(text))
    l = len(word_list)
    middle = []
    words = ""
    for i in range(l):
        words = word_list[l-i-1] + words
        middle += get_preffix(words)
    middle = list(set(middle))
    return middle

def get_country_and_author(text):
    if isinstance(text,str) == False:
        return "", ""
    l = len(text)
    b = False
    country = ""
    author = ""
    for i in range(l):
        if text[i] in ")]}）】」":
            b = False
        elif b == True:
            country += text[i]
        elif text[i] in "([{（【「":
            b = True
            if country != "":
                country += "_"
        else:
            author += text[i]
            continue
    return country, author

def parse_name(text):
    if isinstance(text,str) == False:
        return []
    pre = 0
    l = len(text)
    names = []
    for i in range(l):
        if text[i] in '・· ,， ':
            if text[pre:i] != "":
                names.append(text[pre:i])
            pre = i+1
    names.append(text[pre:l])
    return names

def encrypt(password):
    pw = "19991205" + password + "zjcSQS tq"
    hash = hashlib.sha256()
    hash.update(pw.encode('utf-8'))
    return hash.hexdigest()