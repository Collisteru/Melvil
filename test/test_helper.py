import pytest
import main as m
import helper as h

def test_fuzzy_search_booklist():
    raw_json = h.read_file()
    book_catalog = raw_json["book_list"]
    assert h.fuzzy_search_booklist("Second", book_catalog) == 1
    assert h.fuzzy_search_booklist("Bible", book_catalog) == 0
    assert h.fuzzy_search_booklist("Bile", book_catalog) == 0
    assert h.fuzzy_search_booklist("ible", book_catalog) == 0
    assert h.fuzzy_search_booklist("Fractional", book_catalog) == 2
    assert h.fuzzy_search_booklist("ractional", book_catalog) == 2
