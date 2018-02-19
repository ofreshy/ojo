
class OjoError(Exception):
    """
    Base error class
    """

    def __init__(self, message, job=None):
        """

        :param message:
        :param job: should not be None, but is for pickling purposes, see here
            https://stackoverflow.com/questions/16244923/how-to-make-a-custom-exception-class-with-multiple-init-args-pickleable
        """
        super(OjoError, self).__init__(message)
        self.job = job


class JobStageError(OjoError):
    """
    When the job stage when passed to service is not as expected
    """
    @property
    def stage(self):
        return self.job.stage


class IllegalStateError(OjoError):
    """
    When the state after service work does not make sense
    """


class UnderlyingExceptionError(OjoError):
    """
    When another exception was thrown, so service could not complete its work
    """
    def __init__(self, message, job=None, underlying_exception=None):
        """

        :param message:
        :param job: should never be None, allowed for pickling
        :param underlying_exception: should never be None, allowed for pickling
        """
        super(UnderlyingExceptionError, self).__init__(message, job)
        self.underlying_exception = underlying_exception
