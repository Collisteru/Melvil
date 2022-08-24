# This file focuses on commands that affect the entire booklist.
from main import app, STATES, typer, DEFAULT_FILE_NAME, TODAY, bcolors
import helper as h

import inquirer
import os
import json
import csv

@app.command()
def init():
    """
    Initialize book list.
    """

    # We're going to save the custom location the user provides in a file named config.txt in the same folder
    # as the one the user specifies. Melvil will search for whatever file is specified in config.txt whenever
    # the time comes.
    def file_validation(answers, current):
        if current.endswith(".json") == False:
            # We allow an empty answer; this just goes to the default location saved in the global variable FILE_NAME.
            if(current == ""):
                return True
            print("Not a valid file name. Please use a .json file.")
            return False
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

    # Write filename in a reference PATH the program will use each time to find the file it wants.
    with open("path.txt", 'w+') as path:
        path.write(answers["file_name"].replace(" ", "_"))


    # Initialize book dictionary
    initDict = {}
    initDict['path'] = location
    initDict['last_edited'] = TODAY
    initDict['book_list'] = [] # An empty list indicates that no books have been added yet.
    initDict["tag_list"] = []
    json_string = json.dumps(initDict, indent=4)
    os.makedirs(os.path.dirname(location), exist_ok=True)
    with open(location, "w+") as file:
        print(f"New JSON file initialized at {location}")
        file.write(json_string)

@app.command()
def compile():
    """
    Search for all books with a given tag.
    """
    search_query = input("Which tag would you like to search for? ")

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    # Get tag catalog
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

@app.command()
def delete():
    """
    Delete all the books in the list. Not to be used lightly!
    """
    OPTIONS = ["Yes", "No"]

    raw_json = h.read_file()

    question = [
        inquirer.List('confirmation',
                      message=f"{bcolors.FAIL}WARNING: This will delete all the books in your list at {raw_json['path']}. {bcolors.ENDC} Are you sure you want to do this? (Yes/No)",
                      choices=OPTIONS,
                      ),
    ]

    # List index out of range. But why?
    to_exterminate = inquirer.prompt(question)["confirmation"]

    if to_exterminate == "Yes":
        raw_json["book_list"] = []
        raw_json["tag_list"] = []
        h.write_file(raw_json)
        print("All books and tags have been deleted.")
    else:
        print("Action aborted.")

@app.command()
def transcribe(csv_flag=None):
    """
    Add books from a CSV file in the format of "book title", "book author" to the book list.
    """
    def csv_validation(answers, current):
        if current.endswith(".csv") == False:
            # We allow an empty answer; this just goes to the default location saved in the global variable FILE_NAME.
            if(current == ""):
                return True
            print("Not a valid file name. Please use a .csv file.")
            raise inquirer.errors.ValidationError('', reason='Please use the .csv file extension.')
        return True

    transcription_question = [
        inquirer.Text("file_to_transcribe",
                      message="Choose a csv file to add to the book list in this directory.",
                      validate=csv_validation,
                      )
    ]

    transcription_answer = inquirer.prompt(transcription_question)["file_to_transcribe"]

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]

    print("transcription_answer: ", transcription_answer)
    with open(transcription_answer, "r") as csv_file:
        print("csv_file: ", csv_file)
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            print("row: ", row)
            # Interestingly, teaking list slices lie this is safe, much like the .get() method.
            if (row[0:1] and row[1:2]):
                book_catalog.append({"title": row[0], "author": row[1], "priority": 0, "tags": []})
            elif (row[0:1]):
                book_catalog.append({"title": row[0], "author": "", "priority": 0, "tags": []})
            else:
                # Empty row...?
                pass
    h.write_file(raw_json)
    print("Transcribed")

@app.command()
# TODO: Add flag to show priority too.
def flip(helper: bool=False):
    """
    Prints list contents in order of decreasing priority.
    """
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

@app.command()
def classify(helper: bool=False):
    """
    Prints list of all tags.
    """
    raw_json = h.read_file()

    tag_list = raw_json["tag_list"]
    new_list = sorted(tag_list)

    if not helper:
        for tag in new_list:
            print(tag)

    return new_list

@app.command()
def count():
    """
    Print list length.
    """
    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]
    print(f"There are {len(book_catalog)} books in this list.")