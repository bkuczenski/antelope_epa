class NotConfiguredError(Exception):
    pass


class MissingEpaForegroundEnvVar(Exception):
    """
    User must export EPA_FOREGROUND=/path/to/foreground/data
    """
    pass


class DuplicateSubAssembly(Exception):
    """
    used when a sheet contains the same assembly repeated
    """
    pass
