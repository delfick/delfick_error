from setuptools import setup

setup(
      name = "delfick_error"
    , version = "1.8"
    , py_modules = ['delfick_error', 'delfick_error_pytest']

    , install_requires =
      [ 'total-ordering'
      , 'six'
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.4.9"
        , "nose"
        , "mock"
        ]
      }

    , entry_points =
      { "pytest11": ["delfick_error_pytest = delfick_error_pytest"]
      }

    # metadata for upload to PyPI
    , url = "http://github.com/delfick/delfick_error"
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Customized Exception class"
    , license = "MIT"
    , keywords = "exception"
    )
