# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8') # Useful for authors like Schwarzmüller

import re
import csv
import glob
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

separator = ";" # Do not change

unify_fields = {"Titulo":["title"],
                "Autor":["author"],
                u"Año":["year"],
                "Palabras":["keywords","keywords-plus","author_keywords"],
                "Resumen":["abstract"],
                "Tipo":["ENTRYTYPE"],
                "Id":["ID"],
                "Referencias":["cited-references","references"], # Only on WoS and SCOPUS
                }

# This functions helps to parse correctly every field
def title_parser(title):
    return title.replace("\n", " ") # For WoS field
def author_parser(author):
    author = author.replace("\n", " ") # For WoS field
    author = author.replace(" and", separator)
    return author
def year_parser(date):
    # Return only the year. Ex: 2019/11/30 = 2019
    return re.search('\d{4}', date).group(0)
def keywords_parser(kw):
    kw = kw.replace("\n", " ") # For WoS field
    kw = kw.replace(",", separator) # For EBSCO field
    return kw
def abstract_parser(abs):
    return abs.replace("\n", " ") # For WoS field
def cited_references_parser(cr):
    # This is a WoS field
    f=open("references-wos.txt", "a+")
    f.write(str(cr))
    return cr.replace("\n", separator)
def references_parser(cr):
    # This is a SCOPUS field
    f=open("references-scopus.txt", "a+")
    f.write(str(cr.replace(separator, "\n").strip()))
    return cr

def print_log(msg):
    f=open("log.txt", "a+")
    f.write(str(msg))
    print(msg)

def load_bib(filename):
    with open(filename) as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.loads(bibtex_file.read().replace("{{","{").replace("}}","}"),
                                          parser=parser)
        return bib_database

# Useful to know all the fields in a bib_db
def show_fields(source):
    fields = set()
    bib_db = load_bib(source)
    for entrie in bib_db.entries:
        fields.update(entrie.keys())
    for field in fields:
        print_log(field)
# Useful to see some examples of data in a specific field
def show_ids(source, field, rows=8):
    bib_db = load_bib(source)
    for i in range(rows):
        try:
            print_log(bib_db.entries[i][field])
        except:
            print_log("-")
        print_log("\n")

def unify(bib_entry, source="undefined"):
    entry = {"Fuente": source}
    for k, v in unify_fields.items():
        entry.update({k:""})
        titleletters = re.sub(r'[^a-zA-Z0-9]+', '', bib_entry["title"])
        entry.update({"titleletters": titleletters.lower()}) # Useful for combinations
        for f in v:
            s = ""
            value = ""
            try:
                if len(entry[k]) > 1 and bib_entry[f]:
                    s = separator
                value = bib_entry[f].replace("\t"," ")
                value = globals()[f.replace("-","_")+"_parser"](value)
            except KeyError:
                # Generate an KeyError exception if bib_entry not have [f]
                # Generate an KeyError exception if the [f+"_parser"] function not exists
                pass

            entry[k] += s + value.replace("  "," ").strip()
    return entry

def tocsv(toCSV):
    keys = toCSV[0].keys()
    with open('unified.txt', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter='\t')
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)

def read_bib(source):
    print_log("Reading: "+source)
    bib_db = load_bib(source)
    entries_unified = []
    for entrie in bib_db.entries:
        entries_unified.append(unify(entrie, source))
    print_log(str(len(entries_unified))+" processed records")
    return entries_unified


print_log("\nRunning BibTeX to txt\n")
entries_to_save = []
for filename in glob.glob('*.bib'):
    entries_to_save.extend(read_bib(filename))


print_log("\nSaving unified.txt as a tab separated file")
tocsv(entries_to_save)
print_log(str(len(entries_to_save))+ " total records saved")