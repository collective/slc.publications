 # -*- coding: utf-8 -*-
"""Tests for slc.publication PublicationsView."""

from p4a.subtyper.interfaces import ISubtyper
from slc.publications.interfaces import IPublicationContainerEnhanced
from slc.publications.interfaces import IPublicationEnhanced
from slc.publications.tests.base import IntegrationTestCase
from zope.component import getUtility
from zope.interface import alsoProvides

import unittest2 as unittest


class TestPublicationsView(IntegrationTestCase):
    """Test for the @@publications_view."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # @@publications_view expects to find File content types in
        # 'publish' state, however, by default Files don't have any
        # workflow assigned to them
        self.workflow.setChainForPortalTypes(['File'], 'plone_workflow')

        # create folders that will hold publications and change their subtype
        # to PublicationContainer
        self.subtyper = getUtility(ISubtyper)
        self.portal.invokeFactory('Folder', 'pubs', title='Publications')
        self.pubs = self.portal.pubs
        self.pubs.invokeFactory('Folder', 'reports')
        self.pubs.invokeFactory('Folder', 'magazines')

        alsoProvides(self.pubs, IPublicationContainerEnhanced)
        alsoProvides(self.pubs.reports, IPublicationContainerEnhanced)
        alsoProvides(self.pubs.magazines, IPublicationContainerEnhanced)
        self.subtyper.change_type(
            self.pubs, u'slc.publications.FolderPublicationContainer')
        self.subtyper.change_type(
            self.pubs.reports, u'slc.publications.FolderPublicationContainer')
        self.subtyper.change_type(
            self.pubs.magazines,
            u'slc.publications.FolderPublicationContainer')

        # add some publications
        self.pubs.invokeFactory('File', 'pub1', title='Pub 1')
        self.pubs.reports.invokeFactory('File', 'pub2', title='Pub 2')
        self.pubs.magazines.invokeFactory('File', 'pub3', title='Pub 3')

        self.pub1 = self.pubs.pub1
        self.pub2 = self.pubs.reports.pub2
        self.pub3 = self.pubs.magazines.pub3

        # set Subjects
        self.pub1.setSubject(['foo', 'bar'])
        self.pub2.setSubject(['foo', ])
        self.pub3.setSubject(['bar', ])

        # publish publications
        self.workflow.doActionFor(self.pub1, 'publish')
        self.workflow.doActionFor(self.pub2, 'publish')
        self.workflow.doActionFor(self.pub3, 'publish')

        # reindex everything to update the catalog
        self.pub1.reindexObject()
        self.pub2.reindexObject()
        self.pub3.reindexObject()

        # publications view
        self.view = self.pubs.restrictedTraverse('@@publications_view')

    def test_get_publications_format(self):
        """Check if results are in the right format."""
        publications = self.view.get_publications()

        self.assertEqual(
            publications,
            [{'effective_date': u'',
              'path': '/plone/pubs/pub1/view',
              'size': '0 kB',
              'type': u'Unknown',
              'title': u'Pub 1'},
             {'effective_date': u'',
              'path': '/plone/pubs/reports/pub2/view',
              'size': '0 kB',
              'type': u'Reports',
              'title': u'Pub 2'},
             {'effective_date': u'',
              'path': '/plone/pubs/magazines/pub3/view',
              'size': '0 kB',
              'type': u'Magazine',
              'title': u'Pub 3'}]
        )

    def test_get_publications_filtering(self):
        """Check if we get correct results for different filter options."""

        # filter by keywords
        self.request.form['keywords'] = ['foo']
        publications = self.view.get_publications()
        self.assertEqual(len(publications), 2)
        self.assertEqual(publications[0]['title'], u'Pub 1')
        self.assertEqual(publications[1]['title'], u'Pub 2')

        # additional filtering by type
        self.request.form['typelist'] = 'reports'
        publications = self.view.get_publications()
        self.assertEqual(len(publications), 1)
        self.assertEqual(publications[0]['title'], u'Pub 2')

    def test_get_publications_order(self):
        """Test if publications are sorted correctly."""

        # set effective dates
        # XXX: why is it set to '1000-01-01' by default?
        self.pub1.setEffectiveDate('2010-01-01')
        self.pub2.setEffectiveDate('2012-01-01')
        self.pub3.setEffectiveDate('2011-01-01')
        self.pub1.reindexObject()
        self.pub2.reindexObject()
        self.pub3.reindexObject()

        publications = self.view.get_publications()

        # Publications should be sorted by creation date (descending)
        self.assertEqual(
            [pub['path'] for pub in publications],
            ['/plone/pubs/reports/pub2/view',
             '/plone/pubs/magazines/pub3/view',
             '/plone/pubs/pub1/view']
        )


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
