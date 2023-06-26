import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label
from sbs_utils import fs

class ScienceRouter:
    def __init__(self):
        super().__init__()
        self.route_science_select(self.handle_science)

    @label()
    def handle_science(self):
        if query.has_roles(self.task.SCIENCE_SELECTED_ID, "tsn, Station"):
            yield self.jump(self.station_science)
        elif query.has_roles(self.task.SCIENCE_SELECTED_ID, "tsn, friendly"):
            yield self.jump(self.friendly_science)
        elif query.has_role(self.task.SCIENCE_SELECTED_ID, "raider"):
            yield self.jump(self.raider_science)
        yield self.task.end()

    @label()
    def station_science(self):
        def scan_default(self, event):
            return "This is a friendly station"

        def scan_intel(self, event):
            return "The people seem smart enough"
        
        def scan_bio(self, event):
            return "Just a bunch of people"

        yield self.await_science({
            "scan": scan_default,
            "bio": scan_bio,
            "itl": scan_intel,
        })        

    @label()
    def friendly_science(self):
        def scan_default(self, event):
            return "This is a friendly ship"

        def scan_intel(self, event):
            return "The people seem eager for fight"
        
        def scan_bio(self, event):
            return "People looking to help"

        yield self.await_science({
            "scan": scan_default,
            "bio": scan_bio,
            "itl": scan_intel,
        })        

    @label()
    def raider_science(self):
        bio_intel = "The bio scan has failed."
        taunt_intel = "The captain cannot be taunted."
        taunt_trait=query.get_inventory_value(self.task.SCIENCE_SELECTED_ID, "taunt_trait")
        if taunt_trait is not None and self.taunt_data is not None:
            races = ["kralien", "arvonian", "torgoth", "skaraan", "ximni"]
            race = None
            for test in races:
                if query.has_role(self.task.SCIENCE_SELECTED_ID, test):
                    race = test
                    bio_intel = f"The crew is made up of {race}."
                    break

            intel_list = self.taunt_data.get(race, None)
            if intel_list is not None:
                taunt_intel = intel_list[taunt_trait]['science']


        def scan_default(self, event):
            return "Enemy vessel. Exercise caution."

        def scan_intel(self, event):
            t = taunt_intel
            return t
        
        def scan_bio(self, event):
            b = bio_intel
            return b

        yield self.await_science({
            "scan": scan_default,
            "bio": scan_bio,
            "itl": scan_intel,
        })        
