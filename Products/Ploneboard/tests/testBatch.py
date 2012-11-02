#
# Ploneboard tests
#

from Products.CMFPlone.utils import _createObjectByType
from Products.Ploneboard.batch import Batch
from Products.Ploneboard.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest


class TestBatch(IntegrationTestCase):

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        folder = portal[portal.invokeFactory('Folder', 'folder')]
        self.board = _createObjectByType('Ploneboard', folder, 'board')
        self.forum = _createObjectByType('PloneboardForum', self.board, 'forum')

    def batch(self, size=5, start=0, orphan=1):
        return Batch(self.forum.getConversations,
                     self.forum.getNumberOfConversations(),
                     size, start, orphan=orphan)

    def sorted(self, b):
        items = [x for x in b]
        items.sort(lambda x, y: cmp(x.Title(), y.Title()))
        return items

    def sbatch(self, size=5, start=0, orphan=1):
        b = self.batch(size, start, orphan)
        return b, self.sorted(b)

    def testEmptyBatch(self):
        b = self.batch()
        self.assertEqual(len(b), 0)
        self.assertEqual(b.next, None)
        self.assertEqual(b.previous, None)

    def testLessThanOnePage(self):
        for i in range(3):
            self.forum.addConversation('Title %02s' % i)
        b, items = self.sbatch()
        self.assertEqual(len(b), 3)
        for i in range(3):
            self.assertEqual(items[i].Title(), 'Title %02s' % i)
        self.assertEqual(b.next, None)
        self.assertEqual(b.previous, None)

    def testExactlyOnePage(self):
        for i in range(5):
            self.forum.addConversation('Title %02s' % i)
        b, items = self.sbatch()
        self.assertEqual(len(b), 5)
        for i in range(5):
            self.assertEqual(items[i].Title(), 'Title %02s' % i)
        self.assertEqual(b.next, None)
        self.assertEqual(b.previous, None)

    def testOnePagePlusOrphan(self):
        for i in range(6):
            self.forum.addConversation('Title %02s' % i)
        b, items = self.sbatch()
        self.assertEqual(len(b), 6)
        for i in range(6):
            self.assertEqual(items[i].Title(), 'Title %02s' % i)
        self.assertEqual(b.next, None)
        self.assertEqual(b.previous, None)

    # note: when testing more than one page, we don't test for the
    # exact objects returned, because getConversations returns things
    # sorted by modified date, but when we create objects in a loop like
    # below, the resolution of the timestamp isn't good enough, and thus order
    # is sometimes unpredictable, leading to non-deterministic tests.

    def testOnePagePlusOneMoreThanOrphan(self):
        for i in range(7):
            self.forum.addConversation('Title %02s' % i)
        b = self.batch()
        self.assertEqual(b.previous, None)
        self.assertNotEqual(b.next, None)
        self.assertEqual(len(b.next), 2)

    def testGetLastPage(self):
        for i in range(8):
            self.forum.addConversation('Title %02s' % i)
        b = self.batch(start=5)
        self.assertEqual(len(b), 3)
        self.assertEqual(b.next, None)
        self.assertNotEqual(b.previous, None)
        self.assertEqual(len(b.previous), 5)

    def testGetMiddlePage(self):
        for i in range(12):
            self.forum.addConversation('Title %02s' % i)
        b = self.batch(start=5)
        self.assertEqual(len(b), 5)
        self.assertNotEqual(b.next, None)
        self.assertNotEqual(b.previous, None)
        self.assertEqual(len(b.next), 2)
        self.assertEqual(len(b.previous), 5)
