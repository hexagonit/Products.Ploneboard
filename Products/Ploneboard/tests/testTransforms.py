#
# Ploneboard transform tests
#

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.config import PLONEBOARD_TOOL
from Products.Ploneboard.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest


class TestTransformRegistration(IntegrationTestCase):
    """Test transform registration """

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        folder = self.portal[self.portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board')

    def testDefaultRegistrations(self):
        """Check if the default registrations are present."""
        tool = getToolByName(self.portal, PLONEBOARD_TOOL)
        self.failUnlessEqual(len(tool.getTransforms()), 3)
        self.failUnlessEqual(len(tool.getEnabledTransforms()), 3)

    def testDisabling(self):
        """Try registering and unregistering a transform"""
        tool = getToolByName(self.portal, PLONEBOARD_TOOL)
        tool.enableTransform('safe_html', enabled=False)
        self.failIf('safe_html' in tool.getEnabledTransforms())
        tool.enableTransform('safe_html')
        self.failUnless('safe_html' in tool.getEnabledTransforms())

    def testUnregisteringAllRemovesOnlyThoseAdded(self):
        tool = getToolByName(self.portal, PLONEBOARD_TOOL)
        tool.unregisterAllTransforms()
        transforms = getToolByName(self.portal, 'portal_transforms')
        self.failIf('url_to_hyperlink' in transforms.objectIds())
        self.failIf('text_to_emoticons' in transforms.objectIds())
        self.failUnless('safe_html' in transforms.objectIds())

    def testUnregisteringIndividualRemovesOnlyThoseAdded(self):
        tool = getToolByName(self.portal, PLONEBOARD_TOOL)
        transforms = getToolByName(self.portal, 'portal_transforms')
        tool.unregisterTransform('url_to_hyperlink')
        self.failIf('url_to_hyperlink' in transforms.objectIds())
        tool.unregisterTransform('safe_html')
        self.failUnless('safe_html' in transforms.objectIds())
