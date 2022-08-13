import json

class TitleNotFoundException(Exception):
    pass

"""
Reads mortimer.json and outputs a dictionary
"""
def read_file():
    with open("mortimer.json") as file: # w+ Overwrites an existing file if one already exists. You cannot ignore this! This is not nothing! new_book = json.loads(book_json)
        json_dict = json.load(file)
        return json_dict

"""
Writes to mortimer.json given a dictionary object
"""
def write_file(input: dict) -> None:
    json_string = json.dumps(input, indent=4)
    with open("mortimer.json", "w") as file: # w+ Overwrites an existing file if one already exists. You cannot ignore this! This is not nothing!
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
Asks the user for a value in the status enumeration, and keeps asking until the user gives one.
Returns the index of the status enum corresponding to the user's choice.
"""
# TODO: Use inquirer for this.
def request_state():
    question = """
    Select one of the status options below by inputting one of the four numbers:

    1 -- To Read
    2 -- Reading
    3 -- Read
    4 -- Reviewed
    """

    while True:
        user_input = check_user_input(question, 1)
        if not user_input in range(1, 5):
            print("Invalid state request. \n\n Input either 1, 2, 3, or 4.")
            continue
        else:
            return int(user_input)

"""
Searches the booklist and returns the index of the book with the specified title
"""
# TODO: Change this to match by ID instead of title
def search_booklist(title: str, book_list: list):
    for bookIndex, book in enumerate(book_list):
        try:
            if book["title"]  == title:
                return bookIndex
        except:
            raise KeyError("There's been an error. Is your list in the right format?")

    # There aren't any books of that title in the list
    raise TitleNotFoundException
