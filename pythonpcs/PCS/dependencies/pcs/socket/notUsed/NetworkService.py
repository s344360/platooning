import threading
from PCS.dependencies.pcs.socket.notUsed.SocketPCSToPlexe import SocketPCSToPlexe
from PCS.logicElements.sensor.pcs.SensorLogic import SensorLogic
from PCS.dependencies.pcs.socket.notUsed.MessageHandler import MessageHandler


class NetworkService(threading.Thread):

    def __init__(self, sensor_logic: SensorLogic):
        super(NetworkService, self).__init__()
        self.sensor_logic = sensor_logic

    def run(self):
        try:
            while True:
                message = SocketPCSToPlexe.socket.recv()
                print("Received message from client:")
                print(message)
                print()
                message_handler = MessageHandler(self.sensor_logic, message)
                message_handler.start()
        except IOError:
            print("Network Service got interrupted")
