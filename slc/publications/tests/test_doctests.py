import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from base import PublicationFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from slc.publications.config import product_globals

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    home = package_home(product_globals)
    # find txt files in test dir
    filenames = [filename for filename in
            glob.glob(os.path.sep.join([home, 'doc', '*.txt']))]
    return filenames


def test_suite():
    filenames = list_doctests()
    for f in filenames:
        print os.path.basename(f)
    return unittest.TestSuite(
        [Suite('doc/'+os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='slc.publications',
               test_class=PublicationFunctionalTestCase)
         for filename in filenames]
        )