from typing import List

from PCS.dependencies.pcs.logging.LogLevel import LogLevel
from PCS.dependencies.pcs.logging.target.LogTarget import LogTarget


class ConsoleLogTarget(LogTarget):

    def __init__(self, levels: List[LogLevel]):
        self.levels: List[LogLevel] = levels

    def store_log_entry(self, level: LogLevel, logging_class: str, vehicle_id: int, message: str):
        if level not in self.levels:
            return

        log_entry: str = str(level.name) + " \t" + logging_class + " \t" + "vehicle " + str(vehicle_id) + \
                         " \t" + message

        print(log_entry)
