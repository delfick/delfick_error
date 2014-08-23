# coding: spec

from __future__ import print_function

from delfick_error import DelfickError, DelfickErrorTestMixin

from contextlib import contextmanager
from unittest import TestCase
import random
import uuid
import mock
import six

# Used in the tests
class AError(DelfickError): pass
class BError(DelfickError): pass
class CError(DelfickError): pass

describe TestCase, "DelfickError":
    it "creates a message that combines desc on the class, args and kwargs":
        error = DelfickError("The syncing was bad", a=4, b=5)
        self.assertEqual(str(error), '"The syncing was bad"\ta=4\tb=5')

    it "Works without a message":
        error = DelfickError(a_thing=4, b=5)
        self.assertEqual(str(error), 'a_thing=4\tb=5')

    it "works with subclasses of DelfickError":
        class OtherSyncingErrors(DelfickError):
            desc = "Oh my!"
        error = OtherSyncingErrors("hmmm", d=8, e=9)
        self.assertEqual(str(error), '"Oh my!. hmmm"\td=8\te=9')

        error2 = OtherSyncingErrors(f=10, g=11)
        self.assertEqual(str(error2), '"Oh my!"\tf=10\tg=11')

    it "can tell if an error is equal to another error":
        class Sub1(DelfickError):
            desc = "sub"
        class Sub2(DelfickError):
            desc = "sub"

        self.assertNotEqual(Sub1("blah"), Sub2("blah"))
        self.assertNotEqual(Sub1("blah", one=1), Sub1("blah", one=2))

        self.assertEqual(Sub1("blah"), Sub1("blah"))
        self.assertEqual(Sub1("blah", one=1, two=2), Sub1("blah", two=2, one=1))

    it "treats _errors as a special kwarg":
        error1 = uuid.uuid1()
        error2 = uuid.uuid1()
        errors = [error1, error2]

        error = DelfickError("hmmm", _errors=errors)
        self.assertEqual(error.errors, errors)
        assert "_errors" not in error.kwargs

        self.assertEqual(str(error), "\"hmmm\"\nerrors:\n\t{0}\n\t{1}".format(error1, error2))

    it "can format special values":
        class WithFormat(object):
            def __init__(self, val):
                self.val = val

            def delfick_error_format(self, key):
                return "formatted_{0}_{1}".format(key, self.val)

        error = DelfickError(blah=WithFormat(1), meh=WithFormat(2), things=3)
        self.assertEqual(str(error), "blah=formatted_blah_1\tmeh=formatted_meh_2\tthings=3")

    describe "formatted_val":
        it "just returns val if has no delfick_error_format attribute":
            key = mock.Mock(name="key")
            self.assertEqual(DelfickError().formatted_val(key, 3), 3)

        it "returns result of calling delfick_error_format if it has one":
            key = mock.Mock(name="key")
            thing = mock.Mock(name="thing")
            thing.delfick_error_format.return_value = 50

            self.assertEqual(DelfickError().formatted_val(key, thing), 50)

        it "passes in the key to delfick_error_format":
            key = mock.Mock(name="key")
            thing = mock.Mock(name="thing")
            thing.delfick_error_format.return_value = 50

            self.assertEqual(DelfickError().formatted_val(key, thing), 50)
            thing.delfick_error_format.assert_called_once_with(key)

        it "catches any exception from delfick_error_format":
            key = mock.Mock(name="key")
            error = DelfickError("blah")
            thing = mock.Mock(name="thing")
            thing.delfick_error_format.side_effect = error

            self.assertEqual(DelfickError().formatted_val(key, thing), "<|Failed to format val for exception: val={0}, error={1}|>".format(thing, error))

    describe "Sorting":
        def assertSorted(self, *errors):
            """Shuffle the provided errors and make sure they always get sorted into the provided order"""
            expected = list(errors)
            errors = list(errors)
            print("Expect result of {0}".format(expected))
            print("---")
            def compare(attmpt):
                print("Sorting {0}".format(attmpt))
                sortd = sorted(attmpt)
                print("Got {0}".format(sortd))
                self.assertEqual(sortd, expected)
                print("===")

            for attempt in (errors, list(reversed(errors))):
                compare(attempt)

            for _ in range(5):
                random.shuffle(errors)
                compare(errors)

        it "sorts based on class first":
            self.assertSorted(
                AError("b"), BError("d"), CError("a")
            )

            self.assertSorted(
                AError("b", b=2), BError("a", a=1)
            )

            self.assertSorted(
                AError("b", c=3, _errors=[3, 4]), CError("a", c=2, _errors=[1, 2])
            )

        it "sorts on message second":
            self.assertSorted(
                AError("zadf"), AError("zsdf"), BError("gd"), BError("he"), CError("a")
            )

        it "sorts on kwargs third":
            self.assertSorted(
                AError("zsdf", b=2, c=3), BError("zsdf", a=1), BError("zsdf", a=2, b=4), CError("zsdf", c=1)
            )

        it "sorts on errors last":
            self.assertSorted(
                AError("asdf", a=1, _errors=[5, 4]), AError("asdf", a=1, _errors=[6, 1]), BError("asdf", a=1, _errors=[1, 2]), BError("asdf", a=1, _errors=[1, 2, 1])
            )

# Some objects for my expecting_raised_assertion helper
class Called(object): pass
class BeforeManager(object): pass
class InsideManager(object): pass
class AssertionRaised(object): pass
class NoAssertionRaised(object): pass
class NonAssertionRaised(object): pass

class DelfickErrorCase(TestCase, DelfickErrorTestMixin):
    __test__ = False
    def runTest(self, *args, **kwargs): pass

describe TestCase, "Tests mixin":
    describe "AssertIs":
        it "provides an implementation of assertIs that works":
            m1 = mock.Mock(name='m1')
            m2 = mock.Mock(name='m2')

            try:
                DelfickErrorCase().assertIs(m1, m2, "blah")
                assert False, "Expected an assertion error"
            except AssertionError as error:
                if six.PY3:
                    self.assertEqual(str(error), "{0} is not {1} : blah".format(m1, m2))
                else:
                    self.assertEqual(str(error), "blah")

            try:
                DelfickErrorCase().assertIs(m1, m2)
                assert False, "Expected an assertion error"
            except AssertionError as error:
                self.assertEqual(str(error), "{0} is not {1}".format(m1, m2))

            try:
                DelfickErrorCase().assertIs(m1, m1)
                assert True, "Expected no assertion error"
            except AssertionError as error:
                assert False, "Didn't expect an assertion error, got {0}".format(error)

    describe "Fuzzy assert raises":
        def expecting_raised_assertion(self, *args, **kwargs):
            """Yield (iterator, val) from _expecting_raised_assertion"""
            iterator = self._expecting_raised_assertion(*args, **kwargs)
            while True:
                val = next(iterator)
                yield iterator, val

        def _expecting_raised_assertion(self, called, *args, **kwargs):
            """Assert that an assertion is raised and yield that assertion for more checks"""
            buf = []
            called.append(BeforeManager)
            yield (BeforeManager, None)
            try:
                with DelfickErrorCase().fuzzyAssertRaisesError(*args, **kwargs):
                    called.append(InsideManager)
                    for_raising = yield (InsideManager, None)
                    if for_raising:
                        raise for_raising
                called.append(NoAssertionRaised)
                yield (NoAssertionRaised, None)
            except AssertionError as error:
                print("Assertion raised: '{0}: {1}'".format(error.__class__, error))
                called.append(AssertionRaised)
                buf.append((AssertionRaised, error))
            except Exception as error:
                print("Non assertion raised: '{0}: {1}'".format(error.__class__, error))
                called.append(NonAssertionRaised)
                buf.append((NonAssertionRaised, error))

            # For some reason these values don't come through
            # Unless I yield something before them
            # Outside of the catch blocks...
            # *keeps calm and carries on*
            yield (None, None)
            for val in buf:
                yield val

            # Yield called for sanity checks
            yield (Called, called)

        it "complains if no exception is raised":
            called = []
            for iterator, (part, val) in self.expecting_raised_assertion(called, Exception):
                if part is InsideManager:
                    pass
                elif part is AssertionRaised:
                    assert str(val).startswith("Expected an exception to be raised"), str(val)
            self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

        it "complains if exception is not a subclass of what is expected":
            raised = TypeError("ERROR!")

            called = []
            for iterator, (part, val) in self.expecting_raised_assertion(called, ValueError):
                if part is InsideManager:
                    iterator.send(raised)
                elif part is AssertionRaised:
                    self.assertEqual(str(val), "Expected {0}, got {1}".format(ValueError, TypeError))

            self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

        it "complains if exception is subclass but doesn't match regex":
            class Raised(ValueError): pass
            raised = Raised("blah")

            called = []
            for iterator, (part, val) in self.expecting_raised_assertion(called, ValueError, "meh"):
                if part is InsideManager:
                    iterator.send(raised)
                elif part is AssertionRaised:
                    self.assertEqual(str(val), "Regex didn't match: 'meh' not found in 'blah'")

            self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

        it "works fine if regex and subclass match":
            class Expected(IndexError): pass
            class Raised(Expected): pass
            raised = Raised("stuff")

            called = []
            for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, "stuff"):
                if part is InsideManager:
                    iterator.send(raised)

            self.assertEqual(called, [BeforeManager, InsideManager, NoAssertionRaised])

        describe "For DelfickError exceptions":
            it "complains if any given kwargs doesn't match":
                class Expected(DelfickError): pass

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, one=1, two=1, three=1):
                    if part is InsideManager:
                        iterator.send(Expected(one=1, two=2, three=3))
                    elif part is AssertionRaised:
                        self.assertEqual(str(val), "Mismatched: {'three': expected=1, got=3}, {'two': expected=1, got=2}")

                self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

            it "complains about any missing kwargs from what we specify":
                class Expected(DelfickError): pass

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, one=1, three=1, four=1):
                    if part is InsideManager:
                        iterator.send(Expected(one=1))
                    elif part is AssertionRaised:
                        self.assertEqual(str(val), "Missing: 'four', 'three'")

                self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

            it "doesn't care about extra kwargs in what was raised":
                class Expected(DelfickError): pass

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, one=1):
                    if part is InsideManager:
                        iterator.send(Expected(one=1, two=2))

                self.assertEqual(called, [BeforeManager, InsideManager, NoAssertionRaised])

            it "complains about message before kwargs":
                class Expected(DelfickError):
                    desc = "expected"
                class Raised(Expected):
                    desc = "raised"

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Raised, "testing, 1.. 2.. 3", one=1, three=2):
                    if part is InsideManager:
                        iterator.send(Raised("testing for great good", one=1, three=3))
                    elif part is AssertionRaised:
                        self.assertEqual(str(val), "Regex didn't match: 'testing, 1.. 2.. 3' not found in 'testing for great good'")

                self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

            it "complains if errors aren't the same":
                class Expected(DelfickError): pass

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, one=1, _errors=[3, 5, 10, 4]):
                    if part is InsideManager:
                        iterator.send(Expected(one=1, two=2, _errors=[20, 5, 4, 3]))
                    elif part is AssertionRaised:
                        assert "[3, 4, 5, 20] != [3, 4, 5, 10]" in str(val), str(val)

                self.assertEqual(called, [BeforeManager, InsideManager, AssertionRaised])

            it "does a sorted comparison of the errors":
                class Expected(DelfickError): pass

                called = []
                for iterator, (part, val) in self.expecting_raised_assertion(called, Expected, one=1, _errors=[3, 5, 10, 4]):
                    if part is InsideManager:
                        iterator.send(Expected(one=1, two=2, _errors=[10, 5, 4, 3]))

                self.assertEqual(called, [BeforeManager, InsideManager, NoAssertionRaised])

