from bs4 import BeautifulSoup
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
# Note: we should stem and compress index

# Necessary to work around using nltk library
nltk.download('punkt')
nltk.download('stopwords')

# Global variables
WEBPAGES_ROOT = "WEBPAGES_CLEAN"
inverted_index = dict()
TOKEN_REGEX_PATTERN = "[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+"

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
        with open(file_path) as file:
            soup = BeautifulSoup(file, "lxml")
            stemmer = SnowballStemmer("english", ignore_stopwords=True)
            for tag in soup.findAll(True):
                tokens = nltk.regexp_tokenize(tag.text, TOKEN_REGEX_PATTERN)
                tokens = [stemmer.stem(token) for token in tokens]

                update_index(tokens, file_path_to_docid(file_path))

# given a list of tokens, updates index dictionary using
# update_posting_list helper method
def update_index(tokens, doc_id):
    for token in tokens:
        token = token.lower()
        if len(token) > 1:
            update_posting_list(token, doc_id)

# manipulates the inverted index dictionary to add a docID
# to posting list of token
def update_posting_list(token, doc_id):
    if token not in inverted_index:
        inverted_index[token] =  set()
    inverted_index[token].add(doc_id)

# given the full path of a document, it produces a docID
# formatted in a string for the index
def file_path_to_docid(file_path):
    paths = file_path.split('/')
    return paths[1] + "." + paths[2]

# writes inverted index dictionary to a file in a parse-able format
# token is separated from its posting list by ":"
# each docID in posting list is separated by ";"
def write_index(index_dict):
    with open("index.txt", "w") as index:
        for token in sorted(index_dict):
            index.write((token + ":").encode("utf-8"))
            for doc_id in sorted(index_dict[token]):
                index.write((doc_id + ";").encode("utf-8"))
            index.write(("\n").encode("utf-8"))

# check to see if the document is not a duplicate given its file path
# specific for the format of this assignment (file name is never more than 3 characters long)
def is_not_duplicate(file_path):
    paths = file_path.split('/')
    return len(paths[2]) <= 3


if __name__ == "__main__":
    index_webpages(WEBPAGES_ROOT)
    write_index(inverted_index)
