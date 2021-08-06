version_info = (1, 3, 5)
# format:
# ('dodf_major', 'dodf_minor', 'dodf_patch')


def get_version():
    "Returns the version as a human-format string."
    return '%d.%d.%d' % version_info


__version__ = get_version()
