# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8') # Useful for authors like Schwarzmüller

import csv
import glob
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
#from bibtexparser.bibdatabase import as_text
#print(as_text(bib_db.entries[1]))

separator = ";"

unify_fields = {"Tipo":["ENTRYTYPE"],
                "Id":["ID"],
                u"Año":["year"],
                "Titulo":["title"],
                "Resumen":["abstract"],
                "Autor":["author"],
                #"Referencias":["cited-references","references"],
                "Palabras":["keywords","keywords-plus","author_keywords"]
                }
# TODO: call a function as field name
def abstract(abs):
    return abs.replace("\n", " ")
def cited-references(cr):
    return cr.replace("\n", ";")


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
        print(field)
# Useful to see some examples of data in a specific field
def show_ids(source, field, rows=8):
    bib_db = load_bib(source)
    for i in range(rows):
        try:
            print(bib_db.entries[i][field])
        except:
            print("-")
        print("\n")

def unify(bib_entry, source="undefined"):
    entry = {"Fuente": source}
    for k, v in unify_fields.items():
        entry.update({k:""})
        for f in v:
            s = ""
            try:
                if len(entry[k]) > 1 and bib_entry[f]:
                    s = separator
                entry[k] += s + bib_entry[f].replace("\n",separator).replace("\t"," ")
            except:
                pass
    return entry

def tocsv(toCSV):
    keys = toCSV[0].keys()
    with open('unified.txt', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter='\t')
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)

def read_bib(source):
    print(source)
    bib_db = load_bib(source)
    entries_unified = []
    for entrie in bib_db.entries:
        entries_unified.append(unify(entrie, source))
    print(len(entries_unified))
    return entries_unified

entries_to_save = []
for filename in glob.glob('*.bib'):
    entries_to_save.extend(read_bib(filename))

print("Saving unified.txt as a tab separated file")
tocsv(entries_to_save)
print(len(entries_to_save))