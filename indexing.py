from bs4 import BeautifulSoup
import os
import nltk

# Note: we should stem and compress index

# Necessary to work around using nltk library
nltk.download('punkt')

#
WEBPAGES_ROOT = "WEBPAGES_CLEAN"
inverted_index = dict()
TOKEN_REGEX_PATTERN = "[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+"

# iterates through webpages directory
def index_webpages(root):
    for dir_name in os.listdir(root):
        dir_path = root + '/' + dir_name
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                file_path = (dir_path + '/' + filename)
                index_file(file_path)


def index_file(file_path):
    if is_not_duplicate(file_path):
        with open(file_path) as file:
            soup = BeautifulSoup(file, "lxml")
            for tag in soup.findAll(True):
                tokens = nltk.regexp_tokenize(tag.text, TOKEN_REGEX_PATTERN)
                update_index(tokens, file_path_to_docid(file_path))


def update_index(tokens, doc_id):
    for token in tokens:
        token = token.lower()
        if len(token) > 1:
            update_posting_list(token, doc_id)



def update_posting_list(token, doc_id):
    if token not in inverted_index:
        inverted_index[token] =  set()
    inverted_index[token].add(doc_id)


def file_path_to_docid(file_path):
    paths = file_path.split('/')
    return paths[1] + "." + paths[2]


def write_index(index_dict):
    with open("index.txt", "w") as index:
        for token in sorted(index_dict):
            index.write((token + ":").encode("utf-8"))
            for doc_id in sorted(index_dict[token]):
                index.write((doc_id + ";").encode("utf-8"))
            index.write(("\n").encode("utf-8"))

def is_not_duplicate(file_path):
    paths = file_path.split('/')
    return len(paths[2]) <= 3


if __name__ == "__main__":
    iterate_through_webpages(WEBPAGES_ROOT)
    write_index(inverted_index)
