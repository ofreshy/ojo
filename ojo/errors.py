
class OjoError(Exception):
    pass


class MoveError(Exception):
    pass


class RarError(OjoError):
    pass


# TODO add here job status
class JobStageError(OjoError):
    pass
