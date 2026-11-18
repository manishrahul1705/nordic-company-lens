import pytest
from signalpost.web.collector import extract_public_brand, strip_page_words
from signalpost.web.html import Page


def brand(title, legal):
    return extract_public_brand(Page(f'<html><head><title>{title}</title></head><body>{title}</body></html>'.encode(), 'https://example.no/'), legal)


@pytest.mark.parametrize('title,legal,expected', [
    ('Kontaktinformasjon Falsen Transport', 'FALSEN TRANSPORT AS', None),  # Remainder is the legal name.
    ('Kontaktinformasjon for kunder av Tensio', 'TENSIO AS', None),        # Sentence fragment.
    ('Kontakt oss - Fjordlys', 'FJORDLYS EIENDOM AS', 'Fjordlys'),
    ('Om oss | Bakeriet på hjørnet', 'NILSEN BAKERI AS', 'Bakeriet på hjørnet'),
    ('Velkommen til Fjordhotellet', 'VESTLAND HOTELLDRIFT AS', 'Fjordhotellet'),
    ('Contact us – Northwind', 'NORTHWIND TRADING AS', 'Northwind'),
    ('Hjem', 'EXAMPLE AS', None),
    ('Welcome', 'EXAMPLE AS', None),
    ('Drøbak Montessori – Med barnet i fokus', 'DRØBAK MONTESSORI UNGDOMSSKOLE AS', 'Drøbak Montessori'),
])
def test_leading_page_words_are_stripped_or_withheld(title, legal, expected):
    assert brand(title, legal) == expected


@pytest.mark.parametrize('value', ['Kontaktsenteret', 'Homestead Bygg', 'Omega Elektro', 'Welcomia'])
def test_names_that_merely_begin_like_page_words_are_kept(value):
    assert strip_page_words(value) == value
