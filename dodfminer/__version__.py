version_info = (1, 3, 12)
# format:
# ('dodf_major', 'dodf_minor', 'dodf_patch')


def get_version():
    "Returns the version as a human-format string."
    return f'{version_info[0]}.{version_info[1]}.{version_info[2]}rc2'


__version__ = get_version()
