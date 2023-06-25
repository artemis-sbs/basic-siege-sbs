import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label


intel_list=[
"The captain is very proud of their beautiful ship.",
"The captain is vain and proud of their handsome face.",
"The captain is spiritual a devout to the Kralien religion.",
"The captain is fashion conscous and proud of their attractive uniform.",
"The captain loves the Arvonian royal family.",
"The captain has unfailing faith in the decisions of the Arvonian Supreme Understander.",
"The captain loves their mother and is proud that she is so beautiful.",
"The captain and their spouse have a very stable, loving relationship.",
"The captain is meticulous and proud of their impeccable hygiene.",
"The captain is proud to command the fastest ship in the galaxy.",
"The captain is financially savvy and particularly proud of their investment portfolio.",
"The captain is very status conscous and believe they are a very important person.",
"The captain cannot be taunted.",
]


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
        yield self.end()

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
        taunt_trait=query.get_inventory_value(self.task.SCIENCE_SELECTED_ID, "taunt_trait")
        if taunt_trait is None:
            taunt_intel = intel_list[-1] 
        else:
            side_index=0
            if query.has_role(self.task.SCIENCE_SELECTED_ID, "kralien"):
                side_index=0
            elif query.has_role(self.task.SCIENCE_SELECTED_ID, "arvonian"):
                side_index=1
            elif query.has_role(self.task.SCIENCE_SELECTED_ID, "torgoth"):
                side_index=2
            elif query.has_role(self.task.SCIENCE_SELECTED_ID, "skaraan"):
                side_index=3
            taunt_index=side_index*3+taunt_trait
            taunt_intel = intel_list[taunt_index]

        def scan_default(self, event):
            return "Looks like some bad dudes"

        def scan_intel(self, event):
            return f"{taunt_intel}"
        
        def scan_bio(self, event):
            return "Whew can smell travel through space?"

        yield self.await_science({
            "scan": scan_default,
            "bio": scan_bio,
            "itl": scan_intel,
        })        

    