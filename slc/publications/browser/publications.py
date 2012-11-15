import logging
import os
import subprocess
import tempfile

from DateTime import DateTime

from ordereddict import OrderedDict

from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.publications import HAVE_LINGUAPLONE
from slc.publications.utils import _get_storage_folder


logger = logging.getLogger('slc.publications.publications.publications.py')

# Constants
MAX_RESULTS = 20


class PublicationsView(BrowserView):
    """ Filter/Search for Publications """

    template = ViewPageTemplateFile('templates/publications.pt')
    #template.id = "publications-view"

    has_more_results = False

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.now = DateTime()
        self.portal = getSite()
        self.pc = self.portal.portal_catalog
        self.path = '/'.join(context.getPhysicalPath())
        self.publication_types = OrderedDict({
                "factsheets": _(u"Factsheets"),
                "reports": _(u"Reports"),
                "literature_reviews": _(u"Literature reviews"),
                "e-facts": _(u"E-facts"),
                "outlook": _(u"Outlook"),
                "forum": _(u"Forum"),
                "magazine": _(u"Magazine"),
                "annual_report": _(u"Annual report"),
                "work_programmes": _(u"Work programmes"),
                "evaluation_reports": _(
                    u"Evaluation reports of Agency activities "),
                "other": _(u"Other Publications")
                })
        self.keywords = self.get_keywords()

    def __call__(self):
        return self.template()

    def get_publications(self):
        form = self.request.form
        type_path = self.path + "/" + form.get('typelist', '')
        keywords = form.get("keywords")
        query = {
            'object_provides':
                'slc.publications.interfaces.IPublicationEnhanced',
            'review_state': 'published',
            'SearchableText': form.get("SearchableText", ''),
            'path': type_path,
            }
        if keywords:
            query['Subject'] = keywords

        brains = self.pc.searchResults(query)

        show_all = form.get("show-all", False)
        results = show_all and brains or brains[:MAX_RESULTS]
        if len(brains) > MAX_RESULTS and show_all == False:
            self.has_more_results = True

        publications = []
        translations = getToolByName(self.context, 'translation_service')

        for result in results:
            obj = result.getObject()
            path = result.getPath()
            date = translations.ulocalized_time(result.effective)

            publications.append({
                "title": result.Title.decode("utf-8").replace("'", "&#39;"),
                 "effective_date": date,
                 "size": obj.getObjSize(),
                 "path": path + "/view",
                 "type": self.get_publication_type(path),
                 })
        return publications

    def get_carousel_details(self):
        query = {'object_provides':
                     'slc.publications.interfaces.IPublicationEnhanced',
                 'review_state': 'published'}
        pubs = [i.getObject() for i in self.pc.searchResults(query)[:5]]
        pub_details = []
        for pub in pubs:
            pub_details.append({
                    "absolute_url": pub.absolute_url(),
                    "title": pub.Title(),
                    "images": [],
                    "description": pub.Description(),
                    "images": self._get_carousel_images(pub)})
        return pub_details

    def _get_carousel_images(self, pub):
        pub_folder          = _get_storage_folder(pub)
        pub_folder_contents = pub_folder.objectIds()

        if "carousel_1.gif" not in pub_folder_contents:
            self._generate_carousel_images(pub, pub_folder)

        images = [
            i for i in pub_folder_contents
            if i.startswith("carousel_")]
        return images

    def _generate_carousel_images(self, pub, pub_folder):
        pub_folder = _get_storage_folder(pub)
        tmp_pdf_in = tmp_dir = None
        status     = 1

        try:
            if HAVE_LINGUAPLONE:
                mainpub = pub.getCanonical()
            else:
                mainpub = pub

            data = str(mainpub.getFile())
            if not data:
                return 0

            fd, tmp_pdf_in = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            tmp_dir = tempfile.mkdtemp()

            fhout = open(tmp_pdf_in, "w")
            fhout.write(data)
            fhout.seek(0)

            # There isn't a nice way to only split the first 3 pages
            split_pdf_cmd = "pdftk %s burst output %s/%%04d.pdf" % (
                tmp_pdf_in, tmp_dir)
            self._run_shell_command(split_pdf_cmd)

            pdfs_to_images_cmd = (
                "convert %s/000[1,2,3].pdf -resize 180x255 %s/%%04d.gif" % (
                    tmp_dir, tmp_dir))
            self._run_shell_command(pdfs_to_images_cmd)

            imgfiles = [
                gif for gif in os.listdir(tmp_dir)
                if os.path.splitext(gif)[1] == '.gif']
            imgfiles.sort()

            for i, img in enumerate(imgfiles):
                img = open(os.path.join(tmp_dir, img), "r")
                img_data = img.read()
                img.close()

                pub_folder.invokeFactory(
                    "Image", "carousel_%s.gif" % i, image=img_data)

        except Exception, e:
            logger.warn("generateImage: Could not autoconvert because: %s" % e)
            status = 0

        # try to clean up
        if tmp_pdf_in is not None:
            try:
                os.remove(tmp_pdf_in)
            except:
                pass
        if tmp_dir is not None:
            try:
                for i in os.listdir(tmp_dir):
                    path = os.path.join(tmp_dir, i)
                    print "removing %s" % path
                    os.remove(path)
                os.removedirs(tmp_dir)
            except:
                pass

        return status

    def _run_shell_command(self, cmd):
        logger.info("Running command: %s" % cmd)
        try:
            process = subprocess.Popen(
                cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
        except Exception, e:
            logger.error("Failed to run command: %s\n Exception: %s" % (
                    cmd, e))
        if process.returncode == 1:
            logger.warn("Failed to run command: %s" % cmd)

    def get_publication_type(self, path):
        """The publication type is determined by the folder"""
        for pub_type in self.publication_types.keys():
            pub_type_path = self.path + "/" + pub_type
            if pub_type_path in path:
                return self.publication_types[pub_type]
        return _(u"Unknown")

    def get_keywords(self):
        brains = self.pc.searchResults({
            'object_provides':
            'slc.publications.interfaces.IPublicationEnhanced',
            'review_state': "published",
            'path': self.path,
        })
        keywords = set()
        for brain in brains:
            for keyword in brain.Subject:
                keywords.add(keyword)
        return keywords


class PublicationsJSONView(PublicationsView):
    """Return search results in JSON"""

    def __call__(self):
        """JSON"""
        pubs = self.get_publications()
        return str(pubs).replace("'", '"').replace('u"', '"')
