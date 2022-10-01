import json
from Levenshtein import distance
from collections import OrderedDict
from thefuzz import fuzz
import inquirer

# Import appFile from parent directory. This requires a bit of a python path hack.
import os
import pwd
import sys
import inspect


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
user = pwd.getpwuid(os.getuid())[0]
sys.path.insert(0, "/home/sean/Documents/Programs/Melvil/Melvil_Project")



# TODO: It may actually be possible to solve the interruption problem by adding a custom verify function that checks if the input contains a newline character or an interrupt character or another
# special character and nothing else.


# SEARCH_FRACTION Defines a "reasonable" number of search results for each query as a fraction of the
# total number of books in the catalog.
# Keep this on the high side. See search.py
SEARCH_FRACTION = 0.3

class TitleNotFoundException(Exception):
    pass

"""
Read file
"""
def read_file() -> dict:
    try:
        with open(f"/home/{user}/.melvilPath", 'r') as path:
            path = path.read()
    except:
        print("Can't read path file. Did you initialize a list with 'init'?")
        sys.exit()

    try:
        with open(path, "r") as file:
            return json.load(file)
    except:
        print(f"Invalid path in path file. Try modifying /home/{h.user}/.melvilPath")
        sys.exit()

"""
Writes to Melvil_Project.json given a dictionary object
"""
def write_file(input: dict) -> None:
    json_string = json.dumps(input, indent=4)
    try:
        with open(f"/home/{user}/.melvilPath", 'r') as path:
            path_line = path.read()
    except Exception as e:
        print("Can't read path file. Did you initialize a list with 'init'?")
        print(f"(Exception: {e})")
        quit()

    with open(path_line, "w") as file: # Local variable 'path' referenced before assignment. What could this mean?
        file.write(json_string)

"""
Asks the user for a value of a certain data type, and keeps asking until the user gives it.
The "option" pararameter represents whether you want an int, a float, or a string.
1 means you want an int, 2 means you want a float
If the input is indeed of the requested type, we return that input.
"""
def check_user_input(command: str, option: int = 0):
    user_input = ""
    options_to_english = {1: "int", 2: "float"}
    flag = False
    # First, check that the option parameter is valid
    if option != 0 and option != 1 and option != 2 and option != 3:
        raise Exception("Invalid option input.")
    elif option == 0:
        user_input = input(f"{command}")
        english_option = options_to_english[option]
    else:
        english_option = options_to_english[option]

    while not flag:
        user_input = input(f"{command}")
        try:
            if (option == 1):
                user_input = int(user_input)
            if (option == 2):
                user_input = float(user_input)
            flag = True
            return user_input
        except:
            print(f"Please enter a value of type {english_option}")

"""
Params:
- Search query is the title of the book to find.
- Book list is the list of books (not just titles!) to search through to find the target title.
First tries to exactly match the title of the book with the input title. If there is no such match, returns the index of a first match of a fuzzy search.
Fuzzy searches the booklist and returns the index of the book with the specified title
Returns -1 if something bad happens (probably an invalid title, but I haven't tested this.)
"""
def fuzzy_search_booklist(search_query: str, book_list: list):
    for bookIndex, book in enumerate(book_list):
        try:
            if book["title"]  == search_query:
                return bookIndex
        except:
            print("Oops! Something went wrong in fuzzy_search_booklist!")
            return -1

    # Commence fuzzy search.

    # Create an ordered list of book titles by least-to-greatest Levenshtein distance
    # from the given query.
    title_catalog = [book["title"] for book in book_list]
    title_to_levenshtein = {title: fuzz.ratio(search_query, title) for title in title_catalog}
    sorted_title_to_catalog = {k: v for k, v in sorted(title_to_levenshtein.items(), key=lambda item: item[1])}
    results = OrderedDict(reversed(list(sorted_title_to_catalog.items())))

    # Extract the top match
    results_list = list(results.items())
    result_title = results_list[0][0]

    # Find the index of the book with that matching title.
    for bookIndex, book in enumerate(book_list):
        try:
            if book["title"]  == result_title:
                return bookIndex
        except:
            print("Oops! Something went wrong in fuzzy_search_booklist!")
            return -1

    # The list is empty
    print("Your list is empty!")

# We just need a func that can accept integers or floats
def verify_priority(answers, current):
    try:
        float(current)
    except:
        raise inquirer.errors.ValidationError('', reason='Please enter a floating-point or integer number.')
    return True

# TODO: Add a function that matches by ID instead of title
# Tries to convert the answer into an int and returns True if successful. Otherwise, raises an error.
def force_int(answers, current):
    try:
        int(current)
    except:
        raise inquirer.errors.ValidationError('', reason='Please enter an integer.')
    return True

def safe_prompt(question):
    """
    Call to inquirer that safely handles empty input.
    """
    while True:
        answer = inquirer.prompt(question)
        if (list(answer.values())[0] == ""):
            print("Empty answer. Try again.")
        else:
            return answer

def substring_similarity(string1, string2):
    """
    We assume that string1 is the shorter string and define the similarity of the two
    as the closest similarity of string1 and any of the substrings of string2.
    If string1 is longer than string2, we just compute the similarity of string1 and string2
    """

    if (len(string1) >= len(string2)):
        return distance(string1, string2)
    else:
        # Generate substrings of string1
        distances = []
        substrings = [string2[i:j] for i in range(len(string2)) for j in range(i+1, len(string2)+1)]
        for substring in substrings:
            distances.append(distance(string1, substring))
        return min(distances)

def superstring_finder(substring: str, superstrings: list):
    """
    Finds the string that the given search query is most likely a substring of.
    Returns a dictionary between items in the list and the minimum Levenshtein distance among their substrings.
    """
    results_dict = {}
    for superstring in superstrings:
        results_dict[superstring] = substring_similarity(substring, superstring)
    sorted_results_dict = {k: v for k, v in sorted(results_dict.items(), key=lambda item: item[1])}
    return sorted_results_dict