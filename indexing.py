from bs4 import BeautifulSoup
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
from io import open # IO is specifically for handling unicode encoded files

# Note: we should stem and compress index

# Necessary to work around using nltk library
nltk.download('punkt')
nltk.download('stopwords')

# Global variables
WEBPAGES_ROOT = "WEBPAGES_CLEAN"
inverted_index = dict()
token_freqs = dict() # token : {doc_id: [base_score, freq]}
TOKEN_REGEX_PATTERN = "[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+"
tag_score_multiplier = { # Base multipliers for various HTML tags. Used for ranked retrieval
        'b':1.5,
        'body': 1,
        'h1': 1.2,
        'h2': 1.2,
        'h3': 1.2,
        'strong': 1.4
    }

# iterates through webpages directory and updates the inverted index
# dictionary's tokens with the docID that the token was found in
def index_webpages(root):
    for dir_name in os.listdir(root):
        dir_path = root + '/' + dir_name
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                file_path = (dir_path + '/' + filename)
                index_file(file_path)

# takes all of the text in the file of the given path
# tokenizes the text and updates the index dictionary
def index_file(file_path):
    if is_not_duplicate(file_path):
        with open(file_path, encoding='utf8') as file:
            soup = BeautifulSoup(file, "lxml")
            stemmer = SnowballStemmer("english", ignore_stopwords=True) # Stopwords are useless/ common words

            for tag in soup.findAll(True):
                tokens = nltk.regexp_tokenize(tag.text, TOKEN_REGEX_PATTERN)
                tokens = [stemmer.stem(token) for token in tokens] # Stem all the tokens

                update_index(tokens, file_path_to_docid(file_path), get_tag_score_multiplier(tag.name))

# given a list of tokens, updates index dictionary using
# update_posting_list helper method
def update_index(tokens, doc_id, tag_multiplier):
    for token in tokens:
        token = token.lower()
        if len(token) > 1:
            update_posting_list(token, doc_id)
            update_token_frequency(token, doc_id, tag_multiplier)

# manipulates the inverted index dictionary to add a docID
# to posting list of token
def update_posting_list(token, doc_id):
    if token not in inverted_index:
        inverted_index[token] =  set()
    inverted_index[token].add(doc_id)

def update_token_frequency(token, doc_id, tag_multiplier):
    # Updates the token frequency in the inverted index
    posting_list = token_freqs.setdefault(token, {doc_id: [tag_multiplier, 0]}) # Set with default posting list
    doc_meta_info = posting_list.get(doc_id, [tag_multiplier, 0]) # Get with default doc info
    doc_meta_info[-1] += 1
    posting_list[doc_id] = doc_meta_info
    token_freqs[token] = posting_list

# given the full path of a document, it produces a docID
# formatted in a string for the index
def file_path_to_docid(file_path):
    paths = file_path.split('/')
    return paths[1] + "." + paths[2]

# writes inverted index dictionary to a file in a parse-able format
# token is separated from its posting list by ":"
# each doc in posting list is separated by ";"
# Format>>: Token:doc_freq|doc_id-multiplier-token_freq;doc_id-multiplier-token_freq,....
def write_index(index_dict):
    with open("index.txt", "wb") as index:
        index.write(str(len(index_dict)) + "\n") # Write index size header

        for token in sorted(index_dict):
            index.write((token + ":" + str(get_doc_freq(token)) + "|").encode("utf-8")) # Write Token:doc_freq-

            for doc_id in sorted(index_dict[token]):
                index.write((doc_id + "-" + str(get_token_doc_multiplier(token,doc_id)) + "-" # Write doc_id-multiplier-
                             + str(get_token_freq(token, doc_id)) + ";").encode("utf-8"))     # Write token_freq;
            index.write(("\n").encode("utf-8")) # Write newline


# check to see if the document is not a duplicate given its file path
# specific for the format of this assignment (file name is never more than 3 characters long)
def is_not_duplicate(file_path):
    paths = file_path.split('/')
    return len(paths[2]) <= 3


def get_tag_score_multiplier(tag):
    #param: html tag str (not BeautifulSoup's Tag obj). Default tag multiplier = 1
    # Gets the multiplier for scoring text in certain HTML tags
    return tag_score_multiplier.get(tag, 1)

def get_token_doc_multiplier(token, doc_id):
    # Gets the current multiplier for a token and document
    posting_list = token_freqs.get(token,  {}) # Default empty dict
    doc_meta_info = posting_list.get(doc_id, [1, 0]) #  default value = [tag_multiplier, token freq]
    return doc_meta_info[0]

def get_token_freq(token,doc_id):
    # Gets the token frequency for a token and document
    posting_list = token_freqs.get(token, {}) # Default empty dict
    doc_meta_info = posting_list.get(doc_id, [1, 0])  # Default value = [tag_multiplier, token freq]
    return doc_meta_info[-1]

def get_doc_freq(token):
    # Gets the document frequency of a token
    posting_list = token_freqs.get(token, {})  # Default empty dict
    return len(posting_list)

if __name__ == "__main__":
    index_webpages(WEBPAGES_ROOT)
    write_index(inverted_index)
