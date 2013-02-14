Changelog
=========

4.1 (2013-02-14)
----------------

- Publications revamp #3790 [jcerjak]


4.0 (2012-09-17)
----------------

- Plone 4 release


4.0a1 (2012-02-02)
------------------

- Nothing changed yet.


1.1.26 (2011-03-14)
-------------------

- Show belowcontenttitle on the publication view [thomasw]

1.1.25 (2011-02-21)
-------------------

- Deleted onclick event (call to pageTracker) on PDF download link. Instead added
  class publicationURL around all download links [thomasw]

1.1.24 (2010-11-26)
-------------------

- item url in Related Resources now really really points to /view. Really.
  Fixes #1148 [thomasw]


1.1.23 (2010-11-23)
-------------------

- item url in related_items always points to /view now. Fixes #1148
  [pilz]


1.1.22 (2010-11-22)
-------------------

- item url in publication_relatedItems always points to /view now. Fixes #1148
  [pilz]


1.1.21 (2010-11-05)
-------------------

- 2 bugfixes concerning _get_storage_folder [thomasw]

1.1.20 (2010-10-05)
-------------------

- Enhancements / Bugfixes for translated Publications with chapters. Chapters (ATLinks) are now
  correctly copied over from the canonical to translations 
  [thomasw]
- Now propagating values of languageIndependent schema-extended fields actually works for LinguaPlone 2.2 
  [thomasw]

1.1.19 (2010-07-14)
-------------------

- Added a GA pagetracker to the download link
  [pilz]

1.1.18 (2010-07-06)
-------------------

- The EU-Bookshop has changed their URL format for publications yet again.
  Adapted the publication view accordingly [thomasw]


1.1.17 (2010-06-19)
-------------------

- fixed download speed calculations (pilz)


1.1.16 (2010-06-09)
-------------------

- Bugfix in publication view: don't show links to translations which the user
  may not see (thomasw)

1.1.15 (2009-03-03)
-------------------

- bugfix: file_view creates a folder to hold extra data such as Link
  objects pointing to chapters in the pdf file. Now bypassing security
  checks so that this will also be created when an Anonymous user
  views the publication (deroiste)
- bugfix: BaseAttributeExtractor was defined incorrectly for the case that slc.xliff is not installed (thomasw)


1.1.14 (2009-12-07)
-------------------

- Refined overrides.zcml. It will now also work with newer plone.app.blob
  versions and images in blob. (gerken)
- Change related publications boxes to "key resources" (manually added) and "related resources" (Keyword based) Change requested by Sarah during Bilbao meeting 30.11-1.12.2009  #439 (pilz)
- Added EUPL license (deroiste)


1.1.13 (2009-11-09)
-------------------

- removed unnecessary reference to OSHA in subtyper/publication.py (thomasw)
- typo in FR translation (thomasw)
- added possibility to display additional info on the view of a publication via an adapter (thomasw)

1.1.12 (2009-10-18)
-------------------

-translate the contents of the author field - workaround since the field is language-independent (thomasw)

1.1.11 (2009-10-14)
-------------------

- rerelease. There was a mistake where parts of the package did not get into the egg

1.1.10 (2009-10-13)
-------------------

- fixed an inconsistency in the related publications where language indepentent was not used (pilz)
- replaced all occurences of i18n:translate in the publication_view template 
  with a call to a method on the view that uses MessageFactory. I couldn't figure
  out why i18n:translate worked for some langs, and not for others such as NL (thomasw)



1.1.9 (2009-10-06)
------------------
- Chapter links now always point to the url. Normally, if you click on a link
  and you have edit rights, you would go to the link view and not to the link 
  target. Since we already offer a second edit link, when somebody has edit 
  rights, the regular link can point directly to the place the link points to. 
  (gerken)

- Refactored the Chapter Update functionality. It is not a method any longer
  but a class. That way one can modify the behaviour without the need to
  copy the complete functionality (gerken)

1.1.8 (2009-09-30)
------------------
- Hide the JS-scanner induced PDF icon from the Related publications list on the publication's view (jcbrand)

1.1.7 (2009-09-15)
------------------
- Add try,except to decouple from Products.LinguaPlone (jcbrand)
- don't display a JS-scanner--induced PDF-icon in front of the publication's title (thomasw)

1.1.6 (2009-08-26)
------------------

- Add remove_additionals event handler in adapter/events.py and register it via zcml for IObjectRemovedEvent (jcbrand)
- Edited the object_added event: removed the code that sets translation
  references, it has been superseded by slc.autotranslate. (jcbrand)
- Removed _findAbbrev in adapter/events.py, it's no longer being called (jcbrand)
- Added a new doctest file events.txt to test for the above actions. (jcbrand)

1.1.5 (2009-08-13)
------------------

- enhanced setuphandlers.py (together with import_steps.xml and config.py) to automatically install dependencies. (jcbrand)
- remove explicit blob checking in adapter/publication.py and instead do it via zcml, i.e zcml:condition="installed plone.app.blob" (jcbrand)
- modified addTranslation patch to return the translated item as is done in of LinguaPlone >= 2.3 (jcbrand)
- various new translations have been added (thomasw)

1.1.4 (2009-07-26)
------------------

- have links to publication language versions open in a new window (pilz)

1.1.3 (2009-07-03)
------------------

- changed the link format for the EU Bookshop to fit the new guideline (thomasw)
- Make 'related content' box look like the 'related publications' box (jcbrand)

1.1.2 (2009-06-19)
------------------

- svn:ignore cleanup, removed prints

- test fixes (gerken)

1.1.1 (2009-06-04)
------------------

- made a release without the svn revision in the tag

1.1 (2009-06-04)
----------------

* added a download time estimation control [pilz]
* removed the hardcoded author from the config file and the schema [pilz]
* Trying to make it work without Linguaplone as well [pilz]
* added link to title and image [pilz]
* Added possibility to add manual relations to other content types. This 
  includes a language fallback [brand]
  

1.0 final
---------

* no changes

1.0 beta3
---------

* Added support for slc.xliff
* refactored the adapter.py into adapter/ subdir
* Added an eventhandler to automatically set the suptype on files added to a publication folder
* Added an eventhandler to detect the uploaded language if the filename starts or 
  ends with a lang abbrev
  E.g. XX_filename.pdf or filename_XX.pdf or XX-filename.pdf or filename-XX.pdf.
* Added a patch for linguaplone inserting a new event to allow translating 
  subtyped objects. Translations need to be subtyped just after the object has 
  been created and before attributes are edited.

1.0 beta2
---------

* Switch to p4a.subtyper to make publications out of files
* Use Archetypes.schemaextender to marry normal and publication attributes in one interface
* readded cover image generation

1.0 beta1
---------

* Plone 3 compatibility. Removed the PublicationFolder concept and base completely on Linguaplone

0.9 beta
--------

* initial release
  Thanks to Alin Voinea for creating a Plone2.5 backport. Please see the svn repository for that.
