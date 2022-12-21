# pyisort
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python [isort](https://github.com/PyCQA/isort) formatter for Sublime Text.

## Installation

- Install `pyisort` from Package Control.
- Restart Sublime.

## Configuration

Here are some ways to configure the package.

1. From Preferences > Package Settings > Pyisort > Settings.
2. From the command palette: `Preferences: Pyisort Settings`.
3. Project-specific configuration. From the command palette run `Project: Edit` to open your Project and add your settings in:

```json
{
    "settings": {
        "pyisort": {
            "isort_bin": "isort",
            "isort_on_save": true,
            "options": {
                "line_length": "88",
                "profile": "black",
                "float_to_top": true
            }
        }
    }
}
```

All pyisort `options` will overwrite the configuration which isort looks for the closest supported [config file](https://pycqa.github.io/isort/docs/configuration/config_files.html), and the option keys and isort commands mapping defines  in [options.py](./pyisort/options.py).

If you want to respect the config file, please do not edit the `options` and keep that as original settings.
