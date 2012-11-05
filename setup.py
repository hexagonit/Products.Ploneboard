from setuptools import setup, find_packages

name = 'Products.Ploneboard'
version = '3.3.0.1'

setup(name='Products.Ploneboard',
      version=version,
      description="A discussion board for Plone.",
      long_description=open("README.txt").read() + \
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone board forum',
      author='Jarn, Wichert Akkerman, Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/Products.Ploneboard',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.CMFPlacefulWorkflow',
        'Products.CMFPlone >= 4.1',
        'Products.SimpleAttachment',
        'hexagonit.testing',
        'plone.app.controlpanel',
        'plone.app.portlets',
        'plone.i18n',
        'plone.memoize',
        'plone.portlets',
        'python-dateutil<2.0dev',
        'setuptools',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
