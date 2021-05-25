import abc


from PCS.dependencies.pcs.logging.LogLevel import LogLevel


class LogTarget(abc.ABC):

    @abc.abstractmethod
    def store_log_entry(self, level: LogLevel, logging_class: str, vehicle_id: int, message: str):
        pass
