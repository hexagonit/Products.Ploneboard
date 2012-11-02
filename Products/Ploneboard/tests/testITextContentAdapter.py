#
# Comment tests
#

from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.tests import PloneboardTestCase
from Products.Ploneboard.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest


class TestITextContentAdapter(IntegrationTestCase):

    def setUp(self):
        from Products.ATContentTypes.interface import ITextContent
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        self.conv = self.forum.addConversation('conv1', 'conv1 body')
        self.comment = self.conv.addComment("c1 title", "c1 body")
        self.textContent = ITextContent(self.comment)

    def testGetText(self):
        self.assertEqual(self.comment.getText(),
                         self.textContent.getText())

    def testSetText(self):
        s = 'blah'
        self.textContent.setText('blah')

        self.assertEqual(self.comment.getText(), s)
        self.assertEqual(self.textContent.getText(), s)

    def testCookedBody(self):
        self.assertEqual(self.textContent.CookedBody(),
                         self.comment.getText())

    def testEditableBody(self):
        self.assertEqual(self.textContent.CookedBody(),
                         self.comment.getRawText())
