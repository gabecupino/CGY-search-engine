from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from utilities import *
from search_gui import *

# Global variables
INDEX_PATH = "index.txt"
BOOKKEEPING_PATH = "WEBPAGES_CLEAN/bookkeeping.json"
WRITE_PATH = "query_results.txt"
MAX_RESULTS = 10


# Prompts user for a query and prints out all the URLs as results of the query
def run_query_program():

    query = prompt_query()
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    #write_query_header(WRITE_PATH, query)
    stop_words = set(stopwords.words('english'))

    query_terms = [stemmer.stem(query_term) for query_term in query.split() if query_term not in stop_words]
    # Bug: stemming removes quotes

    query_term_postings = dict() # Format: query_term: {doc_id: score}; Contains postings for a query term
    doc_ids_intersection = None # Set of doc_ids

    for query_term in query_terms:
        postings = retrieve_postings(query_term, INDEX_PATH) # postings are {doc_id: score}
        query_term_postings[query_term] = postings

        if doc_ids_intersection is None:
            doc_ids_intersection = set([doc_id for doc_id in postings.keys()]) # Initialize doc_id_intersection set

        else:
            doc_ids_intersection.intersection_update([doc_id for doc_id in postings.keys()]) # Update intersection set

    doc_id_and_scores = get_doc_ids_and_scores(doc_ids_intersection, query_term_postings)

    sorted_doc_ids = get_sorted_doc_ids(doc_id_and_scores)

    if len(sorted_doc_ids) > 0:
        print_urls(BOOKKEEPING_PATH, sorted_doc_ids, MAX_RESULTS)
        #write_urls_to_file(WRITE_PATH, BOOKKEEPING_PATH, postings, MAX_RESULTS)
    else:
        print "No results found for given query: ", query
        #write_no_results(WRITE_PATH, query)

# Prompts user for a query and prints out all the URLs as results of the query
def run_query_program_with_params(query):
    if len(query) == 0:
        return []
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    #write_query_header(WRITE_PATH, query)
    stop_words = set(stopwords.words('english'))

    query_terms = [stemmer.stem(query_term) for query_term in query.split() if query_term not in stop_words]
    # Bug: stemming removes quotes

    query_term_postings = dict() # Format: query_term: {doc_id: score}; Contains postings for a query term
    doc_ids_intersection = None # Set of doc_ids

    for query_term in query_terms:
        postings = retrieve_postings(query_term, INDEX_PATH) # postings are {doc_id: score}
        query_term_postings[query_term] = postings

        if doc_ids_intersection is None:
            doc_ids_intersection = set([doc_id for doc_id in postings.keys()]) # Initialize doc_id_intersection set

        else:
            doc_ids_intersection.intersection_update([doc_id for doc_id in postings.keys()]) # Update intersection set

    doc_id_and_scores = get_doc_ids_and_scores(doc_ids_intersection, query_term_postings)

    sorted_doc_ids = get_sorted_doc_ids(doc_id_and_scores)

    if len(sorted_doc_ids) > 0:
        return get_urls(BOOKKEEPING_PATH, sorted_doc_ids, MAX_RESULTS)
    else:
        return []


# Prompts user for a query and returns the user input as a string
def prompt_query():
    return raw_input("Enter your query: ")

# Searches index file for single query term and returns a list of
# (docIDs, scores) associated with the term
def retrieve_postings(query, index_path):
    with open(index_path, "r", encoding='utf8') as index:
        index_size = int(index.readline()) # Read index size
        for line in index:
            term_posting = line.split(":")
            if query.lower() == term_posting[0]:

                return process_raw_postings(term_posting[1], index_size)
    return dict()

# Takes raw posting list string and returns a dict of docIDs:score
# Postings format>>: doc_freq|doc_id-multiplier-token_freq;doc_id-multiplier-token_freq,....
def process_raw_postings(postings, index_size):
    doc_id_and_scores = dict() # dict of docIDs:score

    doc_freq_end_index = postings.find("|") # Find | delimiter that ends the doc_freq number
    doc_freq = postings[:doc_freq_end_index]

    docs_info = postings[doc_freq_end_index + 1:].split(";") # Remove doc_freq before splitting


    for doc_info in docs_info:
        if(doc_info != '\n'):
            split_info = doc_info.split("-")
            doc_id, tag_multiplier, term_freq = tuple(split_info)
            #print doc_id, tag_multiplier, term_freq, doc_freq

            # Calculate tf-idf weight scores
            tf_weight =  1 +log_freq_weight(int(term_freq))
            idf_weight = inverse_doc_freq(int(doc_freq), index_size)

            tf_idf_score = tf_weight * idf_weight * int(tag_multiplier)
            doc_id_and_scores[doc_id] = tf_idf_score # Append to list of (doc_id, score)

    return doc_id_and_scores

if __name__ == "__main__":
    run_query_program()
    print "Program terminated."
