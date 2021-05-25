from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon


class FesasBeaconCheckoutReq(FesasBeacon):
    def __init__(self):
        FesasBeacon.__init__(self)
