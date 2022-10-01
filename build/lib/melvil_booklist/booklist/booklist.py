# This file focuses on commands that affect the entire booklist.

from melvil_booklist import app
import inquirer
import os
import json
import csv
import os
import pwd
import sys
import inspect


from helper import helper as h

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project")

from datetime import date

TODAY = str(date.today())
DEFAULT_FILE_NAME= "Melvil_Project.json"
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

def get_username():
    return pwd.getpwuid(os.getuid())[0]

user = get_username()
@app.command()
def init():
    """
    Initialize book list.
    The user enters the name of the booklist and Melvil sets the booklist path to a JSON file of that name in the current working directory.
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
        inquirer.Text('file_name', message="Enter a file name. Melvil will use as your booklist a file with that name in the current directory. .", validate=file_validation)
    ]
    answers = h.safe_prompt(questions)

    # If no file name is provided, use the current working directory
    if answers["file_name"] == "":
        location = os.getcwd() + "/" + DEFAULT_FILE_NAME
    else:
        # Else use the file name provided by the user. Either way, we initialize the file in the current working directory (TODO: we should refactor this to be more flexible).
        location = os.getcwd() + "/" + answers["file_name"].replace(" ", "_")

    # Write filename in a reference PATH the program will use each time to find the file it wants.
    with open(f"/home/{h.user}/.melvilPath", 'w+') as path:
        print(f"Writing new path to /home/{h.user}/.melvilPath")
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
        print("New JSON file initialized at " + location)
        file.write(json_string)

@app.command()
def delete():
    """
    Deletes your current booklist. Not to be used lightly!
    """
    OPTIONS = ["Yes", "No"]

    raw_json = h.read_file()

    question = [
        inquirer.List('confirmation',
                      message=f"{bcolors.FAIL} WARNING: This will delete your booklist at {raw_json['path']}. {bcolors.ENDC} Are you sure you want to do this? (Yes/No)",
                      choices=OPTIONS,
                      ),
    ]

    # List index out of range. But why?
    try:
        to_exterminate = h.safe_prompt(question)["confirmation"]
    except:
        print("Empty input. Exiting.")
        exit()

    if to_exterminate == "Yes":
        os.remove(f"/home/{USER}/.melvilPath")
        print("Booklist deleted. Reinitialize with 'init'.")
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

    transcription_answer = h.safe_prompt(transcription_question)["file_to_transcribe"]

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
                book_catalog.append({"title": row[0], "author": row[1], "priority": 0, "state": "Unknown", "tag_list": []})
            elif (row[0:1]):
                book_catalog.append({"title": row[0], "author": "", "priority": 0, "state": "Unknown", "tag_list": []})
            else:
                # Empty row...?
                pass
    h.write_file(raw_json)
    print("Transcribed")

@app.command()
# TODO: Add flag to show priority too.
def list(helper: bool=False):
    """
    Prints list contents in order of greatest-to-least priority.
    """
    raw_json = h.read_file()

    book_list = raw_json["book_list"]
    new_list = sorted(book_list, key=lambda d: int(d['priority']), reverse=True)

    data_table = []
    if not helper:
        if len(new_list) != 0:
            for book in new_list:
                data_table.append(["\x1B[3m" + book["title"] + "\x1B[0m", "Author: " + book["author"], "Priority: " + str(book["priority"]), "State: " + book["state"]])
            for row in data_table:
                print("{: <60} \n{: <60} {: <60} {: <60} \n".format(*row))
        else:
            print("No books yet. Try adding one with 'add'.")
    return new_list

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
