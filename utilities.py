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
# Number of URLs depends on result_count_cap parameter
def print_urls(bookkeeping_path, postings, result_count_cap):
    counter = 0
    for posting in postings:
        print retrieve_url(bookkeeping_path, convert_posting_format(posting))
        counter += 1
        if (counter >= result_count_cap):
            break

# Returns the URLs corresponding to a list of pre-formatted docIDs
# Number of URLs depends on result_count_cap parameter
def get_urls(bookkeeping_path, postings, result_count_cap):
    counter = 0
    resulting_urls = []
    for posting in postings:
        resulting_urls.append(retrieve_url(bookkeeping_path, convert_posting_format(posting)))
        counter += 1
        if (counter >= result_count_cap):
            break
    return resulting_urls

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

def get_doc_ids_and_scores(doc_ids_intersection, query_term_postings):
    # Params: doc_ids_intersection = set(doc_ids)
    #         query_term_postings = query_term: {doc_id: score}; Contains postings for a query term
    doc_id_and_scores = []

    # Add up all the scores of doc_ids that contain every query term
    for doc_id in doc_ids_intersection:
        total_score = 0  # combined score for a doc and all query terms

        for query_term, postings in query_term_postings.items():
            score = postings.get(doc_id)
            total_score += score

        doc_id_and_scores.append((doc_id, total_score))

    return doc_id_and_scores

def get_sorted_doc_ids(doc_ids_and_scores):
    # Param: [(doc_id, score)]

    # Sort doc_ids by scores
    sorted_doc_id_and_scores = sorted(doc_ids_and_scores, key=lambda doc_info: doc_info[1], reverse=True)

    # List all doc_ids (pre-sorted)
    results = [doc_id_and_score[0] for doc_id_and_score in sorted_doc_id_and_scores]

    return results
