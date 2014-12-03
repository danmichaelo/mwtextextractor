# encoding=utf-8
from __future__ import unicode_literals
import unittest
from mwtextextractor import get_body_text


class TestMWTextExtractor(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_template(self):
        # Check that a simple template is stripped
        text = 'Alfa {{beta}} gamma'
        te = get_body_text(text).split()
        self.assertEqual(len(te), 2)  # only two words should remain

    def test_recursive_tables(self):
        # Check that recursive tables are stripped correctly
        text = 'Alfa {| \n|beta \n{| \n|gamma \n|} \n|} delta'
        te = get_body_text(text).split()
        self.assertEqual(len(te), 2)  # only two words should remain

    def test_math(self):
        # Check that a simple template is stripped
        text = 'on alkuperäinen suure ja <math>1/2 \le r<1 < 2<3</math>. Eudoksoksen oppilas'
        te = get_body_text(text).split()
        self.assertEqual(len(te), 6)


if __name__ == '__main__':
    unittest.main()
