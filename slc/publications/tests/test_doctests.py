# -*- coding: utf-8 -*-
"""Doctest runner."""

from slc.publications.tests.base import IntegrationTestCase
from Testing import ZopeTestCase as ztc
import doctest
import unittest2 as unittest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():

    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'doc/subtyping.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

        ztc.ZopeDocFileSuite(
            'pdf/pdfparser.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

        ztc.ZopeDocFileSuite(
            'doc/events.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

        ztc.ZopeDocFileSuite(
            'doc/bulkuploading.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

        ztc.ZopeDocFileSuite(
            'doc/chapters.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

        ztc.ZopeDocFileSuite(
            'ini/iniparser.txt',
            package='slc.publications',
            test_class=IntegrationTestCase,
            optionflags=OPTIONFLAGS,
        ),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
