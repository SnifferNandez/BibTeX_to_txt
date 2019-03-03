# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8') # Useful for some special chars like ü

import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def new_word(keyword):
    keyword = keyword.strip()
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

def run():
    new_words = transform_all_words("5-uniqueKw.txt")
    print("Given " + str(len(new_words)) + " transformed lines")
    new_unique_words = set(new_words)
    print("Derived in " + str(len(new_unique_words)) + " unique lines")
    save_array(sorted(new_unique_words),"5-NewUniqueDerivedKw.txt")

    plot_frecuency(new_unique_words)
    #with open('thesaurusLogic.json','r') as inf:
    #    thesaurusLogic = eval(inf.read())

run()