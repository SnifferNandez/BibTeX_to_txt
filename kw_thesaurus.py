# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8') # Useful for some special chars like ü

import re
import nltk
import json
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def new_word(keyword):
    keyword = keyword.strip().decode('utf-8', 'ignore')
    # Derivación regresiva con NLTK (Word Stemming)
    # algoritmo Porter de derivación regresiva
    stemmer = PorterStemmer()
    # Palabras lematizadoras usando WordNet (Lemmatize Words)
    # Lematizar palabras es similar a la derivación regresiva; pero, la diferencia es el que la lematización es el mundo real.
    lemmatizer = WordNetLemmatizer()
    kw = lemmatizer.lemmatize(keyword)
    return stemmer.stem(keyword).strip()

def new_words(actual_words):
    # Para sugerir tesauros:
    # Quitar lo que esta entre parentesis, eje Capture the flag (CTF)
    # Quitar lo que esta entre llaves, eje kuwait [middle east]
    words = actual_words.split(" ")
    changed_words = []
    for word in words:
        if word not in stopwords.words("english"):
            changed_words.append(new_word(word))
    return " ".join(changed_words)

def remove_parentheses(words):
    b = words.find("(")
    e = words.find(")")
    if b != -1 and e == -1:
        e = len(words)
    s = words[b:e+1]
    words = words.replace(s,"")
    return words.strip()

def transform_all_words(filename):
    with open(filename) as f:
        words_line = f.readlines()
    print("Analyzing " + str(len(words_line)) + " lines")
    new_all_words = []
    for words in words_line:
        if words.strip() != "":
            nw = new_words(remove_parentheses(words))
            new_all_words.append(nw)
            #Usefull to detect some abbreviations
            #if nw.find("(") != -1:
            #    print("Thesaurus?: " + words.strip())
    return new_all_words

def plot_frecuency(unique_set):
    tokens = []
    for u in unique_set:
        tokens.extend(u.split(" "))
    freq = nltk.FreqDist(tokens)
    for key,val in freq.items():
        print (str(key) + ':' + str(val))
    freq.plot(20, cumulative=False)

def write_file(data, filename="unnamed.txt"):
    print("  Writing "+filename+" file")
    f=open(filename, "w+")
    f.write(data)

def save_array(array, filename="unnamed.txt"):
    to_file = '\n'.join(str(line) for line in array)
    write_file(to_file,filename)

def save_dict(dict_data, filename="unnamed.txt"):
    write_file(json.dumps(dict_data, ensure_ascii=False),filename)

def save_changes_th(changes_th):
    superiors = 0
    for k, v in changes_th["superiors"].items():
        v = list(set(v))
        changes_th["superiors"][k] = v
        superiors += len(v)
    abbreviations = 0
    for k, v in changes_th["abbreviations"].items():
        abbreviations += v
    print(str(superiors) + " different keywords reducet to " + str(len(changes_th["superiors"])) + " superior keywords")
    print(str(abbreviations) + " abbreviations expanded")
    save_dict(changes_th, "5-combined_th.txt")

def unique_words(words):
    new_unique_words = set(words)
    print("Derived in " + str(len(new_unique_words)) + " unique lines")
    save_array(sorted(new_unique_words),"5-NewUniqueDerivedKw.txt")
    #plot_frecuency(new_unique_words)

def change_thesaurus_file(logic, filename):
    with open(filename) as f:
        words_line = f.readlines()
    print("Converting " + str(len(words_line)) + " lines")
    new_all_words = []
    combined_th = {}
    for words in words_line:
        ow = words.strip()
        if ow != "":
            tw = remove_parentheses(words)
            tw = tw.split(" ")
            try:
                nw = logic[tw[0]+"*"]
                try:
                    combined_th[tw[0]+"*"].append(ow)
                except:
                    combined_th[tw[0]+"*"] = [ow]
            except:
                nw = ow
            new_all_words.append(nw)
    print(combined_th)
    return new_all_words

def first_analysis():
    new_words = transform_all_words("5-uniqueKw.txt")
    print("Given " + str(len(new_words)) + " transformed lines")
    unique_words(new_words)

def test_th():
    th_file = 'thesaurusLogic.json'
    with open(th_file,'r') as inf:
        thesaurusLogic = eval(inf.read())
    new_words = change_thesaurus_file(thesaurusLogic,"5-NewUniqueDerivedKw.txt")

def keyword_rules(keyword):
    keyword = keyword.strip()
    keyword = keyword.replace("e-", "e")
    keyword = keyword.replace("m-", "m")
    keyword = keyword.replace("-", " ")
    keyword = keyword.replace("’", "'")
    return keyword

def new_th_keywords(filename, logic_filename, new_filename):
    with open(filename) as f:
        all_lines = f.readlines()
    with open(logic_filename,'r') as inf:
        thesaurusLogic = eval(inf.read())
    changes_th = {"abbreviations":{},"superiors":{}}
    print("Analyzing " + str(len(all_lines)) + " keywords lines")
    new_all_words = []
    for line in all_lines:
        new_line = []
        for words in line.split(";"):
            keywords = remove_parentheses(keyword_rules(words))
            if keywords != "":
                tw = new_words(keywords)
                nw = []
                th_superior = []
                for aw in tw.split(" "):
                    try:
                        if thesaurusLogic[aw].startswith('*'): # Superior
                            thl = thesaurusLogic[aw].split("*")[1:]
                            th_superior.extend(thl)
                            for th in thl:
                                try:
                                    changes_th["superiors"][th].append(words.strip())
                                except:
                                    changes_th["superiors"][th] = [words.strip()]
                        else: # Abbreviation
                            keywords = keywords.replace(aw, thesaurusLogic[aw])
                            try:
                                changes_th["abbreviations"][aw] += 1
                            except:
                                changes_th["abbreviations"][aw] = 1
                    except:
                        nw.append(aw)
                if len(th_superior) > 0: # If use the Superior keywords
                    nw = th_superior
                else:
                    nw = [keywords.decode('utf-8', 'ignore')]
                new_line.extend(nw)
            # Usefull for keywords transformation debugging
            #if words.strip() == "third ict platform":
            #    print(words + "-->" + str(nw))
        new_all_words.append(";".join(list(set(new_line))))
    save_array(new_all_words, new_filename)
    save_changes_th(changes_th)
    return new_all_words

def test_words(keywords):
    print(new_words(remove_parentheses(keyword_rules(keywords))))

def run():
    new_all_words = new_th_keywords("4-allKw.txt","thesaurusLogic.json","5-allKwTh.txt")



#test_words("e-learning")
#test_words("elearning")
run()
