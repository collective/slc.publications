 # -*- coding: utf-8 -*-
"""Tests for slc.publication PublicationsBySubjectView."""

from p4a.subtyper.interfaces import ISubtyper
from slc.publications.interfaces import IPublicationContainerEnhanced
from slc.publications.interfaces import IPublicationEnhanced
from slc.publications.tests.base import IntegrationTestCase
from zope.component import getUtility
from zope.interface import alsoProvides

import unittest2 as unittest


class TestPublicationsBySubjectView(IntegrationTestCase):
    """Test for the @@file_view."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # @@file_view expects to find File content types in 'publish' state,
        # however, by default Files don't have any workflow assigned to them
        self.workflow.setChainForPortalTypes(['File'], 'plone_workflow')

        # create a folder that will hold publications and change it's subtype
        # to PublicationContainer
        self.portal.invokeFactory('Folder', 'pubs1', title='Publications 1')
        self.portal.invokeFactory('Folder', 'pubs2', title='Publications 2')
        self.pubs1 = self.portal.pubs1
        self.pubs2 = self.portal.pubs2
        alsoProvides(self.pubs1, IPublicationContainerEnhanced)
        alsoProvides(self.pubs2, IPublicationContainerEnhanced)
        self.subtyper = getUtility(ISubtyper)
        self.subtyper.change_type(
            self.pubs1, u'slc.publications.FolderPublicationContainer')
        self.subtyper.change_type(
            self.pubs2, u'slc.publications.FolderPublicationContainer')

        # add some publications
        self.pubs1.invokeFactory('File', 'pub1')
        self.pubs1.invokeFactory('File', 'pub2')
        self.pubs2.invokeFactory('File', 'pub3')

        # set Subjects
        self.pubs1.pub1.setSubject(['foo', 'bar'])
        self.pubs1.pub2.setSubject(['foo', ])
        self.pubs2.pub3.setSubject(['bar', ])

        # publish publications
        self.workflow.doActionFor(self.portal.pubs1['pub1'], 'publish')
        self.workflow.doActionFor(self.portal.pubs1['pub2'], 'publish')
        self.workflow.doActionFor(self.portal.pubs2['pub3'], 'publish')

        # reindex everything to update the catalog
        self.catalog.clearFindAndRebuild()

    def test_subtyping(self):
        """Confirm that Folder and File are correctly subtyped."""
        from p4a.subtyper.interfaces import ISubtyper
        self.subtyper = getUtility(ISubtyper)

        # Folder
        self.assertTrue(IPublicationContainerEnhanced.providedBy(self.pubs1))
        self.assertEquals(
            self.subtyper.existing_type(self.pubs1).name,
            u'slc.publications.FolderPublicationContainer'
        )

        # File
        self.assertTrue(IPublicationEnhanced.providedBy(self.pubs1.pub1))
        self.assertEquals(
            self.subtyper.existing_type(self.pubs1.pub1).name,
            u'slc.publications.Publication'
        )

    def test_publist_and_parents(self):
        """Simple test of what self.publist and self.parents contain when
        view is called.
        """
        self.request['subject'] = ['foo', 'bar']
        view = self.portal.unrestrictedTraverse('@@publications-by-subject')
        view()

        publist = view.publist
        self.assertEquals(publist.keys(), ['/plone/pubs1', '/plone/pubs2'])
        self.assertEquals(publist['/plone/pubs1'][0].id, 'pub1')
        self.assertEquals(publist['/plone/pubs1'][1].id, 'pub2')
        self.assertEquals(publist['/plone/pubs2'][0].id, 'pub3')

        parents = view.parents
        self.assertEquals(len(parents), 2)
        self.assertEquals(parents[0][0], '/plone/pubs1')
        self.assertEquals(parents[0][1].id, 'pubs1')
        self.assertEquals(parents[1][0], '/plone/pubs2')
        self.assertEquals(parents[1][1].id, 'pubs2')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
