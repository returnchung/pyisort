import pathlib

import sublime
import sublime_plugin

from .pyisort.logger import get_logger
from .pyisort.utils import (
    get_encoding,
    get_isort_bin,
    is_python_syntax,
    load_settings,
    proc_cmd,
)

logger = get_logger()


class PyisortCommand(sublime_plugin.TextCommand):
    def run(self, edit, auto_save=False):
        if not is_python_syntax(self.view):
            sublime.status_message("pyisort: The current file syntax is not support")
            return

        isort_bin = get_isort_bin(self.view)
        if not isort_bin:
            sublime.status_message("Unable to find isort bin.")
            return

        filename = self.view.file_name() or ""
        if not filename:
            sublime.status_message("Unable to find file to format.")
            return

        if auto_save:
            # Run isort format on current file in the background.
            cmd = [isort_bin, filename]
            proc_cmd(cmd)
        else:
            # Run isort format and replace current file content.
            encoding = get_encoding(self.view)
            if not encoding:
                sublime.status_message("Unable to detect this file encoding.")
                return

            cmd = [isort_bin, "-"]
            contents = self.view.substr(sublime.Region(0, self.view.size()))
            stdout, stderr = proc_cmd(
                cmd, cwd=pathlib.Path(filename).parent, input=contents.encode(encoding)
            )
            if stderr:
                err_msg = stderr.decode(encoding)
                logger.error(err_msg)
                sublime.status_message(err_msg)
                return

            region = sublime.Region(0, self.view.size())
            self.view.replace(edit, region, stdout.decode(encoding))


class PyisortOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view: sublime.View):
        settings = load_settings(view)
        window = view.window()
        if window and settings.get("isort_on_save", False):
            view.run_command("pyisort", {"auto_save": True})
