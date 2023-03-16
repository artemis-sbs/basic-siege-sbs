# start of my python script program file
import sbslibs
import sbs
import time
import math
import random
import sbs_utils.faces as faces
import sbs_utils.scatter as scatter
import sbs_utils.names as names
from sbs_utils.handlerhooks import *
from sbs_utils.gui import Gui
from sbs_utils.pages.start import ClientSelectPage, StartPage
from sbs_utils.objects import PlayerShip, Npc, Terrain
from sbs_utils.tickdispatcher import TickDispatcher
from sbs_utils.consoledispatcher import ConsoleDispatcher
import sbs_utils.query as query
from sbs_utils.engineobject import EngineObject
from docking_tasks import task_player_docking
from station_tasks import task_station_building
from simple_science import player_science_selected, player_science_message
from simple_comms import player_comms_selected, player_comms_message


enemies_to_make = 5
origin_station_id = 0

#######################################################################################################
#######################################################################################################
#######################################################################################################
def  handle_simulation_start(sim):
    ## Create the player ship
    ## Returns a spawn_data so you have easy access to all data to set values
    # class SpawnData:
    # 	id: int
    # 	engine_object: any
    # 	blob: any
    # 	py_object: EngineObject
    player_ship = PlayerShip().spawn(sim,1200,0,200, "Artemis", "tsn", "tsn_battle_cruiser")
    faces.set_face(player_ship.id, faces.random_terran())
    sbs.assign_client_to_ship(0, player_ship.id)
    # Mark this as a player that does basic docking
    player_ship.py_object.add_role("basic_docking")
    ########################
    ## Enable comms and science scanning
    ConsoleDispatcher.add_select(player_ship.id, 'comms_target_UID', player_comms_selected)
    ConsoleDispatcher.add_message(player_ship.id, 'comms_target_UID', player_comms_message)
    ConsoleDispatcher.add_select(player_ship.id, 'science_target_UID', player_science_selected)
    ConsoleDispatcher.add_message(player_ship.id, 'science_target_UID', player_science_message)

    
    stations = [(0,0,0, "Alpha"),(2400,0,100, "Beta")]
    for station in stations:
        ds = Npc().spawn(sim, *station, "tsn", "starbase_command", "behav_station")
        ds.py_object.add_role("Station")
        # Mark this as a station that does builing
        ds.py_object.add_role("station_builder")
        faces.set_face(ds.id, faces.random_terran(civilian=True))


    enemyTypeNameList = ["kralien_dreadnaught","kralien_battleship","skaraan_defiler","cargo_ship","arvonian_carrier","torgoth_behemoth"]
    enemy_prefix = "KLMNQ"

    enemy = 0
    spawn_points = scatter.sphere(int(enemies_to_make), 0,0,0, 6000, 6000+250*enemies_to_make, ring=True)

    for v in spawn_points:
        r_type = random.choice(enemyTypeNameList)
        r_name = f"{random.choice(enemy_prefix)}_{enemy}"
        spawn_data = Npc().spawn(sim, v.x, v.y, v.z, r_name, "RAIDER", r_type, "behav_npcship")
        raider = spawn_data.py_object
        faces.set_face(raider.id, faces.random_kralien())
        raider.add_role("Raider")
        enemy = enemy + 1
        # for player in to_object_list(role("__PLAYER__")):
        # 	do raider.start_task("NPC_Comms", {"player": player})
        # next player

    #####################################
    # TASK SCHEDULING
    # Schedule a task to handle station duties every 5s
    TickDispatcher.do_interval(sim, task_station_building, 5)
    # Schedule a task to handle player docking 5s
    TickDispatcher.do_interval(sim, task_player_docking, 5)
    # Schedule a task to handle NPC Targeting 5s
    TickDispatcher.do_interval(sim, task_npc_targeting, 5)
    # Schedule a task for checking end game state
    TickDispatcher.do_interval(sim, task_end_game, 5)
    
    
    ####################
    # MAP TERRAIN	

    # make a few random clusters of nebula
    spawn_points = scatter.sphere(random.randint(2,7), 0,0,0, 1000, 4000, ring=True)
    for v in spawn_points:
        cluster_spawn_points = scatter.sphere(random.randint(10,20), v.x, 0,v.z, 100, 1000, ring=True)
        for v2 in cluster_spawn_points:
            Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, "nebula", "behav_nebula")

    # make a few random clusters of Asteroids
    spawn_points = scatter.sphere(random.randint(10,20), 0,0,0, 1000, 4000, ring=True)
    asteroid_types = names.asteroid_keys()
    for v in spawn_points:
        cluster_spawn_points = scatter.sphere(random.randint(10,20), v.x, 0,v.z, 100, 1000, ring=False)
        for v2 in cluster_spawn_points:
            #keep value between -500 and 500??
            v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
            a_type = random.choice(asteroid_types)
            Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_asteroid")

    # I want candy
    spawn_points = scatter.sphere(random.randint(5,12), 0,0,0, 1000, 4000, ring=True)
    for v in spawn_points:
        cluster_spawn_points = scatter.sphere(random.randrange(10,20), v.x, 0,v.z, 100, 1000, ring=False)
        # Random type, but same for cluster
        a_type = f"danger_{random.randint(1,5)}{random.choice('abc')}"
        for v2 in cluster_spawn_points:
            #keep value between -500 and 500??
            v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
            Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_mine")


def task_npc_targeting(sim, task):
    for raider in query.role('Raider'):
        the_target = query.closest(raider, query.role("__PLAYER__"), 2000)
        if the_target is None:
            the_target = query.closest(raider, query.role("Station"))
        if the_target is not None:
            query.target(sim, raider, the_target, True)

def task_end_game(sim, _):
    #-------------------------------------------------------------------------------
    if len(query.role("Raider")) <= 0:
        # no enemy ships left in list!
        the_start_page.desc = "You have won!^All enemies have been destroyed."
        sbs.pause_sim()

    #-------------------------------------------------------------------------------
    if len(query.role("__PLAYER__")) <= 0:
        the_start_page.desc = "All your base are belong to us. All PLayer ships have been lost!"
        sbs.pause_sim()



# end of my python script program file
def start_mission(sim, _):
    sbs.create_new_sim()
    handle_simulation_start(sim)
    sbs.resume_sim()
# if "continue" == message_tag:
# 	sbs.resume_sim()

the_start_page = StartPage("Mission: Basic Siege.^^This is a simple mission script for testing purposes.", start_mission)
def start_page():
    return the_start_page


Gui.server_start_page_class(start_page)
Gui.client_start_page_class(ClientSelectPage)

