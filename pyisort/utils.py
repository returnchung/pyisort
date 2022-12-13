import pathlib
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

import sublime

from .constants import PACKAGE_NAME, SETTINGS_FILE_NAME
from .logger import get_logger

logger = get_logger()


def get_package_settings() -> sublime.Settings:
    settings = sublime.load_settings(SETTINGS_FILE_NAME)
    logger.debug("sublime package settings: %s", settings.to_dict())
    return settings


def get_project_settings(view: sublime.View) -> Dict[str, Any]:
    window = view.window()
    if not window:
        return {}

    project_settings: Dict[str, Dict[str, Any]] = (
        (window.project_data() or {}).get("settings", {}).get(PACKAGE_NAME, {})
    )
    logger.debug("sublime project settings: %s", project_settings)
    return project_settings


def load_settings(view: sublime.View) -> Dict[str, Any]:
    package_settings = get_package_settings()
    project_settings = get_project_settings(view)
    settings = {**package_settings.to_dict(), **project_settings}
    return settings


def proc_cmd_in_background(cmd, success_msg=None):
    def _callback(future):
        if future.exception() is not None:
            sublime.message_dialog(str(future.exception()))
        else:
            stdout, stderr = future.result()
            print(stdout.decode("UTF-8"))
            if success_msg:
                sublime.message_dialog(success_msg)

    def _process(cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=3)
        return stdout, stderr

    executor = ThreadPoolExecutor(max_workers=5)
    f = executor.submit(_process, cmd)
    f.add_done_callback(_callback)
    executor.shutdown(wait=False)


def proc_cmd(cmd: List[str]) -> Tuple[str, str]:
    def _process(cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=3)
        return stdout.decode("UTF-8"), stderr.decode("UTF-8")

    return _process(cmd)


def get_isort_bin(view: sublime.View) -> Optional[str]:
    settings = load_settings(view)
    isort_bin = settings.get("isort_bin")
    if isort_bin:
        return f"{pathlib.Path(isort_bin).absolute()}"


def is_python_syntax(view: sublime.View) -> bool:
    return False if view.settings().get("syntax").lower().find("python") == -1 else True
