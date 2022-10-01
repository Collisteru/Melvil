# Manages which books you are reading now.

# At this point, though, creating a hierarchy of literature might be nice, so that when we tag a site all the children receive
# the same tags, too.

# Once again though, that would be hard to implement. Keep it simple, we're not geniuses, here.

# Okay, here's what we're going to do:
from melvil_booklist import app
from helper import helper as h
import os
import inspect
import sys
import subprocess
from collections import OrderedDict
from thefuzz import fuzz

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project")

import inquirer

# Going to try this one:
# https://python.plainenglish.io/scraping-the-subpages-on-a-website-ea2d4e3db113

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json


# If there are no books in the list with this state, then the function just delivers the highest-priority book
# in the index, with a book with undefined priority ranking last. If all books have no priority and are not to-read,
# this function just delivers the first book in an alphabetical sequence.
@app.command() # Type not supported goes somewhere in here.
def next(): # Type not supported: class 'list'.
    """
    Delivers the book you want to read next, defined the book with the highest priority and the "to-read" state.
    """

    # Commence fuzzy search.

    # Create an ordered list of book titles by least-to-greatest Levenshtein distance
    # from the given query.
    raw_json = h.read_file()

    unordered_book_list = raw_json["book_list"]

    ordered_book_list = sorted(unordered_book_list, key=lambda k: int(k['priority']))

    try:
        general_first = ordered_book_list[0]
    except:
        print("No books to read. Try adding a book with 'add'.")
        return


    for book in ordered_book_list:
        if book['state'] == "To Read":
            print(f"Found a book to read: {book['title']}")
            return


    # If none of the books have the to-read state, state this frankly.
    print(f"You haven't designated any books as 'to-read', but the work with the highest priority overall is \x1B[3m{general_first['title']}\x1B[0m")

@app.command()
def reading():
    """
    Delivers the book you are reading now, defined as the book with the highest priority in the reading states.
    """

    raw_json = h.read_file()

    unordered_book_list = raw_json["book_list"]

    ordered_book_list = sorted(unordered_book_list, key=lambda k: int(k['priority']))


    # TODO: ^^' Could have just used flip for the above, hehehe.
    try:
        general_first = ordered_book_list[0]
    except:
        print("No books to read. Try adding a book with 'add'.")
        return

    try:
        for book in ordered_book_list:
            if book['state'] == "To Read":
                print(f"Found the book you're currently reading: {book['title']}")
                return
        print("You aren't reading anything right now. Try adding a book with 'add' or finding a book to read with 'next'.")
    except:
        print("No books are in the booklist. Try adding a book with 'add'.")
        return