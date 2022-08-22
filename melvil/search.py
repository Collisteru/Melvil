# A file containing functions related to search
from main import app, inquirer, STATES, typer
import helper as h

@app.command()
def lookup():
    """
    Search for a book by title.
    """
    question = [
        inquirer.Text('title',
                      message="Which book would you like to look up?",
                      ),
    ]
    answers = inquirer.prompt(question)
    search_query = answers["title"]

    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]
    title_catalog = [book["title"] for book in book_catalog]

    num_results = max(1, round(h.SEARCH_FRACTION*len(book_catalog)))
    print(f"These are the {num_results} titles that most closely match your query: ")
    for result in range(num_results):
        top_result_index = int(h.fuzzy_search_booklist(search_query, book_catalog))
        top_result = title_catalog[top_result_index]
        print(top_result)
        book_catalog.pop(top_result_index)
