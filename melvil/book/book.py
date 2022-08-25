
# A file for commands that affect a single book.
from helper import helper as h

# Import app from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil")

from app import app

STATES = ["Unknown", "To Read", "Reading", "Read", "Reviewed"]

import typer
import inquirer

# TODO: Change so that a new file is written containing the title of the file you want to use.
@app.command()
def add(
        author: bool = typer.Option(False, "--author", "-a", help="Specify the author of the book"),
        state: bool = typer.Option(False, "--state", "-s", help="Specify what stage you are at in reading this book."),
        priority: bool = typer.Option(False, "--priority", "-p", help="Specify the priority of this book relative to others (changes the ordering of the list)."),
        tags: bool = typer.Option(False, "--tags", "-t", help="Specify whether you would like to add tags to this book now."),
        custom: bool = typer.Option(False, "--custom", "-c", help="Add your own field to the book.")
):
    """
    Add a book.
    """

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

    custom_field_question = [
        inquirer.Text('custom_field_name',
                      message="What custom field would you like to add?",
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

    try:
        book['title'] = title_answer['title']
    except:
        print("Empty title, aborting.")
        sys.exit(0)

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

        # Right now we have two problems: The loop loops doubly so that we have nine
        # total iterations instead of three, and we get an error when we try to take
        # tag_answers.values(). I think we can solve both of these on this very bus!

        # We know it's safe to convert the tag_num answer into an integer because force_int passed verification.
        for i in range(int(tag_number_input["tag_num"])):
            tag_questions.append(inquirer.Text(f'tag_{i}', message=f"Tag #{i + 1}?"))

        tag_answers = inquirer.prompt(tag_questions)
        new_tag_list = [value for value in tag_answers.values()]
        book["tags"] = new_tag_list
    else:
        new_tag_list = []
        book["tags"] = []


    if custom:
        custom_field_input = inquirer.prompt(custom_field_question)
        custom_field_value = [
            inquirer.Text('custom_field_value',
                          message=f"What value should we add to the custom field {custom_field_input['custom_field_name']}?"
                          )
        ]

    # Convert the dictionary to JSON, load the JSON of the file holding the books, append this JSON to the other JSON,
    # and dump it all back into the file.

    # Read melvil.json to get what's already there.
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

@app.command()
def attribute():
    """
    Add an author to a book.
    """
    # Get the title of the target book
    title_question = [
        inquirer.Text('title',
                      message="What is the title of the book you want to change the author of?",
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

    attribute_question = [
        inquirer.Text('attribute',
                      message="What author do you want to add to this book?",
                      )
    ]

    attribute_answer = inquirer.prompt(attribute_question)
    book["author"] = attribute_answer["attribute"]
    h.write_file(raw_json)

@app.command()
def remove():
    """
    Remove a book.
    """
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

@app.command()
def prioritize():
    """
    Change priority of a single book in the list.
    """
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

@app.command()
def tag():
    """
    Tag a book that's already in the list. If that tag isn't in the tag catalog yet,
    add it to the tag catalog.
    """
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

    # Ask the user how many tags they would like to add
    tag_number_question = [
        inquirer.Text(
            'tag_num',
            message=f"How many tags would you like to add to the closest title match, {book['title']}?",
            validate= h.force_int
        ),
    ]
    tag_number_input = inquirer.prompt(tag_number_question)


    # Create a number of tag questions equal to the number of tags the user wants.
    tag_questions = []
    for i in range(int(tag_number_input["tag_num"])):
        tag_questions.append(inquirer.Text(f'tag_{i}', message=f"Tag #{i + 1}?"))

    # TPrompt the user
    tag_answers = inquirer.prompt(tag_questions)

    # Fill in the new tag list with the user's desired tags.
    new_tag_list = [value for value in tag_answers.values()]
    print("new_tag_list: ", new_tag_list)

    # Add these tags to the book and to the tag catalog if they aren't already in the tag catalog
    for new_tag in new_tag_list:
        book["tags"].append(new_tag)
        if not (new_tag in raw_json["tag_list"]):
            raw_json["tag_list"].append(new_tag)

    # Write and report to user.
    h.write_file(raw_json)
    print(f"Added the following tags to target book {book['title']}.")
    for tag in new_tag_list:
        print(tag)

@app.command()
def untag():
    """
    Remove a tag from a book that's already in the list.
    """
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

    # List tags the book already has for the user's convenience
    if target_book["tags"] == []:
        print(f"{target_book['title']} doesn't have any tags to remove, silly!")
        return
    else:
        print(f"The following tags are in the closest match {target_book['title']}")
        for tag in target_book["tags"]:
            print(tag)

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

@app.command()
def skim():
    """
    List attributes of one book.
    """
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

@app.command()
def advance():
    """
    Change book status.
    """
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
        # Change the state of the target title to the target state
        book = raw_json["book_list"][book_index]
        print(f"The closest title match is {book['title']}")
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]

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