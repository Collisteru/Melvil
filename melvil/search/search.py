# A file containing functions related to search

STATES = ["Unknown", "To Read", "Reading", "Read", "Reviewed"]
# Import app from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil")

from main import app, FUZZY_RATIO_THRESHOLD
from helper import helper as h

sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil/")
import typer


# TODO: Possibly make this a scrollable list of the list ordered by reverse Levenshtein distance. Until then, keep the fraction of books listed high.
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
        answers = inquirer.prompt(question)
        search_query = answers["title"]

        title_catalog = [book["title"] for book in book_catalog]

        num_results = max(1, round(h.SEARCH_FRACTION*len(book_catalog)))

        # This only lists titles with a certain maximum fuzzy distance ratio between themselves and the target query.
        # It says different things depending on whether there is only one result or many.
        if (h.fuzz.ratio(search_query, title_catalog[0]) < FUZZY_RATIO_THRESHOLD):
            print("There aren't any titles that closely match your query. Use the 'list' command to see all titles.")
            return
        else:
            if num_results == 1:
                print(f"This title most closely matches your query:")
                print(title_catalog[0])
            else:
                for result in range(num_results):
                    top_result_index = int(h.fuzzy_search_booklist(search_query, book_catalog))
                    top_result = title_catalog[top_result_index]
                    if (h.fuzz.ratio(top_result, search_query) < FUZZY_RATIO_THRESHOLD):
                        return
                    else:
                        print(top_result)
                        book_catalog.pop(top_result_index)





@app.command()
def compile():
    """
    Search by tag
    """
    search_query = input("Which tag would you like to search for? ")

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    # Get tag catalog
    tag_catalog = raw_json["tag_list"]
    tag_to_levenshtein = {tag: h.fuzz.ratio(search_query, tag) for tag in tag_catalog}
    sorted_tag_to_catalog = {k: v for k, v in sorted(tag_to_levenshtein.items(), key=lambda item: item[1])}

    target_tag = sorted_tag_to_catalog.popitem()[0]

    # Fuzzy Distance Limit
    print(f"search_query: {search_query}")
    print(f"target_tag: {target_tag}")
    if (h.fuzz.ratio(search_query, target_tag) < FUZZY_RATIO_THRESHOLD):

        print("There aren't any tags that closely match your query. Use the 'classify' command to see a list of all available tags.")
        return

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