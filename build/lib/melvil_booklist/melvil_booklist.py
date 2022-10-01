VERSION = "1.0.0"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
STATES = ["Unknown", "To Read", "Reading", "Read", "Reviewed"]
DEFAULT_FILE_NAME = "melvil/melvil.json"
FUZZY_RATIO_THRESHOLD = 75 # We shouldn't count fuzzy ratios that are higher than this.

# Root file for major dependencies and data.
# Melvil only keeps track of one booklist at a time, but this booklist can be saved anywhere the user wants to save
# it. Melvil keeps track of where that booklist is saved by saving its path.
# Note that this includes all the information Melvil needs to find the proper file to edit:

import typer
from datetime import date

TODAY = str(date.today())
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

app = typer.Typer()

# Import Standard Modules
from book.book import *
from booklist.booklist import *
from reading import *
from search import *
import helper.helper as h





# Import submodules

# Testing that we have indeed imported the required packages...
def EmptyTitleException(Exception):
    pass

@app.callback()
def callback():
    """
    Melvil, the command-line book management tool.
    """
    pass

# App is only invoked when we run melvil.py directly, but not when we import it.
if __name__ == "__main__":
      app()