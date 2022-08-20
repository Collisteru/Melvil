from typing import Optional
import os
import typer
from datetime import date
import json
import helper as h
import inquirer
from pprint import pprint


TODAY = str(date.today())
app = typer.Typer()

VERSION = "0.3.0"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
STATES = ["Unknown", "To Read", "Reading", "Read", "Reviewed"]
DEFAULT_FILE_NAME = "mortimer.json"

# Mortimer only keeps track of one booklist at a time, but this booklist can be saved anywhere the user wants to save
# it. Mortimer keeps track of where that booklist is saved by saving its path.
# Note that this includes all the information Mortimer needs to find the proper file to edit:

"""
Initialize JSON in location specified by user or, if none, the working directory.
"""
@app.command()
def init():

    # We're going to save the custom location the user provides in a file named config.txt in the same folder
    # as the one the user specifies. Mortimer will search for whatever file is specified in config.txt whenever
    # the time comes.
    def file_validation(answers, current):
        if current.endswith(".json") == False:
            # We allow an empty answer; this just goes to the default location saved in the global variable FILE_NAME.
            if(current == ""):
                return True
            print("Not a valid file name. Please use a .json file.")
            raise inquirer.errors.ValidationError('', reason='Please use a .json file extension.')
        return True

    # Inquire as to the desired location
    questions = [
        inquirer.Text('file_name', message="Please enter the file you would like to designate as the storage file for your books.", validate=file_validation)
    ]
    answers = inquirer.prompt(questions)

    # If no file name is provided, use the current working directory
    if answers["file_name"] == "":
        location = os.getcwd() + "/" + DEFAULT_FILE_NAME
    else:
        # Else use the file name provided by the user. Either way, we initialize the file in the current working directory (TODO: we should refactor this to be more flexible).
        location = os.getcwd() + "/" + answers["file_name"]

    # Initialize book dictionary
    initDict = {}
    initDict['lastEdited'] = TODAY
    initDict['book_list'] = [] # An empty list indicates that no books have been added yet.
    initDict["tag_list"] = []
    json_string = json.dumps(initDict, indent=4)
    os.makedirs(os.path.dirname(location), exist_ok=True)
    with open(location, "w+") as file:
        print(f"New JSON file initialized at {location}")
        file.write(json_string)


# TODO: Check for and eliminate duplicates
# Change this to add flags based on what information the user wants to add. The title is required
# TODO: Change so that you only need to input the title unless you use flags to input more.
@app.command()
def add(
        author: bool = typer.Option(False, "--author", "-a", help="Specify the author of the book"),
        state: bool = typer.Option(False, "--state", "-s", help="Specify what stage you are at in reading this book."),
        priority: bool = typer.Option(False, "--priority", "-p", help="Specify the priority of this book relative to others (changes the ordering of the list)."),
        tags: bool = typer.Option(False, "--tags", "-t", help="Specify whether you would like to add tags to this book now.")
):

    # Capture info about the new book
    author_question = [
        inquirer.Text('book_author',
                      message="What is the author?",
                      )
    ]

    state_question = [
        inquirer.List('state',
                      message="What state is the book in?",
                      choices=STATES,
                      )
    ]

    priority_question = [
        inquirer.Text('priority',
                      message="What is the priority of the book?",
                      validate=h.verify_priority,
                      )
    ]

    tag_number_question = [
        inquirer.Text('tag_num',
                      message="How many tags to add?",
                      validate=h.force_int,
                      )
    ]

    # Define the book as a dictionary, filling in its keys with values depending on what the user has decided
    # to specify with flags.
    book = {}

    # Define title
    title_question = [
        inquirer.Text('title',
                      message="What is the title of the book you want to add?",
                      )
    ]

    title_answer = inquirer.prompt(title_question)
    book['title'] = title_answer['title']

    # Define author, conditional on flag
    if author:
        author_input = inquirer.prompt(author_question)
        book["author"] = author_input["book_author"]
    else:
        book["author"] = ""

    # Define state, conditional on flag
    if state:
        state_input = inquirer.prompt(state_question)
        book["state"] = state_input["state"]
    else:
        book["state"] = "Unknown"

    # Define priority, conditional on flag
    if priority:
        priority_input = inquirer.prompt(priority_question)
        book["priority"] = priority_input["priority"]
    else:
        book["priority"] = "0" # Default to zero priority

    if tags:
        tag_number_input = inquirer.prompt(tag_number_question)
        tag_questions = []

        # We know it's safe to convert the tag_num answer into an integer because force_int passed verification.
        for i in range(int(tag_number_input["tag_num"])):
            tag_questions.append(inquirer.Text(f'tag_{i}', message=f"Tag #{i + 1}?"))

        tag_answers = inquirer.prompt(tag_questions)
        new_tag_list = [value for value in tag_answers.values()]
        book["tags"] = new_tag_list
    else:
        new_tag_list = []
        book["tags"] = []



    # Convert the dictionary to JSON, load the JSON of the file holding the books, append this JSON to the other JSON,
    # and dump it all back into the file.

    # Read mortimer.json to get what's already there.
    old_data = h.read_file()

    # Add new_book to the booklist
    old_book_list = old_data["book_list"]
    old_book_list.append(book)

    # Add new tags to the taglist
    old_tag_set = set(old_data["tag_list"])

    new_tag_set = set(new_tag_list).union(old_tag_set)

    # Update JSON data with new booklist and taglist
    old_data["book_list"] = old_book_list
    old_data["tag_list"] = list(new_tag_set)

    # Write old_data to file
    h.write_file(old_data)

    # Notify user
    if author:
        print(f"{book['title']} by {book['author']} added to the list.")
    else:
        print(f"{book['title']} added to the list.")

"""
Searches the database for a book with this title. Deletes the book with that title or, if there
are no such books, lets the user know this.
(Search is non-fuzzy to prevent accidental deletions.)
"""
@app.command()
def remove():
    question = [
        inquirer.Text('title',
                      message="What is the title of the book you want to remove?",
                      ),
    ]
    answers = inquirer.prompt(question)
    input_title = answers["title"]
    raw_json = h.read_file()

    # raw_json is a dictionary, raw_json["book_list"] is a list of dictionaries
    new_book_list = raw_json["book_list"]
    for bookNum, book in enumerate(raw_json["book_list"]):
        if book["title"] == input_title:
            new_book_list.pop(bookNum)
            break # We only remove the FIRST book matching that title

            # TODO: Provision unique IDs to books so they can have the same titles.
            # If we are at the end of the list, notify the user that there is no book with such a title
        elif ((bookNum + 1) == len(raw_json["book_list"])):
            print("There is no book with such a title in your list.")
            return
    raw_json["book_list"] = new_book_list
    h.write_file(raw_json)

"""
Prints the contents of the list in order of greatest-to-least priority.
"""
@app.command()
# TODO: Add flag to show priority too.
def flip(helper: bool=False):
    raw_json = h.read_file()

    book_list = raw_json["book_list"]
    new_list = sorted(book_list, key=lambda d: int(d['priority']), reverse=True)

    # Sometimes, we want to use this function internally to get a title catalog.
    # In these cases, we don't want to print the list to the user.
    if not helper:
        for book in new_list:
            if book["author"]:
                print(book["title"] + " by " + book["author"])
            else:
                print(book["title"])

    return new_list # Can we use this as a helper for other commands?

"""
Changes the status of target book to target status.
Ugh, this is going to be a nightmare to test.
"""
@app.command()
def advance():
    # Key Error title
    title_question = [
        inquirer.Text('title',
                      message="What is the title of the book you want to change the status of?",
                     )
    ]
    # Use fuzzy search to figure out which book the user is asking for, then tell them what we've found
    # and ask them to choose the new state.

    asked_title_question = inquirer.prompt(title_question)
    target_book = asked_title_question["title"]

    # Get the index of the target book
    raw_json = h.read_file()
    try:
        book_index = h.fuzzy_search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]
    print("book: ", book)

    # KeyError... title?
    state_question = [
        inquirer.List('state',
                      message=f"Change {book['title']} to which target state?",
                      choices=STATES,
                      ),
    ]

    asked_state_question = inquirer.prompt(state_question)
    target_state = asked_state_question["state"]

    book["state"] = target_state
    raw_json["book_list"][book_index] = book
    assert(type(raw_json) == dict)

    h.write_file(raw_json)
    print(f"Changed the status of {book['title']} to {target_state}")
    return

"""
Lists all the attributes of the single input book.
"""
@app.command()
def skim():
    question = [
        inquirer.Text('title',
                      message="Which book would you like to skim?",
                      ),
    ]
    answers = inquirer.prompt(question)
    target_book = answers["title"]
    raw_json = h.read_file()

    try:
        book_index = h.fuzzy_search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    book = raw_json["book_list"][book_index]
    print(f"Skimming the closest match {book['title']}:\n")
    book_keys = book.keys()
    book_values = book.values()
    keys_to_values = zip(book.keys(), book.values())
    for pair in keys_to_values:
        print(f"{pair[0]}: {pair[1]}")


"""
Changes the status of target book to target status.
"""
@app.command()
def prioritize():

    # Get the index of the target book
    title_question = [
        inquirer.Text('title',
                      message="Which book would you like to prioritize?",
                      ),
    ]

    # Use fuzzy search to figure out which book the user is asking for, then tell them what we've
    # found and ask them to choose the new state.
    asked_title_question = inquirer.prompt(title_question)

    # Get the index of the target book
    raw_json = h.read_file()
    try:
        book_index = h.fuzzy_search_booklist(asked_title_question, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]

    priority_question = [
        inquirer.Text('priority',
                      message=f"What priority would you like to set {book['title']} to?",
                      validate=h.verify_priority, )
    ]

    asked_priority_question = inquirer.prompt(priority_question)
    target_priority = asked_priority_question["priority"]

    book["priority"] = target_priority

    # Change the priority of the target title to the target priority
    book = raw_json["book_list"][book_index]
    book["priority"] = target_priority

    h.write_file(raw_json)

    return

"""
Adds the target tag to the target book.
"""
@app.command()
def tag():
    title_question = [
        inquirer.Text('title',
                      message="Which book would you like to tag?",
                      ),
        ]

    target_book = inquirer.prompt(title_question)["title"]

    # Get the index of the book with the nearest title to the one we've typed in.
    raw_json = h.read_file()
    try:
        book_index = h.fuzzy_search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return
    book = raw_json["book_list"][book_index]

    # Let the user know which book we've selected as the closest match and have them choose which tags to add.
    tag_question = [
        inquirer.Text('tag',
                      message=f"What tag would you like to add to the closest title match, {book['title']}?",
                      ),
    ]

    tag_answer = inquirer.prompt(tag_question)
    tag_to_add = tag_answer["tag"]

    # Add the target tag to the target title
    book["tags"].append(tag_to_add)
    h.write_file(raw_json)
    print(f"Added the tag {tag_to_add} to target book {book['title']}.")

"""
Removes the target tag from the target book.
"""
@app.command()
def untag():
    title_question = [
        inquirer.Text('title',
                      message="Which book would you like to untag?",
                      ),
        ]

    title_answer = inquirer.prompt(title_question)["title"]
    raw_json = h.read_file()

    try:
        book_index = h.fuzzy_search_booklist(title_answer, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return
    target_book = raw_json["book_list"][book_index]

    tag_question = [
        inquirer.Text('tag',
                      message=f"What tag would you like to remove from the closest title match, {target_book['title']}?",
                      ),
    ]

    tag_answer = inquirer.prompt(tag_question)
    target_tag = tag_answer["tag"]

    # We have the target tag and the target book.
    # Now, search the booklist for
    for tag in target_book["tags"]:
        if tag.strip() == target_tag:
            target_book["tags"].remove(target_tag)
            new_taglist = target_book["tags"]
            raw_json["book_list"][book_index]["tags"] = new_taglist
            h.write_file(raw_json)
            print(f"Removed tag {target_tag} from {target_book['title']}")
            return
    print(f"{target_tag} isn't a tag of {target_book['title']}")

"""
Search by title: Fuzzy search returns all the book titles that roughly match your target by sifting the results of flip.
"""
@app.command()
def lookup():
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
    print(f"These are the {num_results} titles that most closely match your query: ")
    for result in range(num_results):
        top_result_index = int(h.fuzzy_search_booklist(search_query, book_catalog))
        top_result = title_catalog[top_result_index]
        print(top_result)
        book_catalog.pop(top_result_index)

"""
Search by tag functionality. 


Figure out what tag the user wants in a robust way by creating an ordered lists of tags by greatest-to-least
Levenshtein distance from the given query.

We just fuzzy search the set based on the user's query and select the topmost tag. Then we iterate over the list of books that have that tag
, and then we spit out all the titles that include such tags attached to them.
"""
@app.command()
def compile():
    search_query = input("Which tag would you like to search for? ")

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    tag_catalog = raw_json["tag_list"]
    tag_to_levenshtein = {tag: h.fuzz.ratio(search_query, tag) for tag in tag_catalog}
    sorted_tag_to_catalog = {k: v for k, v in sorted(tag_to_levenshtein.items(), key=lambda item: item[1])}
    target_tag = sorted_tag_to_catalog.popitem()[0]

    books_with_target_tag = []
    for book in book_catalog:
        try:
            if target_tag in book["tags"]:
                books_with_target_tag.append(book["title"])
        except:
            # This book has no tags. Nothing to worry about.
            continue

    print(f"These are the books with the tag {target_tag}: ")
    for book in books_with_target_tag:
        print(book)


"""
Delete all the books in the list and the corresponding list of global tags. Not to be used lightly!
"""
@app.command()
# TODO: Make the text red.
def delete():
    OPTIONS = ["Yes", "No"]

    question = [
        inquirer.Text('confirmation',
                      message="WARNING: This action will delete ALL The Books in your list. Are you sure you want to do this? (Yes/No)",
                      ),
    ]
    to_exterminate = inquirer.prompt(question)["confirmation"]

    if to_exterminate == "Yes" or to_exterminate == "yes" or to_exterminate == "Y" or to_exterminate == "y":
        raw_json = h.read_file()
        raw_json["book_list"] = []
        raw_json["tag_list"] = []
        h.write_file(raw_json)
        print("All books and tags have been deleted.")
    else:
        print("Action aborted.")

if __name__ == "__main__":
      app()
