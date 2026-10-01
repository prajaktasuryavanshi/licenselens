import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scanner'))
from compatibility import assess_risk


def test_gpl_in_mit_is_high():
    assert assess_risk('MIT', 'GPL-3.0') == 'high'


def test_lgpl_is_medium():
    assert assess_risk('MIT', 'LGPL-2.1') == 'medium'


def test_mit_is_ok():
    assert assess_risk('MIT', 'MIT') == 'ok'


def test_gpl_project_accepts_gpl():
    assert assess_risk('GPL-3.0', 'GPL-3.0') == 'ok'
