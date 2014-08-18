# coding: spec

from __future__ import print_function

from delfick_error import DelfickError, DelfickErrorTestMixin

from contextlib import contextmanager
from unittest import TestCase
import uuid
import mock

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
                    self.assertEqual(str(val), "Regex didn't match: 'blah' not found in 'meh'")

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
                        self.assertEqual(str(val), "Regex didn't match: 'testing for great good' not found in 'testing, 1.. 2.. 3'")

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

