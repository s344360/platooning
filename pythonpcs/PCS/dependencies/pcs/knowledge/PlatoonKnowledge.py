from typing import List


from PCS.dependencies.pcs.model.Platoon import Platoon
from PCS.dependencies.pcs.knowledge.exception.NoSuchPlatoonException import NoSuchPlatoonException
from PCS.dependencies.pcs.knowledge.exception.PlatoonException import PlatoonException


# knowledge that holds platoon data, should only be accessed via a DataService
class PlatoonKnowledge:

    def __init__(self):
        self.platoons: dict = {}

    def get_platoon(self, platoon_id: int) -> Platoon:
        if platoon_id in self.platoons:
            return self.platoons[platoon_id]
        else:
            raise NoSuchPlatoonException(str(platoon_id))

    def get_platoons(self) -> List[Platoon]:
        return list(self.platoons.values())

    def save_platoon(self, platoon: Platoon):
        if platoon.platoon_id <= 0:     # | platoon.platoon_id in self.platoons:
            # do not accept platoons without a positive unique ID
            raise PlatoonException("illegal platoon id")
        else:
            self.platoons[platoon.platoon_id] = platoon
            """
            debugging:
            p_string = ""
            for p in platoon.vehicles:
                p_string += " - " + str(p)
            print(p_string)
            """

    def delete_platoon(self, platoon: Platoon):
        try:
            del self.platoons[platoon.platoon_id]
        except KeyError:
            print("Key not found")
