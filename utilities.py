from io import open
import json
from math import log10

# Converts docID format to work with bookkeeping.json format
def convert_posting_format(doc_id):
    paths = doc_id.split(".")
    return paths[0] + "/" + paths[1]

# Returns the corresponding URL of a given docID
def retrieve_url(bookkeeping_path, doc_id):
    with open(bookkeeping_path, "r") as url_data_file:
        data = json.load(url_data_file)
        return data[doc_id]

# Prints out all the URLs corresponding to a list of pre-formatted docIDs
def print_urls(bookkeeping_path, postings):
    for posting in postings[:-1]:
        print retrieve_url(bookkeeping_path, convert_posting_format(posting))

# Writes to file a header for a query
def write_query_header(write_path, query):
    with open(write_path, "wb") as results:
        results.write(("Search results for query \"" + query + "\":\n\n").encode("utf-8"))


# Handles writing to file when no results are queried
def write_no_results(write_path, query):
    with open(write_path, "wb") as results:
        results.write(("No results found for query: \"" + query + "\"\n\n\n").encode("utf-8"))


# Write URLs to an out file to save run data
def write_urls_to_file(write_path, bookkeeping_path, postings, max_results):
    with open(write_path, "wb") as results:
        url_count = 0
        for posting in postings[:-1]:
            url = retrieve_url(bookkeeping_path, convert_posting_format(posting))
            results.write((url + "\n").encode("utf-8"))
            url_count += 1
            if (url_count >= max_results):
                break
        results.write(("\nNumber of URLs retrieved: " + str(url_count) + "\n\n\n").encode("utf-8"))

def log_freq_weight(term_freq):
    if term_freq > 0:
        return 1 + log10(term_freq)
    else:
        return 0

def inverse_doc_freq(doc_freq, index_size):
    return log10(index_size/doc_freq)

    
