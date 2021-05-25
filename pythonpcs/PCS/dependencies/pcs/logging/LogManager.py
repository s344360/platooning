from typing import List
import json
import os
from pathlib import Path


from PCS.dependencies.pcs.logging.target.LogTarget import LogTarget
from PCS.dependencies.pcs.logging.target.ConsoleLogTarget import ConsoleLogTarget
from PCS.dependencies.pcs.logging.LogLevel import LogLevel


"""Avoid circular dependencies. First the LogTargets then the Logger (which uses them in the log method)"""


log_targets: List[LogTarget] = []
initialised: bool = False


class Logger:

    def __init__(self, logging_class: str):
        self.logging_class = logging_class

    def debug(self, vehicle_id: int, message: str, args: List[str] = None):
        self.log(LogLevel.DEBUG, vehicle_id, message, args)

    def info(self, vehicle_id: int, message: str, args: List[str] = None):
        self.log(LogLevel.INFO, vehicle_id, message, args)

    def warn(self, vehicle_id: int, message: str, args: List[str] = None):
        self.log(LogLevel.WARN, vehicle_id, message, args)

    def error(self, vehicle_id: int, message: str, args: List[str] = None):
        self.log(LogLevel.ERROR, vehicle_id, message, args)

    def log(self, level: LogLevel, vehicle_id: int, message: str, args: List[str] = None):
        if args is None:
            args = {""}
        for a in args:
            message = message.replace('{}', a, 1)
        for t in log_targets:
            t.store_log_entry(level, self.logging_class, vehicle_id, message)


loggers: List[Logger] = []


def get_logger(logging_class: str) -> Logger:
    if not initialised:
        init()
    for l in loggers:
        if l.logging_class == logging_class:
            return l
    logger: Logger = Logger(logging_class)
    loggers.append(logger)
    return logger


def init():
    global initialised
    initialised = True

    # load log targets
    # go back until pythonpcs in file directory
    cwd = Path.cwd()
    while str(cwd.name) != 'pythonpcs':
        cwd = cwd.parent
    # load config.json into a dictionary
    path_to_config = cwd / 'Logging/logging.json'
    if not os.path.exists(path_to_config):
        print("logging.json not found - no log targets initialized")
        return
    config = json.loads(open(path_to_config).read())
    for c in config:
        if c["type"] == "console":
            levels: List[LogLevel] = []
            for l in c["levels"]:
                levels.append(LogLevel[l])
            log_targets.append(ConsoleLogTarget(levels))
    print("initialized " + str(len(log_targets)) + " log targets")


# test area
"""
init()
print(log_targets[0].levels)
"""
