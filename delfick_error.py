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

