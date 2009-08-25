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


def test_suite():
    return unittest.TestSuite((

            Suite('doc/subtyping.txt',
                   optionflags=OPTIONFLAGS,
                   package='slc.publications',
                   test_class=PublicationFunctionalTestCase) ,

            Suite('pdf/pdfparser.txt',
                   optionflags=OPTIONFLAGS,
                   package='slc.publications',
                   test_class=PublicationFunctionalTestCase) ,

            Suite('ini/iniparser.txt',
                   optionflags=OPTIONFLAGS,
                   package='slc.publications',
                   test_class=PublicationFunctionalTestCase) ,

            Suite('doc/chapters.txt',
                   optionflags=OPTIONFLAGS,
                   package='slc.publications',
                   test_class=PublicationFunctionalTestCase) ,

           Suite('doc/bulkuploading.txt',
                  optionflags=OPTIONFLAGS,
                  package='slc.publications',
                  test_class=PublicationFunctionalTestCase) ,

           Suite('doc/events.txt',
                  optionflags=OPTIONFLAGS,
                  package='slc.publications',
                  test_class=PublicationFunctionalTestCase) ,
        ))

