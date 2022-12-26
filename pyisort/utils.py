import json
import pathlib
import subprocess
from concurrent.futures import ThreadPoolExecutor

import sublime

from .constants import (
    DEFAULT_ENCODING,
    PACKAGE_NAME,
    PREFERENCE_FILE_NAME,
    SETTINGS_FILE_NAME,
    UNDEFINED_ENCODING,
)
from .logger import get_logger
from .options import SETTING_OPTIONS_COMMANDS_MAPPING
from .typing import Any, Dict, List, Tuple, Union

logger = get_logger()


def get_preference_settings() -> sublime.Settings:
    settings = sublime.load_settings(PREFERENCE_FILE_NAME)
    return settings


def get_package_settings() -> sublime.Settings:
    settings = sublime.load_settings(SETTINGS_FILE_NAME)
    logger.debug("Get sublime package settings")
    return settings


def get_project_settings(view: sublime.View) -> Dict[str, Any]:
    window = view.window()
    if not window:
        return {}

    settings = (window.project_data() or {}).get("settings", {}).get(PACKAGE_NAME, {})
    logger.debug(
        "Get sublime project settings: {settings}".format(settings=json.dumps(settings))
    )
    return settings


def load_settings(view: sublime.View) -> Dict[str, Any]:
    package_settings = get_package_settings()
    project_settings = get_project_settings(view)
    settings = {
        k: package_settings.get(k) for k in project_settings if package_settings.has(k)
    }
    settings.update(project_settings)
    logger.debug(
        "Load sublime settings finally: {settings}".format(
            settings=json.dumps(settings)
        )
    )
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
        return pathlib.Path(isort_bin).as_posix()


def is_python_syntax(view: sublime.View) -> bool:
    return False if view.settings().get("syntax").lower().find("python") == -1 else True


def get_encoding(view: sublime.View) -> str:
    encoding = view.encoding()
    logger.debug("View encoding: {encoding}".format(encoding=encoding))
    if encoding == UNDEFINED_ENCODING:
        encoding = get_preference_settings().get("default_encoding", "")
        logger.debug("Preferences encoding: {encoding}".format(encoding=encoding))

    return encoding


def get_options(view: sublime.View):
    settings = load_settings(view)
    options = []
    for name, value in settings.get("options", {}).items():
        option = SETTING_OPTIONS_COMMANDS_MAPPING[name]
        if option and value:
            if isinstance(value, bool):
                options.extend([option])
            elif isinstance(value, list):
                for v in value:
                    options.extend([option, v])
            elif isinstance(value, str):
                options.extend([option, value])

    return options
