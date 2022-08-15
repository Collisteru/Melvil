import os
import sys
import re
from pprint import pprint
import random
import inquirer
from inquirer import errors

sys.path.append(os.path.realpath('.'))

def file_validation(answers, current):
    if not current.endswith('.json'):
        raise inquirer.errors.ValidationError('', reason='Please use a .json file extension.')
    return True

questions = [
    inquirer.Text('file_name', message="Please enter the file you would like to designate as the storage file for your books.", validate=file_validation)
]

answers = inquirer.prompt(questions)

pprint(answers)