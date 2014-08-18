from __future__ import print_function
from contextlib import contextmanager
import sys

class DelfickError(Exception):
    """Helpful class for creating custom exceptions"""
    desc = ""

    def __init__(self, message="", **kwargs):
        self.kwargs = kwargs
        self.errors = kwargs.get("_errors", [])
        if "_errors" in kwargs:
            del kwargs["_errors"]
        self.message = message
        super(DelfickError, self).__init__(message)

    def __str__(self):
        message = self.oneline()
        if self.errors:
            message = "{0}\nerrors:\n\t{1}".format(message, "\n\t".join(str(error) for error in self.errors))
        return message

    def oneline(self):
        """Get back the error as a oneliner"""
        desc = self.desc
        message = self.message

        info = ["{0}={1}".format(k, self.formatted_val(k, v)) for k, v in sorted(self.kwargs.items())]
        info = '\t'.join(info)
        if info and (message or desc):
            info = "\t{0}".format(info)

        if desc:
            if message:
                message = ". {0}".format(message)
            return '"{0}{1}"{2}'.format(desc, message, info)
        else:
            if message:
                return '"{0}"{1}'.format(message, info)
            else:
                return "{0}".format(info)

    def formatted_val(self, key, val):
        """Format a value for display in error message"""
        if not hasattr(val, "delfick_error_format"):
            return val
        else:
            try:
                return val.delfick_error_format(key)
            except Exception as error:
                return "<|Failed to format val for exception: val={0}, error={1}|>".format(val, error)

    def __eq__(self, error):
        """Say whether this error is like the other error"""
        return error.__class__ == self.__class__ and error.message == self.message and error.kwargs == self.kwargs

class ProgrammerError(Exception):
    """For when the programmer should have prevented something happening"""

class NotSpecified(object):
    """Used to tell the difference between None and Empty"""

class DelfickErrorTestMixin:
    @contextmanager
    def fuzzyAssertRaisesError(self, expected_kls, expected_msg_regex=NotSpecified, **values):
        """
        Assert that something raises a particular type of error.

        The error raised must be a subclass of the expected_kls
        Have a message that matches the specified regex.

        And have atleast the values specified in it's kwargs.
        """
        try:
            yield
        except Exception as error:
            try:
                assert issubclass(error.__class__, expected_kls), "Expected {0}, got {1}".format(expected_kls, error.__class__)
                if expected_msg_regex is not NotSpecified:
                    self.assertRegexpMatches(expected_msg_regex, error.message)

                if issubclass(error.__class__, DelfickError):
                    errors = values.get("_errors")
                    if "_errors" in values:
                        del values["_errors"]

                    self.assertDictContainsSubset(values, error.kwargs)
                    if errors:
                        self.assertEqual(sorted(error.errors), sorted(errors))
            except AssertionError:
                exc_info = sys.exc_info()
                try:
                    print("!" * 20)
                    print("Got error: {0}".format(error))
                    msg = "Expected: {0}".format(expected_kls)
                    if expected_msg_regex is not NotSpecified:
                        msg = "{0}: {1}".format(msg, expected_msg_regex)
                    if values:
                        msg = "{0}: {1}".format(msg, values)
                    print(msg)
                    print("!" * 20)
                finally:
                    raise exc_info[0], exc_info[1], exc_info[2]
        else:
            assert False, "Expected an exception to be raised\n\texpected_kls: {0}\n\texpected_msg_regex: {1}\n\thave_atleast: {2}".format(
                expected_kls, expected_msg_regex, values
            )

