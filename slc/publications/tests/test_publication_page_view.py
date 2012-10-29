 # -*- coding: utf-8 -*-
"""Tests for slc.publication PublicationPageView."""

from p4a.subtyper.interfaces import ISubtyper
from slc.publications.interfaces import IPublicationContainerEnhanced
from slc.publications.interfaces import IPublicationEnhanced
from slc.publications.tests.base import IntegrationTestCase
from zope.component import getUtility
from zope.interface import alsoProvides

import unittest2 as unittest


class TestPublicationPageView(IntegrationTestCase):
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
        self.portal.invokeFactory('Folder', 'pubs', title='Publications')
        self.pubs = self.portal.pubs
        alsoProvides(self.pubs, IPublicationContainerEnhanced)
        self.subtyper = getUtility(ISubtyper)
        self.subtyper.change_type(
            self.pubs, u'slc.publications.FolderPublicationContainer')

        # add some publications
        self.pubs.invokeFactory('File', 'pub1')
        self.pubs.invokeFactory('File', 'pub2')
        self.pubs.invokeFactory('File', 'pub3')

        # set Subjects
        self.pubs.pub1.setSubject(['foo', 'bar'])
        self.pubs.pub2.setSubject(['foo', ])
        self.pubs.pub3.setSubject(['bar', ])

        # publish publications
        self.workflow.doActionFor(self.portal.pubs['pub1'], 'publish')
        self.workflow.doActionFor(self.portal.pubs['pub2'], 'publish')
        self.workflow.doActionFor(self.portal.pubs['pub3'], 'publish')

        # reindex everything to update the catalog
        [pub.reindexObject() for pub in self.pubs.values()]

    def test_subtyping(self):
        """Confirm that Folder and File are correctly subtyped."""
        from p4a.subtyper.interfaces import ISubtyper
        self.subtyper = getUtility(ISubtyper)

        # Folder
        self.assertTrue(IPublicationContainerEnhanced.providedBy(self.pubs))
        self.assertEquals(
            self.subtyper.existing_type(self.pubs).name,
            u'slc.publications.FolderPublicationContainer'
        )

        # File
        self.assertTrue(IPublicationEnhanced.providedBy(self.pubs.pub1))
        self.assertEquals(
            self.subtyper.existing_type(self.pubs.pub1).name,
            u'slc.publications.Publication'
        )

    def test_fetchRelatedPublications(self):
        """Simple test of fetching related publications."""
        view = self.portal.pubs.pub1.unrestrictedTraverse('@@file_view')
        results = view.fetchRelatedPublications()

        self.assertEquals(results[0].id, 'pub2')
        self.assertEquals(results[1].id, 'pub3')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
