import pathlib

import sublime
import sublime_plugin

from .pyisort.logger import get_logger
from .pyisort.utils import (
    get_encoding,
    get_isort_bin,
    get_options,
    is_python_syntax,
    load_settings,
    proc_cmd,
)

logger = get_logger()


class PyisortCommand(sublime_plugin.TextCommand):
    def run(self, edit, auto_save=False):
        if not is_python_syntax(self.view):
            err_msg = "Pyisort: The current file syntax is not support"
            logger.error(err_msg)
            sublime.status_message(err_msg)
            return

        isort_bin = get_isort_bin(self.view)
        if not isort_bin:
            err_msg = "Pyisort: Unable to find isort binary."
            logger.error(err_msg)
            sublime.status_message(err_msg)
            return

        filename = self.view.file_name() or ""
        if not filename:
            err_msg = "Pyisort: Unable to find file to format."
            logger.error(err_msg)
            sublime.status_message(err_msg)
            return

        options = get_options(self.view)
        if auto_save:
            # Run isort format on current file in the background.
            cmd = [isort_bin, filename] + options
            proc_cmd(cmd)
        else:
            # Run isort format and replace current file content.
            encoding = get_encoding(self.view)
            if not encoding:
                err_msg = "Pyisort: Unable to detect this file encoding."
                logger.error(err_msg)
                sublime.status_message(err_msg)
                return

            cmd = [isort_bin, "-"] + options
            cwd = pathlib.Path(filename).parent.absolute().as_posix()
            contents = self.view.substr(sublime.Region(0, self.view.size()))
            stdout, stderr = proc_cmd(
                cmd, cwd=cwd, input=contents.encode(encoding)
            )
            if stderr:
                err_msg = stderr.decode(encoding)
                logger.error(err_msg)
                sublime.status_message("Pyisort: {err_msg}".format(err_msg=err_msg))
                return

            region = sublime.Region(0, self.view.size())
            self.view.replace(edit, region, stdout.decode(encoding))


class PyisortOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view: sublime.View):
        settings = load_settings(view)
        window = view.window()
        if window and settings.get("isort_on_save", False):
            view.run_command("pyisort", {"auto_save": True})
