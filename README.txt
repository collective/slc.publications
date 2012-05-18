.. contents::

.. Note!
   -----

   - code repository
   - bug tracker
   - questions/comments feedback mail


- Code repository: http://svn.plone.org/svn/collective/slc.publications
- Questions and comments to info (at) syslab (dot) com
- Report bugs at http://plone.org/products/slc.publications/


About
=====

The Publication Product can be used to organise printed publications that are
available online for download. Publications usually have a publication date,
order and ISBN numbers, and an author. They may exist in several language versions.
Once stored in the Publication Product, they can be displayed using
auto-generated overviews.

LinguaPlone
-----------

If LinguaPlone is installed, multiple language versions of a publication can be uploaded. A box that offers a link to every language version will be displayed.

  .. Note::

   LinguaPlone needs to be installed separately, e.g. by adding it to the buildout.


Dependencies
============

You need the following libs available on your system:

 * ``pdfinfo`` (part of the ``xpdf`` package)
 * ``ghostscript``
 * ``convert`` (part of ``ImageMagick``)
 * ``pdftk`` (http://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
 
Credits
=======

Copyright European Agency for Health and Safety at Work and Syslab.com
GmbH.

slc.publications development was funded by the European Agency for
Health and Safety at Work.


License
=======

slc.publications is licensed under the GNU Lesser Generic Public
License, version 2 or later and EUPL version 1.1 only. The complete
license texts can be found in docs/LICENSE.GPL and docs/LICENSE.EUPL.
