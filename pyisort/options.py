from collections import defaultdict


SETTINGS_OPTIONS_MAPPING = defaultdict(
    str,
    {
        "line_length": "--line-length",
        "profile": "--profile",
        "float_to_top": "--float-to-top",
        "future": "--future",
        "thirdparty": "--thirdparty",
        "project": "--project",
        "known_local_folder": "--known-local-folder",
    },
)