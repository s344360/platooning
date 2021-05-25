import traceback


import PCS.dependencies.pcs.logging.LogManager as l_m


logger: l_m.Logger = l_m.get_logger("test")

logger.debug(1, "1 {} 2", ["1", "2"])
