from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import unittest


class ProductsPloneboardLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""

        # Required by Products.CMFPlone:plone-content to setup defaul plone site.
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'Products.Ploneboard')
        z2.installProduct(app, 'Products.SimpleAttachment')

        # Load ZCML
        import Products.Ploneboard
        self.loadZCML(package=Products.Ploneboard)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup

        # Installs all the Plone stuff. Workflows etc. to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone')

        # Install portal content. Including the Members folder! to setup defaul plone site.
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')

        self.applyProfile(portal, 'Products.Ploneboard:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'Products.SimpleAttachment')
        z2.uninstallProduct(app, 'Products.Ploneboard')
        z2.uninstallProduct(app, 'Products.PythonScripts')


FIXTURE = ProductsPloneboardLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="ProductsPloneboardLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="ProductsPloneboardLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING