# coding: spec

from delfick_error import DelfickError

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

