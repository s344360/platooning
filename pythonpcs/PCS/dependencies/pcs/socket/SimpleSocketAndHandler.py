import zmq
import threading


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.logicElements.sensor.pcs import SensorLogic


class SimpleSocketAndHandler(threading.Thread):

    def __init__(self):
        super(SimpleSocketAndHandler, self).__init__()

    def run(self):
        logging_class: str = "MessageHandler"
        logger: LogManager.Logger = LogManager.get_logger(logging_class)


        # creates socket to hear on a tcp port
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5556")#5556
        logger.info(0, "start reading from new connection")
        try:
            while True:
                # Wait for Request
                message = socket.recv_json()

                # Do Work
                logger.debug(0, "received message from Plexe: {}", [str(message)])
                reply = SensorLogic.call_logic(message)
                # Send Reply
                socket.send_json(reply)
        finally:
            socket.close()
            context.term()
            logger.info(0, "connection to client closed")
