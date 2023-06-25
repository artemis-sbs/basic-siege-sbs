# start of my python script program file
import sbslibs
import sbs
import sbs_utils.faces as faces
from sbs_utils.handlerhooks import *
from sbs_utils.gui import Gui
import sbs_utils.query as query
from sbs_utils.pymast.pymaststory import PyMastStory
from sbs_utils.pymast.pymaststorypage import PyMastStoryPage
from sbs_utils.pymast.pymasttask import label
from sbs_utils.mast.mast import MastDataObject
from station_tasks import task_station_building
from comms import CommsRouter
from basic_ai import SpawnRouter
from science import ScienceRouter
import siege
from consoles import ClientGui
from extra_gui import ExtraGui
from map_common import MapCommon
from grid_ai import GridAi
from internal_damage import InternalDamage
from game_results import GameResults
#enemies_to_make = 5
origin_station_id = 0

# Uses mixin for modular design
class SiegeStory(PyMastStory, ClientGui, CommsRouter, 
                SpawnRouter, ScienceRouter, ExtraGui, 
                MapCommon, GridAi, 
                InternalDamage, GameResults
                ):
    def __init__(self):
        super().__init__()

        self.start_text = "Mission: Basic Siege written in PyMast"
        self.enemy_count = 5
        self.player_count = 1
        self.game_started = False
        self.player_list = [
            MastDataObject({"name": "Artemis", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point": (200,0,0) , "face": faces.random_terran()}),
            MastDataObject({"name": "Intrepid", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point": (300,0, -100), "face": faces.random_terran()}),
            MastDataObject({"name": "Aegis", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser" , "spawn_point": (500,0, -200), "face": faces.random_terran()}),
            MastDataObject({"name": "Horatio", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser" , "spawn_point": (700,0, -300), "face": faces.random_terran()}),
            MastDataObject({"name": "Excalibur", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point": (-200,0,0) , "face": faces.random_terran()}),
            MastDataObject({"name": "Hera", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point":  (-300,0,-100), "face": faces.random_terran()}),
            MastDataObject({"name": "Ceres", "id": None, "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point": (-500,0, -200) , "face": faces.random_terran()}),
            MastDataObject({"name": "Diana", "id": None , "side": "tsn", "ship": "tsn_battle_cruiser", "spawn_point": (-700,0, -300), "face": faces.random_terran()}),
        ]

        self.route_science_select(self.handle_science)
        #self.route_destroy(self.update_score)

    @label()
    def start_server(self):
        self.gui_section("area: 5, 10, 50, 90;")
        self.gui_text(f"""{self.start_text}""")

        self.gui_section("area: 50, 10, 95,90;row-height:75px;padding:0px,10px")
        self.gui_text(""" justify:right;text:Difficulty """)
        difficulty = self.gui_slider(self.enemy_count, "low: 1.0;high:11.0")
        self.gui_row()
        self.gui_blank()
        self.gui_row()
        self.gui_text(""" justify:right;text:Player ships """)
        player_count = self.gui_slider(self.player_count,"low: 1.0;high:8.0")
        self.gui_row()
        self.gui_blank()
        self.gui_row()
        self.gui_text(""" justify:right;text:Mission Type""")
        world_select = self.gui_drop_down("text: Mission type;list:siege,single front,double front,deep strike,peacetime,border war,infestation")
        self.gui_row()
        self.gui_text("""justify:right;text:Terrain""")
        terrain_select = self.gui_drop_down("text: Terrain;list:None, Few,Some, lots, many")
        self.gui_row()
        self.gui_text("""justify:right;text:Friendly Ships""")
        friendly_select = self.gui_drop_down("text: Friendly Ships;list:None, Few,Some, lots, many")
        self.gui_row()
        self.gui_text("""justify:right;text:Anomalies""")
        anom_select = self.gui_drop_down("text: Anomalies;list:None, Few,Some, lots, many")

        self.world_select = "siege"
        self.friendly_select = "none"
        self.terrain_select = "none"
        self.anom_select = "none"
        def on_message(__,event ):
            if event.sub_tag==difficulty.tag:
                self.enemy_count = int(difficulty.value+0.4)
                difficulty.value = self.enemy_count
                return True
            elif event.sub_tag==player_count.tag:
                self.player_count = int(player_count.value+0.4)
                player_count.value = self.player_count
                return True
            elif event.sub_tag==friendly_select.tag:
                self.friendly_select = friendly_select.value.lower()
                return True
            elif event.sub_tag==world_select.tag:
                self.world_select = world_select.value.lower()
                return True
            elif event.sub_tag==terrain_select.tag:
                self.terrain_select = terrain_select.value.lower()
                return True
            elif event.sub_tag==anom_select.tag:
                self.anom_select = anom_select.value.lower()
                return True
            return False
        self.reroute_gui_clients(self.start_client)
        yield self.await_gui({
            "justify: center; text:Start Mission": self.start
        }, on_message=on_message)

        #self.reroute_gui_clients(self.game_started_client)

    @label()
    def pause_screen(self):
        #
        # Shown if the simulation is paused
        #

        self.gui_section("area: 5, 10, 50, 90;")
        self.gui_text("""Simulation paused""")

        @label()
        def resume():
            sbs.resume_sim()
            yield self.jump(self.pause_screen)

        yield self.await_gui({
            "Resume Mission": resume
        })

        
            

    @label()
    def start(self):
        sbs.create_new_sim()
        siege.build_world(self)
        self.spawn_friendly_npc()
        sbs.resume_sim()
        self.game_started = True

        self.game_stats["start_time"] = self.task.sim.time_tick_counter
                
        # Example story functions define inside the story
        self.schedule_task(self.task_end_game)
        # Example story functions define outside the story
        self.schedule_task(task_station_building)
        #
        # Note that this tasks end, the end game logic 
        # will reroute to a new task.
        #
        yield self.jump(self.pause_screen)

    @label()
    def task_end_game(self):
        #print(self.__class__)
        #-------------------------------------------------------------------------------
        if len(query.role("Raider")) <= 0:
            # no enemy ships left in list!
            self.start_text = "You have won!^All enemies have been destroyed."
            sbs.pause_sim()
            yield self.reroute_gui_all(self.show_game_results)
            return

        #-------------------------------------------------------------------------------
        if len(query.role("__PLAYER__")) <= 0:
            self.start_text = "All your base are belong to us. All PLayer ships have been lost!"
            sbs.pause_sim()
            yield self.reroute_gui_all(self.show_game_results)
            return
        
        yield self.delay(5, use_sim=True)
        yield self.jump(self.task_end_game)

    
class StoryPage(PyMastStoryPage):
    story = SiegeStory()

Gui.server_start_page_class(StoryPage)
Gui.client_start_page_class(StoryPage)

