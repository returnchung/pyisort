import sublime
import sublime_plugin

from .pyisort.utils import get_isort_bin, is_python_syntax, load_settings, proc_cmd


class PyisortCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("pyisort command")
        if not is_python_syntax(self.view):
            sublime.status_message("pyisort: The current file syntax is not support")
            return

        filename = self.view.file_name() or ""
        settings = load_settings(self.view)
        isort_bin = get_isort_bin(self.view)
        if not isort_bin:
            sublime.status_message("Unable to find isort bin.")

        cmd = [
            isort_bin,
            filename,
            "--profile",
            "black",
        ]
        if settings.get("isort_on_save") is not True:
            cmd.append("--stdout")
            stdout, stderr = proc_cmd(cmd)
            region = sublime.Region(0, self.view.size())
            self.view.replace(edit, region, stdout)
        else:
            proc_cmd(cmd)


class PyisortOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view: sublime.View):
        settings = load_settings(view)
        window = view.window()
        if window and settings.get("isort_on_save") is True:
            view.run_command("pyisort")
