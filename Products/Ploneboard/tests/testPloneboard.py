#
# Ploneboard tests
#

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.Extensions import Install  # Catch errors in Install
from Products.Ploneboard.content.Ploneboard import Ploneboard
from Products.Ploneboard.interfaces import IPloneboard, IForum
from Products.Ploneboard.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zExceptions import Unauthorized
from zope.interface.verify import verifyClass, verifyObject

import unittest


class TestPloneboardBasics(IntegrationTestCase):
    """Test the basics, like creation"""

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def testPloneboardCreation(self):
        """Try creating and deleting a board"""
        board_id = 'board'
        board = _createObjectByType('Ploneboard', self.portal, board_id)
        self.failIfEqual(board, None)
        self.failUnless(board_id in self.portal.objectIds())
        self.portal._delObject(board_id)
        self.failIf(board_id in self.portal.objectIds())


class TestPloneboardInterface(IntegrationTestCase):
    """Test if it fulfills the interface"""

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board')

    def testInterfaceVerification(self):
        self.failUnless(verifyClass(IPloneboard, Ploneboard))

    def testInterfaceConformance(self):
        self.failUnless(IPloneboard.providedBy(self.board))
        self.failUnless(verifyObject(IPloneboard, self.board))

    def testAddForum(self):
        """Create new folder in home directory & check its basic
        properties and behaviour"""
        board = self.board
        forum_id = 'forum'
        board.addForum(forum_id, 'title', 'description')
        self.failUnless(forum_id in board.objectIds())
        forum = getattr(board, forum_id)
        self.failUnless(IForum.providedBy(forum))

    def testRemoveForum(self):
        board = self.board
        forum_id = 'forum'
        board.addForum(forum_id, 'title', 'description')
        board.removeForum(forum_id)
        self.failIf(forum_id in board.objectIds())

    def testGetForum(self):
        board = self.board
        forum_id = 'forum'
        board.addForum(forum_id, 'title', 'description')
        forum = board.getForum(forum_id)
        self.failUnless(IForum.providedBy(forum))

    def testGetForumIds(self):
        board = self.board
        forum_ids = ['forum1', 'forum2']
        for forum_id in forum_ids:
            board.addForum(forum_id, 'title', 'description')
        self.failUnlessEqual(forum_ids, board.getForumIds())

    def testGetForums(self):
        board = self.board
        forum_ids = ['forum1', 'forum2']
        for forum_id in forum_ids:
            board.addForum(forum_id, 'title', 'description')
        self.failUnlessEqual(
                set([board.getForum(forum_id) for forum_id in forum_ids]),
                set(board.getForums()))

    def testSearchComments(self):
        pass


class TestPloneboardWithoutContainment(IntegrationTestCase):
    """Test a single board used more as a topic, with forums in folders"""

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        self.folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', self.folder, 'board')

    def testGetForumsOutsideBoard(self):
        forum1 = _createObjectByType('PloneboardForum', self.folder, 'forum1')
        forum2 = _createObjectByType('PloneboardForum', self.folder, 'forum2')
        forums = self.board.getForums(sitewide=True)
        self.failUnless(forum1 in forums)
        self.failUnless(forum2 in forums)


class TestPloneboardRSSFeed(IntegrationTestCase):

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board',
                title='Test Board')
        self.syn_tool = getToolByName(portal, 'portal_syndication')
        self.view = self.board.restrictedTraverse("@@RSS")

    def testEnablingSyndication(self):
        self.assertEqual(self.syn_tool.isSyndicationAllowed(self.board), False)
        self.syn_tool.enableSyndication(self.board)
        self.assertEqual(self.syn_tool.isSyndicationAllowed(self.board), True)

    def testViewNotAllowedWithSyndicationDisabled(self):
        self.assertRaises(Unauthorized, self.view.__call__)

    def testViewUrl(self):
        self.assertEqual(self.view.url(), self.board.absolute_url())

    def testViewDate(self):
        self.assertEqual(self.view.date(), self.board.modified().HTML4())

    def testViewTitle(self):
        self.assertEqual(self.view.title(), 'Test Board')

    def testHumbleBeginnings(self):
        self.view.update()
        self.assertEqual(self.view.comments, [])

    def testFirstComment(self):
        forum=self.board.addForum('forum1', 'Title one', 'Description one')
        conv=forum.addConversation('Conversation one', 'Text one')
        conv.addComment("comment title", "comment body")
        self.view.update()
        self.assertEqual(len(self.view.comments), 2) # original text is first comment

    def testCommentInfo(self):
        forum=self.board.addForum('forum1', 'Title one', 'Description one')
        conv=forum.addConversation('Conversation one', 'Text one')
        conv.addComment("comment title", "comment body")
        self.view.update()
        comment=self.view.comments[0]
        self.assertEqual(comment['title'], 'comment title')
        self.assertEqual(comment['description'], 'comment body')
        self.assertEqual(comment['author'], 'test_user_1_')
        self.failUnless('date' in comment)
        self.failUnless('url' in comment)
