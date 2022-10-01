# A file containing functions related to search

STATES = ["Unknown", "To Read", "Reading", "Read", "Reviewed"]
# Import appFile from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect
import regex

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project")

from melvil_booklist import app, FUZZY_RATIO_THRESHOLD
from helper import helper as h

sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project/")
import typer

# TODO: Possibly make this a scrollable list of the list ordered by reverse Levenshtein distance. Until then, keep the fraction of listed books high.
@app.command()
def lookup(input_string="", helper=False):
    """
    Search by title.
    """

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    if helper == True:
        top_result_index = int(h.fuzzy_search_booklist(input_string, book_catalog))
        return top_result_index
    else:
        import inquirer
        question = [
            inquirer.Text('title',
                          message="Which book would you like to look up?",
                          ),
        ]
        try:
            answers = h.safe_prompt(question)
        except:
            print("Empty input. Exiting.")
            quit()
        search_query = answers["title"]

        title_catalog = [book["title"] for book in book_catalog]

        num_results = min(10, round(h.SEARCH_FRACTION*len(book_catalog)))

        titles_ordered_by_distance = h.superstring_finder(search_query, title_catalog)

        print(f"Top {num_results} results:")
        for i in range(num_results):
            print(f"{list(titles_ordered_by_distance.keys())[i]}")

@app.command()
def compile():
    """
    Search by tag
    """
    search_query = typer.prompt("Which tag would you like to search by?")

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    # Get tag catalog
    tag_catalog = raw_json["tag_list"]

    list_target_tags = h.superstring_finder(search_query, tag_catalog)

    target_tag = list(list_target_tags.keys())[0]
    print(f"Choosing target tag {target_tag}")

    books_with_target_tag = []
    for book in book_catalog:
        try:
            if target_tag in book["tag_list"]:
                books_with_target_tag.append(book["title"])
        except:
            # This book has no tags. Nothing to worry about.
            continue

    print(f"The following books have the tag {target_tag}: ")
    for book in books_with_target_tag:
        print(book)