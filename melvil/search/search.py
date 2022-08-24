# A file containing functions related to search
from main import STATES
import helper as h

# Import app from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil")


from app import app


import typer

# TODO: Possibly make this a scrollable list of the list ordered by reverse Levenshtein distance. Until then, keep the fraction of books listed high.
@app.command()
def lookup():
    """
    Search for a book by title.
    """
    question = [
        inquirer.Text('title',
                      message="Which book would you like to look up?",
                      ),
    ]
    answers = inquirer.prompt(question)
    search_query = answers["title"]

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]
    title_catalog = [book["title"] for book in book_catalog]

    num_results = max(1, round(h.SEARCH_FRACTION*len(book_catalog)))
    if num_results == 1:
        print(f"This title most closely matches your query:")
    else:
        print(f"These are the {num_results} titles that most closely match your query: ")
    for result in range(num_results):
        top_result_index = int(h.fuzzy_search_booklist(search_query, book_catalog))
        top_result = title_catalog[top_result_index]
        print(top_result)
        book_catalog.pop(top_result_index)