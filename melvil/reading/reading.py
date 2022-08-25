# Manages which books you are reading now.

# At this point, though, creating a hierarchy of literature might be nice, so that when we tag a site all the children receive
# the same tags, too.

# Once again though, that would be hard to implement. Keep it simple, we're not geniuses, here.

# Okay, here's what we're going to do:
from helper import helper as h
import os
import inspect
import sys
import subprocess
from collections import OrderedDict
from thefuzz import fuzz

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil")

from app import app # Type not yet supported: class 'list'


# Create a function that delivers the book you're currently reading. This is just the highest-priority book with the to-read ## tag.

# Create a function that delivers the book you want to read next. This is the highest-priority book with the "to-read" tag.
# Imports all the websites of a given subdomain. This is good
## for looking up blog catalogs. You'll want to try this with WordPress blogs, LessWrong, other website, etc.
## Basically, try it with all the websites you've posted on your own website.
# Import all the articles from that subdomain.
@app.command()
def surf():
    subdomain_question = [
        inquirer.Text("Enter the URL prefix to take articles from. You should enter the prefix ending with a * that Melvil will replace with websites in that doman. For example, 'https;//en.wikipedia.org/*' would fill in with 'https://en.wikipedia.org/a, https://en.wikpedia.org/b, etc.'")
    ]
    subdomain = inquirer.prompt(subdomain_question)

    print(f"Searching for all websites in {subdomain}: ")


# TODO: WRITE AND TEST SUBPROCESS CALL WHEN YOU HAVE ACCESS TO THE INTERNET AGAIN.

# This function delivers the book you want to read next, which is defined as the book with the highest priority and the TO-READ
# state. If there are no books in the list with the TO-READ state, then the function just delivers
# the highest-priority book in the index, with books with undefined priority ranking last.
# If all books have no priority and are not to-read, this function just delivers the first book in an alphabetical sequence.
@app.command() # Type not supported goes somewhere in here.
def next(): # Type not supported: class 'list'. Wat!?

    # Commence fuzzy search.

    # Create an ordered list of book titles by least-to-greatest Levenshtein distance
    # from the given query.
    raw_json = h.read_file()


    unordered_book_list = raw_json["book_list"]

    ordered_book_list = sorted(unordered_book_list, key=lambda k: k['priority'])

    # ^^ Could have just used flip for the above, hehehe.


    try:
        general_first = ordered_book_list[0]
    except:
        print("No books to read. Try adding a book with 'add'.")
        return


    for book in ordered_book_list:
        if book['state'] == "To Read":
            print(f"Found a book to read: {book['title']}")
            return

    print(f"Found a book to read: {book['title']}")
    # If none of the books in the list have the to_read state, we must deliver general_first.
    # Otherwise, we must deliver the highest priority book with  the to read state.

# This function delivers the book you're currently reading, which is defined as the book with the highest priority in the READING state.
@app.command()
def reading():
    raw_json = h.read_file()

    unordered_book_list = raw_json["book_list"]

    ordered_book_list = sorted(unordered_book_list, key=lambda k: k['priority'])

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
        print("You're not currently reading anything. Try adding a book with 'add', or finding a book to read with 'next'.")
    except:
        print("No books are in the booklist. Try adding a book with 'add'.")
        return