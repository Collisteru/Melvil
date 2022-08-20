import copy
import pty
import subprocess
from subprocess import PIPE, Popen
import pytest
import os
from datetime import date
TODAY = str(date.today())


pytest_plugins = ["pytester"]


# Multiline f-strings in Python are weird. Apologies.
initial_content = (
    '{\n'
    f'"lastEdited": "{TODAY}",\n'
    '"book_list": [],\n'
    '"tag_list": []\n'
    '}'
)

one_content = (
    '{\n'
        f'"lastEdited": "{TODAY}",\n'
        '"book_list": [\n'
            '\t{\n'
                '\t\t"title": "The Lord of the Rings",\n'
                '\t\t"author": "J. R. R. Tolkien",\n'
                '\t\t"state": "Unknown",\n'
                '\t\t"priority": "50"\n'
                '\t\t"tags": ["fantasy", "fiction"]\n'
            '\t},\n'
        '],\n'
        '"tag_list": [\n'
            '\t"fantasy",\n'
            '\t"fiction"\n'
        ']\n'
    '}'
)

add_request =  {
    "title": "The Lord of the Rings",
    "author": "J.R.R. Tolkien",
    "state": "Read",
    "priority": "3",
    "tags": ["fantasy", "fiction"]
}


tmp_path = "../"

"""
def test_entrypoint():
    exit_status = os.system('python main.py --help')
    assert exit_status == 0
"""

@pytest.fixture()
def initial_filler(tmp_path):
    full_path = tmp_path / "test_init"
    full_path.mkdir()
    file_name = full_path / "mortimer.json"
    with file_name.open("w+") as f:
        f.write(initial_content)
    return file_name

@pytest.fixture()
def fill_with_one(tmp_path):
    full_path = tmp_path / "test_init"
    full_path.mkdir()
    file_name = full_path / "mortimer.json"
    def test_add_book(initial_filler):
        exit_status = os.system('python main.py add')
    return file_name

# Functions for reading from and writing to a subprocess
import subprocess



def start(executable_file: list):
    return subprocess.run(
        executable_file,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def read(process):
    try:
        return process.stdout.readline().decode("utf-8").strip()
    except:
        # process.stdout is a bytes-like object
        return process.stdout.decode("utf-8").strip()


def write(process, message):
    try:
        process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
    except AttributeError:
        process.stdin.write(f"{message.strip().decode()}\n".encode("utf-8"))
        pass
    # Broken pipe

def terminate(process):
    try:
        process.stdin.close()
        process.wait(timeout=0.2)
    except:
        pass
        # Nevermind!

def test_init():

    # "Broken Pipe" occurs about half the time. You must ignore this.
    process = start(["./main.py"])
    try:
        write(process, "")
    except:
        pass
        # Nevermind!
    print("Reading from process")
    print(read(process))
    terminate(process)



if __name__ == "__main__":
    test_init()