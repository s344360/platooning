import threading
from PCS.logicElements.sensor.pcs.SensorLogic import SensorLogic


class MessageHandler(threading.Thread):
    def __init__(self, sensor_logic: SensorLogic, message: str):
        super(MessageHandler, self).__init__()
        self.sensor_logic = sensor_logic
        self.message = message

    def run(self):
        try:
            # send data forward to Sensor Logic
            self.sensor_logic.call_logic(self.message)
        except IOError:
            print("Error in Message Handler")