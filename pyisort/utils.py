import pathlib
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple, Union

import sublime

from .constants import (
    DEFAULT_ENCODING,
    PACKAGE_NAME,
    PREFERENCE_FILE_NAME,
    SETTINGS_FILE_NAME,
    UNDEFINED_ENCODING,
)
from .logger import get_logger

logger = get_logger()


def get_preference_settings() -> sublime.Settings:
    settings = sublime.load_settings(PREFERENCE_FILE_NAME)
    return settings


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


def proc_cmd_in_background(
    cmd, success_msg: Union[str, None] = None, encoding: str = DEFAULT_ENCODING
):
    def _callback(future):
        if future.exception() is not None:
            sublime.message_dialog(str(future.exception()))
        else:
            stdout, stderr = future.result()
            logger.debug(stdout.decode(encoding))
            if success_msg:
                sublime.message_dialog(success_msg)

    def _process(cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=10)
        return stdout, stderr

    executor = ThreadPoolExecutor(max_workers=5)
    f = executor.submit(_process, cmd)
    f.add_done_callback(_callback)
    executor.shutdown(wait=False)


def proc_cmd(
    cmd: List[str],
    cwd: Union[str, bytes, None] = None,
    input: Union[bytes, None] = None,
) -> Tuple[bytes, bytes]:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )
    stdout, stderr = proc.communicate(input=input, timeout=10)
    return stdout, stderr


def get_isort_bin(view: sublime.View) -> Union[str, None]:
    settings = load_settings(view)
    isort_bin = settings.get("isort_bin")
    if isort_bin:
        return f"{pathlib.Path(isort_bin)}"


def is_python_syntax(view: sublime.View) -> bool:
    return False if view.settings().get("syntax").lower().find("python") == -1 else True


def get_encoding(view: sublime.View) -> str:
    encoding = view.encoding()
    logger.debug(f"View encoding: {encoding}")
    if encoding == UNDEFINED_ENCODING:
        encoding = get_preference_settings().get("default_encoding", "")
        logger.debug(f"Preferences encoding: {encoding}")

    return encoding
