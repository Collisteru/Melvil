# This file focuses on commands that affect the entire booklist.

import inquirer
import os
import json
import csv

from helper import helper as h

# Import app from parent directory. This requires a bit of a python path hack.
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/melvil")

from app import app
from datetime import date


TODAY = str(date.today())
DEFAULT_FILE_NAME= "melvil.json"
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@app.command()
def init():
    """
    Initialize book list.
    The user enters the location they would like their book list to have.
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
        location = os.getcwd() + "/" + answers["file_name"].replace(" ", "_")

    # Write filename in a reference PATH the program will use each time to find the file it wants.
    with open("./path.txt", 'w+') as path:
        print("Writing new path to path.txt")
        path.write(location)

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
            # Interestingly, taking list slices like this is safe, like the .get() method.
            if (row[0:1] and row[1:2]):
                book_catalog.append({"title": row[0], "author": row[1], "priority": 0, "state": "Unknown", "tags": []})
            elif (row[0:1]):
                book_catalog.append({"title": row[0], "author": "", "priority": 0, "state": "Unknown", "tags": []})
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