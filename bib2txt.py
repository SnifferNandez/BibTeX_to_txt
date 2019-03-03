# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8') # Useful for authors like Schwarzmüller

import re
import csv
import glob
import logging
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
                "Impacto":["times-cited","note"], # Only on WoS and SCOPUS
                "Referencias":["cited-references","references"], # Only on WoS and SCOPUS
                }


logger = logging.getLogger(__name__)
f_handler = logging.FileHandler('0-log.txt')
f_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#f_handler.setLevel(logging.ERROR)
logger.addHandler(f_handler)

def print_log(msg):
    logger.info(msg)
    print(msg)

def write_file(data, filename="unnamed.txt"):
    print_log("-Writing "+filename+" file")
    f=open(filename, "a+")
    f.write(data)

# This functions helps to parse correctly every field
def title_parser(title):
    return title.replace("\n", " ") # For WoS field
def author_parser(author):
    author = author.replace("\n", " ") # For WoS field
    author = author.replace(separator, "-").replace(" and", separator)
    return author
def year_parser(date):
    # Return only the year. Ex: 2019/11/30 = 2019
    return re.search('\d{4}', date).group(0)
def keywords_parser(kw):
    kw = kw.replace("\n", " ") # For WoS field
    kw = kw.replace(" and ",separator) # For some SCOPUS keywords
    kw = kw.replace("--", separator).replace(",", separator) # For EBSCO field
    return kw
def keywords_plus_parser(kw):
    kw = kw.replace("\n", " ") # For WoS field
    return kw
def abstract_parser(abs):
    return abs.replace("\n", " ") # For WoS field
def times_cited_parser(impact):
    return impact # For WoS field
def note_parser(impact):
    return impact.split("cited By ")[1] # For SCOPUS field: note={cited By 1}
def cited_references_parser(cr):
    # This is a WoS field
    cr = cr.replace(separator, "-").replace("\n", separator)
    #f=open("9-references-wos.txt", "a+")
    #f.write(str(cr))
    return cr
def references_parser(cr):
    # This is a SCOPUS field
    cr = cr.replace(separator, "-").replace(separator, "\n").strip()
    #f=open("9-references-scopus.txt", "a+")
    #f.write(str(cr))
    return cr

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

def read_bib(source):
    print_log("Reading: "+source)
    bib_db = load_bib(source)
    entries_unified = []
    for entrie in bib_db.entries:
        entries_unified.append(unify(entrie, source))
    print_log(str(len(entries_unified))+" processed records")
    return entries_unified

def overlaying(data):
    print_log("- Simple overlay analysis:")
    overlay = {}
    for d in data:
        #o = separator.join(sorted(d.split(separator)))
        try:
            overlay[d] += 1
        except:
            overlay[d] = 1
    # Analizar casos: wos.bib;wos.bib;wos.bib (resta 2 a wos.bib)
    # o: wos.bib;ebsco.bib;wos.bib (resta 1 a wos.bib y suma a ebsco.bib;wos.bib)
    for k, v in overlay.items():
        print_log(str(v) + "\t" + k.replace(separator," + "))

def overlayed(entries, repeated, commons):
    print_log(str(len(commons))+" repeated records")
    overlay = []
    for common in commons:
        for entrie in entries:
            if entrie["titleletters"] == common:
            # **************************************
            # **************************************
            # **************************************
            #                TODO:
            #      El impacto y las referencias
            # no pueden ser de EBSCO sino WoS-SCOPUS
            #       Tambien sumar las keywords
            # **************************************
            # **************************************
            # **************************************
            # This make a prefered selection, articles over all
                fuentes = []
                for r in repeated:
                    if r["titleletters"] == common:
                        fuentes.append(r["Fuente"])
                repeated.append(entrie.copy())
                d = entrie["Fuente"] + separator + separator.join(fuentes)
                entrie["Fuente"] = separator.join(sorted(d.split(separator)))
                overlay.append(str(entrie["Fuente"]))
                break
    tocsv(repeated,"3-repeated.txt")
    overlaying(overlay)
    return entries

def search_titleletters(titleletters, entries):
    for e in entries:
        if titleletters == e["titleletters"]:
            return e
    return {}

def merge(entries):
    print_log("\nSearching for similar records...")
    unique = set()
    repeated = []
    commons = set()
    merged = []
    for e in entries:
        i = len(unique)
        unique.add(e["titleletters"])
        if i == len(unique):
            commons.add(e["titleletters"])
            if e["Tipo"] == "article":
                old = search_titleletters(e["titleletters"],entries)
                if old["Tipo"] != "article":
                    print("replacing " + e["titleletters"])
                    repeated.append(old)
                    merged.remove(old)
                    merged.append(e)
                else:
                    repeated.append(e)
            else:
                repeated.append(e)
        else:
            merged.append(e)
    if len(commons) > 0:
        merged = overlayed(merged, repeated, commons)
    else:
        print_log("No repeated records found")
    tocsv(merged,"2-uniques.txt")
    return merged

def types_counter(entries):
    print_log("- Types record analysis:")
    types = {}
    for e in entries:
        # Indicar en que fuentes se encuentran esos tipos
        try:
            types[e["Tipo"]] += 1
        except:
            types[e["Tipo"]] = 1
    for k, v in types.items():
        print_log(str(v) + "\t" + k.replace(separator," + "))

def keywords_analysis(entries):
    print_log("- Analysis of keywords:")
    unique_keywords = set()
    for e in entries:
        keywords = e["Palabras"].capitalize()
        for keyword in keywords.split(separator):
            unique_keywords.add(keyword.strip())
    #print(unique_keywords)
    print_log(str(len(unique_keywords))+ " unique keywords")
    to_file = '\n'.join(str(line) for line in sorted(unique_keywords))
    write_file(to_file,"4-uniqueKW.txt")

def unauthor(entries):
    print_log("\nSearching for unauthored records")
    withouttitle = []
    for e in entries:
        if e["Autor"] == "" or e["Autor"] == None:
            withouttitle.append(e)
            entries.remove(e)
    print_log(str(len(withouttitle))+ " records without author")
    if len(withouttitle) > 0:
        tocsv(withouttitle,"9-withoutauthor.txt")
        tocsv(entries,"9-withauthor.txt")
    return entries

def tocsv(toCSV, filename="unamed.txt"):
    print_log("\nSaving "+filename+" as a tab separated file")
    keys = toCSV[0].keys()
    with open(filename, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter='\t')
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)
    print_log(str(len(toCSV))+ " total records saved")

def run():
    print_log("\nRunning BibTeX to txt\n")
    entries_to_save = []
    for filename in glob.glob('*.bib'):
        entries_to_save.extend(read_bib(filename))
    tocsv(entries_to_save,"1-all.txt")
    entries_to_save = merge(entries_to_save)
    types_counter(entries_to_save)
    keywords_analysis(entries_to_save)



try:
    run()
except Exception as e:
    logging.error("Exception occurred", exc_info=True)
