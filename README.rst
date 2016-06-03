Delfick Error
=============

This is an error class that I keep remaking in projects

.. image:: https://travis-ci.org/delfick/delfick_error.png?branch=master
    :target: https://travis-ci.org/delfick/delfick_error

Usage
-----

The point of this exception class is to be able to create an error class that
automatically combines keyword arguments given to the exception instance:

.. code-block:: python

    >>> from delfick_error import DelfickError
    >>> DelfickError()
    DelfickError('',)
    >>> str(DelfickError())
    ''
    >>> str(DelfickError("blah"))
    '"blah"'
    >>> str(DelfickError("blah", a=1, b=2))
    '"blah"\ta=1\tb=2'

You can also subclass DelfickError and override the description of the error:

.. code-block:: python

    >>> class AnError(DelfickError):
    ...  desc = "An error specific to something"
    ... 
    >>> AnError()
    AnError('',)
    >>> str(AnError("things"))
    '"An error specific to something. things"'
    >>> str(AnError("things", a=1, b=2))
    '"An error specific to something. things"\ta=1\tb=2'

You can also use it to display multiple errors:

.. code-block:: python

    >>> ex1 = ValueError("Bad value")
    >>> ex2 = IndexError("Bad index")
    >>> ex3 = Exception("blah")
    >>> str(AnError("found errors", _errors=[ex1, ex2, ex3]))
    '"An error specific to something. found errors"\nerrors:\n\tBad value\n\tBad index\n\tblah'
    >>> print str(AnError("found errors", _errors=[ex1, ex2, ex3]))
    "An error specific to something. found errors"
    errors:
            Bad value
            Bad index
            blah
    >>> 

Here, the ``_errors`` argument is interpreted using special logic to put each
item in it's list on a new line.

DelfickError also has a mechanism to allow you to control how the error is
formatted when converting the error to a string.

.. code-block:: python

    >>> class SomeObject(object):
    ...   def __init__(self, val):
    ...     self.val = val
    ...   def delfick_error_format(self, key):
    ...     return "{0}_formatted_{1}".format(self.val, key)
    ... 
    >>> obj = SomeObject(20)
    >>> str(DelfickError(a=1, b=obj))
    'a=1\tb=20_formatted_b'

Changelog
---------

1.7.2
    Making it possible for fuzzyAssertsError to match fake delfick_error classes

1.7
    Added default UserQuit exception

1.6
    Added six to install_requires

1.5
    Made DelfickError hashable

1.4
    Fixed an embarrassing bug

1.3
    Made DelfickError Orderable

    Added an assertIs shim to DelfickErrorTestMixin

1.2
    Tests work in python26, python27 and python34

1.1
    Now with tests!

    And DelfickErrorTestMixin for your testing pleasure

1.0
    Initial release

Installation
------------

Use pip!:

.. code-block:: bash

    pip install delfick_error

Or if you're developing it:

.. code-block:: bash

    pip install -e .
    pip install -e ".[tests]"

Tests
-----

To run the tests in this project, just use the helpful script:

.. code-block:: bash

    ./test.sh

Or run tox:

.. code-block:: bash

    tox

