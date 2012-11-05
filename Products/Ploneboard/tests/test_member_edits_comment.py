from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow.WorkflowPolicyConfig import manage_addWorkflowPolicyConfig
from hexagonit.testing.browser import Browser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing import layered
from Products.Ploneboard.tests.base import FUNCTIONAL_TESTING
from zope.testing import renormalizing

import doctest
import manuel.codeblock
import manuel.doctest
import manuel.testing
import re
import transaction
import unittest


FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE


CHECKER = renormalizing.RENormalizing([
    # Normalize the generated UUID values to always compare equal.
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<UUID>'),
])


def addMember(portal, username, fullname="", email="", roles=('Member',), last_login_time=None):
    portal.portal_membership.addMember(username, 'secret', roles, [])
    member = portal.portal_membership.getMemberById(username)
    member.setMemberProperties({'fullname': fullname, 'email': email,
                                'last_login_time': DateTime(last_login_time),})


def setUpDefaultMembersBoardAndForum(portal):
    addMember(portal, 'member1', 'Member one', 'member1@example.com', roles=('Member',))
    addMember(portal, 'member2', 'Member two', 'member2@example.com', roles=('Member',))
    addMember(portal, 'manager1', 'Manager one', 'manager1@example.com', roles=('Manager',))
    addMember(portal, 'reviewer1', 'Reviewer one', 'reviewer1@example.com', roles=('Reviewer',))

    board = portal[portal.invokeFactory('Ploneboard', 'board1')]
    board.addForum('forum1', 'Forum 1', 'Forum one')


def setupEditableForum(portal):
    forum = portal['board1']['forum1']
    manage_addWorkflowPolicyConfig(forum)
    pw_tool = portal.portal_placeful_workflow
    config = pw_tool.getWorkflowPolicyConfig(forum)
    config.setPolicyIn(policy='EditableComment')
    config.setPolicyBelow(policy='EditableComment', update_security=True)


def setUp(self):
    layer = self.globs['layer']
    browser = Browser(layer['app'])
    portal = layer['portal']
    workflow = getToolByName(portal, 'portal_workflow')

    self.globs.update({
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
        'browser': browser,
        'portal': portal,
        'workflow': workflow,
    })

    browser.setBaseUrl(portal.absolute_url())

    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()

    setRoles(portal, TEST_USER_ID, ['Manager'])

    setUpDefaultMembersBoardAndForum(portal)
    setRoles(portal, 'reviewer1', ['Reviewer'])

    setupEditableForum(portal)


    transaction.commit()


def DocFileSuite(testfile, flags=FLAGS, setUp=setUp, layer=FUNCTIONAL_TESTING):
    """Returns a test suite configured with a test layer.

:param testfile: Path to a doctest file.
:type testfile: str

:param flags: Doctest test flags.
:type flags: int

:param setUp: Test set up function.
:type setUp: callable

:param layer: Test layer
:type layer: object

:rtype: `manuel.testing.TestSuite`
"""
    m = manuel.doctest.Manuel(optionflags=flags, checker=CHECKER)
    m += manuel.codeblock.Manuel()

    return layered(
        manuel.testing.TestSuite(m, testfile, setUp=setUp, globs=dict(layer=layer)),
        layer=layer)


def test_suite():
    return unittest.TestSuite([
        DocFileSuite('MemberEditsComment.txt'),
        ])
