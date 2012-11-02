#
# Event notification tests
#

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest
import zope.component


notified = []


@zope.component.adapter(ObjectInitializedEvent)
def dummyEventHandler(event):
    notified.append(event.object)


class TestPloneboardEventNotifications(IntegrationTestCase):
    """Test the events that should be fired when conversations or comments are added"""

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')
        zope.component.provideHandler(dummyEventHandler)

    def testPloneboardEventNotifications(self):
        conv = self.forum.addConversation('subject', 'body')
        self.failUnless(conv in notified)
        comment = conv.addComment('subject', 'body')
        self.failUnless(comment in notified)
