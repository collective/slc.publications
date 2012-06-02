# -*- coding: utf-8 -*-
"""Doctest runner."""

from Globals import package_home
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from slc.publications.config import product_globals
from slc.publications.tests.base import SLC_PUBLICATIONS_FUNCTIONAL_TESTING
from StringIO import StringIO
import doctest
import os
import unittest2 as unittest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def loadfile(rel_filename):
    """A helper method for loading test data files."""
    home = package_home(product_globals)
    filename = os.path.sep.join([home, rel_filename])
    data = StringIO(open(filename, 'r').read())
    data.filename = os.path.basename(rel_filename)
    return data


def setUp(self):
    """A custom setUp method that prepares additional stuff needed in our
    doctests.
    """
    layer = self.globs['layer']
    # Update global variables within the tests.
    self.globs.update({
        'portal': layer['portal'],
        'folder': layer['portal'].folder,
        'loadfile': loadfile,
    })
    setRoles(layer['portal'], TEST_USER_ID, ['Manager'])


def test_suite():

    suite = unittest.TestSuite()

    subtyping = doctest.DocFileSuite(
        '../doc/subtyping.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    subtyping.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    pdfparser = doctest.DocFileSuite(
        '../pdf/pdfparser.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    pdfparser.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    events = doctest.DocFileSuite(
        '../doc/events.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    events.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    bulkuploading = doctest.DocFileSuite(
        '../doc/bulkuploading.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    bulkuploading.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    chapters = doctest.DocFileSuite(
        '../doc/chapters.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    chapters.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    iniparser = doctest.DocFileSuite(
        '../ini/iniparser.txt',
        setUp=setUp,
        optionflags=OPTIONFLAGS,
        globs={'layer': SLC_PUBLICATIONS_FUNCTIONAL_TESTING},
    )
    iniparser.layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING

    suite.addTests([
             subtyping,
             pdfparser,
             events,
             bulkuploading,
             chapters,
             iniparser,
         ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
