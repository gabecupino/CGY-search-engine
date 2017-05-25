import json

INDEX_PATH = "index.txt"
BOOKKEEPING_PATH = "WEBPAGES_CLEAN/bookkeeping.json"
WRITE_PATH = "query_results.txt"


# Prompts user for a query and prints out all the URLs as results of the query
def run_query_program():
    query = prompt_query()
    write_query_header(WRITE_PATH, query)
    postings = retrieve_postings(query, INDEX_PATH)
    if len(postings) > 0:
        write_urls_to_file(WRITE_PATH, BOOKKEEPING_PATH, postings)
    else:
        write_no_results(WRITE_PATH, query)


# Prompts user for a query and returns the user input as a string
def prompt_query():
    return raw_input("Enter your query: ")

# Searches index file for single query term and returns a list of
# docIDs associated with the term
def retrieve_postings(query, index_path):
    with open(index_path, "r") as index:
        for line in index:
            term_posting = line.split(":")
            if query.lower() == term_posting[0]:

                return process_raw_postings(term_posting[1])
    return list()

# Takes raw posting list string and returns a list of docIDs
def process_raw_postings(postings):
    return postings.split(";")

# Converts docID format to work with bookkeeping.json format
def convert_posting_format(doc_id):
    paths = doc_id.split(".")
    return paths[0] + "/" + paths[1]

# Returns the corresponding URL of a given docID
def retrieve_url(bookkeeping_path, doc_id):
    if len(doc_id.split("/")[1]) <= 3:
        with open(bookkeeping_path, "r") as url_data_file:
            data = json.load(url_data_file)
            return data[doc_id]
    else:
        return ""

# Prints out all the URLs corresponding to a list of pre-formatted docIDs
def print_urls(bookkeeping_path, postings):
    for posting in postings[:-1]:
        print retrieve_url(bookkeeping_path, convert_posting_format(posting))

def write_query_header(write_path, query):
    with open(write_path, "a") as results:
        results.write(("Search results for query \"" + query + "\":\n\n").encode("utf-8"))

def write_no_results(write_path, query):
    with open(write_path, "a") as results:
        results.write(("No results found for query: \"" + query + "\"\n\n\n").encode("utf-8"))


def write_urls_to_file(write_path, bookkeeping_path, postings):

    with open(write_path, "a") as results:
        url_count = 0
        for posting in postings[:-1]:
            url = retrieve_url(bookkeeping_path, convert_posting_format(posting))
            if len(url) > 0:
                results.write((url + "\n").encode("utf-8"))
                url_count += 1
        results.write(("\nNumber of URLs retrieved: " + str(url_count) + "\n\n\n").encode("utf-8"))

if __name__ == "__main__":
    run_query_program()
    print "Program terminated."
