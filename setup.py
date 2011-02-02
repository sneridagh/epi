import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.zodbconn',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'ZODB3',
    'WebError',
    'repoze.who',
    'pyramid_who',
    'pyramid_zcml',
    'mechanize',
    'BeautifulSoup',
    'pyramid_beaker',
    'plone.memoize',
    'zope.app.cache',
    'DateTime',
    ]

setup(name='epi',
      version='0.0',
      description='epi',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="epi",
      entry_points = """\
      [paste.app_factory]
      main = epi:main
      """,
      paster_plugins=['pyramid'],
      )

