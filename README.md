# Melvil

[//]: <> (TODO: Add quote from Melvil Dewey here)

## The Command-line Book Management Tool

Melvil aims to be the most user-friendly command line tool available for managing books. People who like convenience,
speed, and owning their own data will like Melvil.

Install with `install.sh`

### Dependencies:

* `python`
* `typer`
* `thefuzz`

## Features:


Melvil stores your books in a JSON file. Each book contains information about:

* A title
* An author
* A series of tags that describe its genre 
* A state of being read
* A priority (Position in the list)

There are many features that make your life easier:

* Smooth command line interaction with [Typer](https://github.com/tiangolo/typer) and [Inquirer](https://github.com/kazhala/InquirerPy)
* Fuzzy searching for book titles for nearly all commands, so you don't have to type the whole title every time. Don't remember a title name? No problem, fuzzy search by tag is available, too.
* Flags for more common commands allow the user to define how much info they want Melvil to track.

[//]: <> (TODO: Insert video demonstrating Melvil's features. You'll want a short GIF here similar to what you did for the time tracker, but you might also want to record a full-length video to better demonstrate your work.)

### Commands:

* `init` makes a new book list
* `add` adds a new book
* `remove` gets rid of a book
* `flip` prints out all the books from greatest to least priority
*  `change-status` modifies the status of a book
* `skim` lists the attributes of a book
* `prioritize` changes the priority of a book
* `tag` adds the given tag to the given book
* `untag` removes the target tag from the given book
* `lookup` searches by title
* `compile` searches by tag
* `delete` clears the booklist

