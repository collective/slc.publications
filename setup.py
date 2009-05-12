from setuptools import setup, find_packages

version = '1.0.2'

setup(name='slc.publications',
      version=version,
      description="A content type to store and parse pdf publications",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone content publications pdf parse metadata',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='http://plone.org/products/PublicationProduct',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.common',
          'p4a.z2utils',
          'p4a.subtyper',
          'archetypes.schemaextender',
          
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
