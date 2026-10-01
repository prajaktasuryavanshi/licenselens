from api import classify


def test_gpl_is_high():
    assert classify('GPL-3.0') == 'High'


def test_lgpl_is_medium():
    assert classify('LGPL-2.1') == 'Medium'


def test_mit_is_low():
    assert classify('MIT') == 'Low'


def test_unknown():
    assert classify('Unknown') == 'Unknown'
