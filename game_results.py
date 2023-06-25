import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.pymast.pymasttask import label
from sbs_utils.pymast.pymastcomms import receive
import random


class GameResults:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_destroy(self.update_score)

        self.game_stats = {
            "tsn_destroyed": 0,
            "raider_destroyed": 0,
            "kralien_ships_destroyed": 0,
            "skaraan_ships_destroyed": 0,
            "arvonian_ships_destroyed": 0,
            "torgoth_ships_destroyed": 0,
            "start_time": 0
        }


    @label()
    def update_score(self):
        obj = query.to_object(self.task.DESTROYED_ID)
        if obj is not None:
            side = "{obj.side.lower()}_destroyed"
            count = self.game_stats.get(side, 0)
            self.game_stats[side] = count + 1

            race = obj.art_id
            under = race.find("_")
            if under>=0:
                race = race[0:under]
                race = "{race.lower()}_ships_destroyed"
                count = self.game_stats.get(race, 0)
                self.game_stats[race] = count + 1


    # ========== show_game_results ===============
    @label()
    def show_game_results(self):
        sbs.pause_sim()
        
        self.gui_section("area: 10, 10, 99, 90;")
        self.gui_text("color:white;justify: center; font: gui-6;text:Game results")
        self.gui_row()
        self.gui_text(f"color:cyan;justify:center;font:gui-5;text:{self.start_text}")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("color:yellow; text:TSN Destroyed")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["tsn_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("""color:yellow; text:Raider Destroyed""")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["raider_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("""color:yellow; text:arvonian ships destroyed""")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["arvonian_ships_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("""color:yellow; text:kralien ships destroyed""")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["kralien_ships_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("""color:yellow; text:skaraan ships destroyed""")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["skaraan_ships_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_text("""color:yellow; text:torgoth ships destroyed""")
        self.gui_text(f"""color:yellow;justify: right; text:{self.game_stats["torgoth_ships_destroyed"]}""")
        self.gui_row()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        self.gui_hole()
        end_time = int((self.task.sim.time_tick_counter - self.game_stats["start_time"]) / 30  /60)
        self.gui_text("""color:yellow; right; text:Game Time""")
        self.gui_text(f"""color:yellow;justify: right; text:{end_time} minutes""")

        if self.task.page.client_id == 0:
            yield self.await_gui({
                "play again": self.start
            })
        else:
            yield self.await_gui()

