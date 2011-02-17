""" Installer
"""
from setuptools import setup, find_packages
import os
from os.path import join

NAME = 'slc.publications'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="A content type to store pdf publications",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone content publications pdf parse metadata',
      author='Syslab.com GmbH',
      author_email='info@syslab.com GmbH',
      url='http://plone.org/products/PublicationProduct',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
