from bs4 import BeautifulSoup
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
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
        'p': 3, # BeautifulSoup puts the tag-less title into the body and a paragraph tag;
        'b':1.5,
        'body': 1,
        'h1': 1.2,
        'h2': 1.2,
        'h3': 1.2,
        'strong': 1.4
    }
HTML_TAGS = ['p', 'b', 'body', 'h1', 'h2', 'h3', 'strong']

# iterates through webpages directory and updates the inverted index
# dictionary's tokens with the docID that the token was found in
def index_webpages(root):
    for dir_name in os.listdir(root):
        dir_path = root + '/' + dir_name
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                file_path = (dir_path + '/' + filename)
            #file_path = ('WEBPAGES_CLEAN/0/155') # Test cases: /0/40, /0/43, /0/155
                index_file(file_path)

# takes all of the text in the file of the given path
# tokenizes the text and updates the index dictionary
def index_file(file_path):
    if is_not_duplicate(file_path):
        with open(file_path, encoding='utf8') as file:
            soup = BeautifulSoup(file, "lxml")
            stemmer = SnowballStemmer("english", ignore_stopwords=True) # Stopwords are useless/ common words; Don't stem
            stop_words = set(stopwords.words('english'))

            num_title_tokens = None

            for html_tag in HTML_TAGS:

                if html_tag == 'p':
                    # BeautifulSoup fixes broken html (missing opening <body> tag) by putting everything into <p> and <body> tag
                    # Avoid parsing both <p> and <body> tags if they are duplicates
                    p_soup =  soup.find('p')
                    body_soup = soup.find('body')
                    if p_soup is not None and body_soup is not None and p_soup.text == body_soup.text:
                        continue

                for tag in soup.findAll(html_tag):
                    tokens = nltk.regexp_tokenize(tag.text, TOKEN_REGEX_PATTERN)
                    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words] # Stem all the tokens that arent stop words

                    if html_tag == 'p': # if tokens are part of title
                        num_title_tokens = len(tokens)

                    elif html_tag == 'body' and num_title_tokens is not None:
                        tokens = tokens[num_title_tokens:] # Remove beginning duplicate title <p> tokens from <body> tokens

                    #print(tag.name)
                    #print tokens
                    update_index(tokens, file_path_to_docid(file_path), get_tag_score_multiplier(html_tag))

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
    if tag_multiplier > posting_list.get(doc_id, [tag_multiplier, 0])[0]:
        posting_list[0] = tag_multiplier # Update tag multiplier if current is greater than previous
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
# Format>>:
# index_size(num lines)
# Token:doc_freq|doc_id-multiplier-token_freq;doc_id-multiplier-token_freq,....
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
# specific for the format of this assignment (file name is never more than 3 characters long) TEST
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
