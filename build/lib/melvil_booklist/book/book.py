# A file for commands that affect a single book.
from helper import helper as h
from search import search as s

# Import appFile from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project")

from melvil_booklist import app

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
):
    """
    Add a book. Use 'add --help' for more info.
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

    # Define the book as a dictionary, filling in its keys with values depending on what the user has decided
    # to specify with flags.
    book = {}

    # Define title
    title_question = [
        inquirer.Text('title',
                      message="What is the title of the book you want to add?",
                      )
    ]

    title_answer = h.safe_prompt(title_question)
    book['title'] = title_answer['title']

    # Define author, conditional on flag
    if author:
        author_input = h.safe_prompt(author_question)
        book["author"] = author_input["book_author"]
    else:
        book["author"] = ""

    # Define state, conditional on flag
    if state:
        state_input = h.safe_prompt(state_question)
        book["state"] = state_input["state"]
    else:
        book["state"] = "Unknown"

    # Define priority, conditional on flag
    if priority:
        priority_input = h.safe_prompt(priority_question)
        book["priority"] = priority_input["priority"]
    else:
        book["priority"] = "0" # Default to zero priority

    if tags:
        tag_number_input = h.safe_prompt(tag_number_question)
        tag_questions = []

        # We know it's safe to convert the tag_num answer into an integer because force_int passed verification.
        for i in range(int(tag_number_input["tag_num"])):
            tag_questions.append(inquirer.Text(f'tag_{i}', message=f"Tag #{i + 1}?"))

        tag_answers = h.safe_prompt(tag_questions)
        new_tag_list = [value for value in tag_answers.values()]

        # Extend the book's own list of tags with this new taglist
        try:
            for new_tag in new_tag_list:
                if not new_tag in book["tag_list"]:
                    book["tag_list"].append(new_tag)
        except: # Triggers in the case that book was never initialized with a tag list
            book["tag_list"] = new_tag_list

    else:
        new_tag_list = []
        book["tag_list"] = []


    """
    if custom:
        custom_field_input = h.safe_prompt(custom_field_question)
        custom_field_value = [
            inquirer.Text('custom_field_value',
                          message=f"What value should we add to the custom field {custom_field_input['custom_field_name']}?"
                          )
        ]
    """

    # Convert the dictionary to JSON, load the JSON of the file holding the books, append this JSON to the other JSON,
    # and dump it all back into the file.

    # Read Melvil_Project.json to get what's already there.
    old_data = h.read_file()

    # Add new_book to the booklist
    old_book_list = old_data["book_list"]
    old_book_list.append(book)

    # Add new tags to the taglist, making sure to avoid adding in duplicates
    old_tag_list = old_data["tag_list"]
    for new_tag in new_tag_list:
        if not new_tag in old_tag_list:
            old_tag_list.append(new_tag)

    # Update JSON data with new booklist and taglist
    old_data["book_list"] = old_book_list
    old_data["tag_list"] = list(old_tag_list)

    # Write old_data to file
    h.write_file(old_data)

    # Notify user
    if author:
        print(f"{book['title']} by {book['author']} added to the list.")
    else:
        print(f"{book['title']} added to the list.")




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
    answers = h.safe_prompt(question)
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
def untag():
    """
    Remove a tag from a book that's already in the list.
    """
    title_question = [
        inquirer.Text('title',
                      message="Which book would you like to untag?",
                      ),
    ]

    title_answer = h.safe_prompt(title_question)["title"]
    raw_json = h.read_file()

    try:
        book_index = h.fuzzy_search_booklist(title_answer, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return
    target_book = raw_json["book_list"][book_index]

    # List tags the book already has for the user's convenience
    if target_book["tag_list"] == []:
        print(f"{target_book['title']} doesn't have any tags to remove, silly!")
        return
    else:
        print(f"The following tags are in the closest match {target_book['title']}")
        for tag in target_book["tag_list"]:
            print(tag)

    tag_question = [
        inquirer.Text('tag',
                      message=f"What tag would you like to remove from the closest title match, {target_book['title']}?",
                      ),
    ]

    tag_answer = h.safe_prompt(tag_question)
    target_tag = tag_answer["tag"]

    # We have the target tag and the target book.
    # Now, search the booklist for
    for tag in target_book["tag_list"]:
        if tag.strip() == target_tag:
            target_book["tag_list"].remove(target_tag)
            new_taglist = target_book["tag_list"]

            # Make sure to remove this tag from the JSON taglist as well
            old_master_taglist = raw_json["tag_list"]
            try:
                raw_json["tag_list"].remove(target_tag)
            except:
                print("This tag wasn't found in the master taglist, so there's probably a bug either in add or transcribe.")
                pass



            # Write the new json to the file
            raw_json["book_list"][book_index]["tag_list"] = new_taglist
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
    answers = h.safe_prompt(question)
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
def change(
        title: bool = typer.Option(False, "--title", "-i"),
        author: bool = typer.Option(False, "--author", "-a", help="Specify the author of the book"),
        state: bool = typer.Option(False, "--state", "-s", help="Specify what stage you are at in reading this book."),
        priority: bool = typer.Option(False, "--priority", "-p",
                                      help="Specify the priority of this book."),
        tags: bool = typer.Option(False, "--tags", "-t",
                                  help="Tag this book."),
):
    """
    Change one or more of a book's attributes. Use 'change --help' for more.
    """
    # The user needs to use this with at least one command flag.
    if not (title | author | state | priority | tags):
        explanation_string = """
            Please specify which fields to add to the book with a flag on the change command, like this:
            -a, --author --> Add an author
            -s, --state --> Add a state
            -p, --priority --> Add a priority
            -t, --tags --> Add one or more tags
        """
        print(explanation_string)
        quit()

    # What book title does the book want to modify?
    title_question = [
        inquirer.Text('title',
                      message="What book would you like to change?",
                      )
    ]

    # Find the book in the list that most closely follows the title search and extract it from the JSON
    title_answer = h.safe_prompt(title_question)

    target_book_index = s.lookup(input_string=title_answer, helper=True)

    raw_json = h.read_file()

    book = raw_json["book_list"][target_book_index]

    book_title = book["title"]

    if(title==True):
        # Every book has a title, so we don't have to check for it.

        title_change_question = [
            inquirer.Text('title',
                          message=f"What title to change to from {book_title}?")
        ]

        title_answer = h.safe_prompt(title_change_question)["title"]
        book["title"] = title_answer
        print(f"Title changed to {title_answer}")


    if(author==True):
        # Inform the user about an author that already exists
        if (book["author"]):
            print(f"{book_title} already has the author {book['author']}")

        author_question = [
            inquirer.Text('author',
                           message=f"What author should {book_title} have?")
        ]

        author_answer = h.safe_prompt(author_question)["author"]
        book["author"] = author_answer

    if(state==True):
        # Inform the user about the state right now
        try:
            if (book["state"]):
                print(f"{book_title} already has the state {book['state']}")
        except:
            # Do nothing-- if there was a KeyError then this field doesn't exist already and there's nothing to present to the user.
            pass

        state_question = [
            inquirer.List('state',
                          message=f"What state should {book_title} have?",
                          choices=STATES
                          )
        ]
        state_answer = h.safe_prompt(state_question)["state"]
        book["state"] = state_answer

    if(priority==True):
        # Inform the user about the priority right now
        if (book["priority"]):
            print(f"{book_title} already has the priority {book['priority']}")

        priority_question = [
            inquirer.Text('priority',
                          message=f"What priority should {book_title} have?",
                          validate=h.verify_priority
                          )
        ]

        # NoneType object cannot be subscripted
        raw_priority_answer = h.safe_prompt(priority_question)["priority"]
        book["priority"] = raw_priority_answer

    if(tags==True):
        # Inform the user about the tags right now
        if (book["tag_list"]):
            print(f"{book_title} already has the tags {book['tag_list']}")

        tag_num_question = [
            inquirer.Text('tag_num',
                          message=f"How many tags would you like to add to {book_title}?",
                          validate=h.force_int
                          )
        ]
        tag_number_input = h.safe_prompt(tag_num_question)

        tag_questions = []

        for i in range(int(tag_number_input["tag_num"])):
            tag_questions.append(inquirer.Text(f'tag_{i}', message=f"Tag #{i + 1}?"))

        tag_answers = h.safe_prompt(tag_questions)
        new_tag_list = [value for value in tag_answers.values()]
        book["tag_list"].extend(new_tag_list)

        # Add tags to tag list

        old_tag_list = raw_json["tag_list"]
        for new_tag in new_tag_list:
            if not (new_tag in old_tag_list):
                old_tag_list.append(new_tag)

    # The list now contains the modified book.
    raw_json["book_list"][target_book_index] = book
    h.write_file(raw_json)