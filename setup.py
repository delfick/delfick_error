from setuptools import setup

setup(
      name = "delfick_error"
    , version = "1.1"
    , py_modules = ['delfick_error']

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.4.9"
        , "nose"
        , "mock"
        ]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/delfick_error"
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Customized Exception class"
    , license = "MIT"
    , keywords = "exception"
    )
