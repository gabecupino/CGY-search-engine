from nltk.stem.snowball import SnowballStemmer
from utilities import *

# Global variables
INDEX_PATH = "index.txt"
BOOKKEEPING_PATH = "WEBPAGES_CLEAN/bookkeeping.json"
WRITE_PATH = "query_results.txt"
MAX_RESULTS = 35000


# Prompts user for a query and prints out all the URLs as results of the query
def run_query_program():
    query = prompt_query()
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    write_query_header(WRITE_PATH, query)
    index_size = 0

    query = stemmer.stem(query)
    postings = retrieve_postings(query, INDEX_PATH,index_size)

    if len(postings) > 0:
        print_urls(BOOKKEEPING_PATH, postings)
        #write_urls_to_file(WRITE_PATH, BOOKKEEPING_PATH, postings, MAX_RESULTS)
    else:
        print "No results found for given query: ", query
        #write_no_results(WRITE_PATH, query)


# Prompts user for a query and returns the user input as a string
def prompt_query():
    return raw_input("Enter your query: ")

# Searches index file for single query term and returns a list of
# docIDs associated with the term
def retrieve_postings(query, index_path, index_size):
    with open(index_path, "r", encoding='utf8') as index:
        index_size = int(index.readline())
        for line in index:
            term_posting = line.split(":")
            if query.lower() == term_posting[0]:

                return process_raw_postings(term_posting[1], index_size)
    return list()

# Takes raw posting list string and returns a list of docIDs
# Postings format>>: doc_freq|doc_id-multiplier-token_freq;doc_id-multiplier-token_freq,....
def process_raw_postings(postings, index_size):
    doc_id_and_scores = list() # List of (doc_id, score)

    doc_freq_end_index = postings.find("|") # Find | delimiter that ends the doc_freq number
    doc_freq = postings[:doc_freq_end_index]

    docs_info = postings[doc_freq_end_index + 1:].split(";") # Remove doc_freq before splitting


    for doc_info in docs_info:
        if(doc_info != '\n'):
            split_info = doc_info.split("-")
            doc_id, tag_multiplier, term_freq = tuple(split_info)
            #print doc_id, tag_multiplier, term_freq, doc_freq

            # Calculate tf-idf weight scores
            tf_weight = log_freq_weight(int(term_freq))
            idf_weight = inverse_doc_freq(int(doc_freq), index_size)

            tf_idf_score = tf_weight * idf_weight * int(tag_multiplier)
            doc_id_and_scores.append((doc_id, tf_idf_score)) # Append to list of (doc_id, score)

    # Sort the documents by score
    sorted_doc_id_and_scores = sorted(doc_id_and_scores, key = lambda doc_info: doc_info[1], reverse= True)

    print "doc id, score"
    for (doc_id, score) in sorted_doc_id_and_scores:
        print doc_id, score

    return [doc_id_and_score[0] for doc_id_and_score in sorted_doc_id_and_scores] # Return sorted list of only the doc_ids


if __name__ == "__main__":
    run_query_program()
    print "Program terminated."
