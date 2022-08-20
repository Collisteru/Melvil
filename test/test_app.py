import copy
import pty
import subprocess
from subprocess import PIPE, Popen
import pytest
import os
from datetime import date
from Mortimer import helper as h
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

def test_init(initial_filler):
    # Make a new tty for the process IO to use:wa

    # What is pty?
    # Pty are the pseudo-terminals that are used to communicate with the child process.
    master_fd, slave_fd = pty.openpty() # Opens a pty master/slave pair. Why we need a master/slave pseudoterminal beats me.
    # TODO: Add more and test them all in sequence.
    init_cmd_1 = ["python", "../main.py", "init"] # String or bytes instance should be fine for the first argument


    #inpty(init_cmd_1))
    def inpty(argv):
        output = []
        #  pty.spawn(argv, master_read=reader)
        # Where does the file descriptor come from?

        # Spawn might fill in the file descriptor
        # for it. We can see what it fills in.

        # File descriptor is naturally 7
        def reader(fd): # Function (int) -> bytes
            c = os.read(fd, 1024) # Reads from the file descriptor and returns bytes. The file descriptor is either seven or nothing.

            print("\n")

            # In practice, this is reading from a file descriptor with index 7 and returning the question ased by the init function. It makes sense that this isn't ever disappearing, because we never actually
            # put input to the pseudoterminal. Let's fix this


            # This is good, but the problem remains that we're not entering the input in thes sense of getting the input to go onto another register.
            # What triggers inquirer to move onto the next input? The enter key. But this isn't the same as a newline,
            # because we already input a newline and aren't getting the proper result. We need something else.
            os.write(fd, b"mortimer.json\n") # This works but we never signal the end of our teletype-- might need to insert a null bytes object to do so.

            try:
                output = os.read(fd, 1024)
                assert output == "New JSON file initialized at mortimer.json"
            except:
                print(f"Assert error exception; output is {output}.")
            return c

        # Stdin for this process defaults to the real STDIN because
        # we don't define it otherwise. Let's fix that.

        # Passing in reader to pty.spawn renders 7 as the file descriptor
        process = pty.spawn(argv, master_read=reader) # Also, it seems reader has the wrong type signature.



        return b"".join(output).decode('utf-8')
    print(f"Command output: {init_cmd_1}" + inpty(init_cmd_1))


"""
    # Execute a child program in a new process
    # These args are wrong
    process = subprocess.Popen(init_cmd_1)
    initial_output = process.communicate(b"test.json")
    second_output = process.communicate()
    assert second_output == "New JSON file initialized at test.json"
    assert h.read_file("test.json") == second_output
    
    
# I'm not sure this can modify the keys and values of an *internal* dictionary.
# Start this up with the initial, standard filler.
def test_add_book(initial_filler):
    # First, test with no flags
    process = Popen(["python", "main.py", "add"], stdin=PIPE, stdout=PIPE, bufsize=1)
    process.communicate(b"TestTitle")
    desired_content = (
        '{\n'
        f'"lastEdited": "{TODAY}",\n'
        '"book_list": [\n'
        '\t{\n'
        '\t\t"title": "TestTitle",\n'
        '\t},\n'
        '],\n'
        '"tag_list": []\n'
        '}'
    )
    assert h.read_file(initial_filler) == desired_content
    print("h.read_file = ", h.read_file)
"""

if __name__ == "__main__":
    test_entrypoint()