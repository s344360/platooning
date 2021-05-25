from PCS.dependencies.pcs.knowledge.exception.VehicleException import VehicleException


class NoSuchVehicleException(VehicleException):
    pass


# test area

"""
try:
    raise NoSuchVehicleException("hi hi")
except Exception as e:
    print("sg" + repr(e))
"""
