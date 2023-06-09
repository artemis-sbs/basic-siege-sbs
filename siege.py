import sbs
from sbs_utils.objects import PlayerShip, Npc, Terrain
import random
import sbs_utils.faces as faces
import sbs_utils.names as names
import sbs_utils.query as query
import sbs_utils.scatter as scatter
import sbs_utils.names as names
from sbs_utils.pymast.pymasttask import label
from sbs_utils.gridobject import GridObject

#######################################################################################################
#######################################################################################################
#######################################################################################################

@label()
def  build_world(self):
    sim = self.sim
    #
    # Self here is the story
    #
    ## Create the player ship
    ## Returns a spawn_data so you have easy access to all data to set values
    # class SpawnData:
    # 	id: int
    # 	engine_object: any
    # 	blob: any
    # 	py_object: EngineObject
    first = True
    colors  = ["yellow", "green", "blue"]
    c = 0
    #do print(f"{player_count}")
    for player_ship_data in self.player_list:
        if c>= self.player_count:
            # make sure the id is cleared dry docked ships
            player_ship_data.id = None
            continue

        player_ship = query.to_id(PlayerShip().spawn(self.task.sim, *player_ship_data.spawn_point, player_ship_data.name, player_ship_data.side, player_ship_data.ship))
        c+=1
        player_ship_data.id = player_ship

        faces.set_face(player_ship, player_ship_data.face)
        if first:
            sbs.assign_client_to_ship(0,player_ship)
            first = False
        points = query.get_open_grid_points(sim,player_ship)
        
        for i in range(3):
            if len(points)>0:
                point = random.choice(points)
                points.remove(point)
                GridObject().spawn(self.task.sim, player_ship, f"DC{i+1}", f"DC{i+1}", point[0],point[1], 80, colors[i], "damcons")


    ########################
    ## Enable comms and science scanning
    #ConsoleDispatcher.add_select(player_ship.id, 'comms_target_UID', player_comms_selected)
    #ConsoleDispatcher.add_message(player_ship.id, 'comms_target_UID', player_comms_message)
    # for station in query.role("Station"):
    #     comms = ExampleComms()
    #     comms.enable(player_ship.id, station)

    
    stations = 1
    spawn_points = scatter.sphere(random.randint(1,3), 0,0,0, 2500, 6500, ring=True)
    for station in spawn_points:
        ds = Npc().spawn(sim, station.x, station.y, station.z,f"DS{stations}", "tsn", "starbase_command", "behav_station")
        stations +=1
        ds.py_object.add_role("Station")
        # Mark this as a station that does builing
        ds.py_object.add_role("station_builder")
        faces.set_face(ds.id, faces.random_terran(civilian=True))
        
        # Protect stations with mines
        start_angle = random.randrange(0, 180)
        very_start = start_angle
        for wedge in range(random.randint(0,3)):
            angle = random.randrange(30,80)
            end_angle = start_angle + angle
            cluster_spawn_points = scatter.ring(random.randint(3,5),random.randint(3,5), station.x, station.y, station.z, 3500, 2500, start_angle, end_angle)
            # Random type, but same for cluster
            a_type = "danger_1a"
            for v2 in cluster_spawn_points:
                #keep value between -500 and 500??
                if v2.y != 0:
                    v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
                Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_mine")
            start_angle += angle + random.randrange(10, 50)
            if start_angle>= very_start+360:
                break



    enemyTypeNameList = []
    enemyTypeNameList.extend(names.torgoth_ship_keys())
    enemyTypeNameList.extend(names.kralien_ship_keys())
    enemyTypeNameList.extend(names.skaraan_ship_keys())
    enemyTypeNameList.extend(names.arvonian_ship_keys())
    enemyTypeNameList.extend(names.ximni_ship_keys())
    enemy_prefix = "KLMNQ"

    enemy = 0
    enemy_count = self.enemy_count
    if enemy_count <1:
        enemy_count = 1

    spawn_points = scatter.sphere(int(enemy_count), 0,0,0, 8000, 8000+250*enemy_count, ring=True)
    
    
    for v in spawn_points:
        r_type = random.choice(enemyTypeNameList)
        race = r_type.split("_")
        race = race[0]
        if race=="xim":
            race = "ximni"
    
        roles = f"{race}, raider"
        r_name = f"{random.choice(enemy_prefix)}_{enemy}"
        spawn_data = Npc().spawn(self.task.sim, v.x, v.y, v.z, r_name, roles, r_type, "behav_npcship")
        raider = spawn_data.py_object
        # add a taunt trait
        query.set_inventory_value(raider.id, "taunt_trait", random.randint(0,2))
        #
        # Should add a commnon funtion to call to get the face based on race
        #
        faces.set_face(raider.id, faces.random_face(race))
        enemy = enemy + 1
        
    
    ####################
    # MAP TERRAIN	
    # make a few random clusters of nebula

    # make a few random clusters of nebula
    spawn_points = scatter.sphere(random.randint(2,7), 0,0,0, 5000, 20000, ring=True)
    for v in spawn_points:
        cluster_spawn_points = scatter.sphere(random.randint(10,20), v.x, 0,v.z, 100, 2000, ring=True)
        for v2 in cluster_spawn_points:
            Terrain().spawn(self.sim, v2.x, v2.y, v2.z,None, None, "nebula", "behav_nebula")


    # make a few random clusters of Asteroids
    spawn_points = scatter.sphere(random.randint(4,7), 0,0,0, 2000, 9000, ring=True)
    asteroid_types = names.plain_asteroid_keys()
    for v in spawn_points:
        cluster_spawn_points = scatter.line(random.randint(20,50),  v.x, 0,v.z-800,   v.x, 0,v.z+800,   random=True)
    #    scatter_sphere(random.randint(10,20), v.x, 0,v.z, 100, 1000, ring=False)
        for v2 in cluster_spawn_points:
            #keep value between -500 and 500??
            #v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
            a_type = random.choice(asteroid_types)
            #a_type = "asteroid_crystal_blue"
            Terrain().spawn(self.sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_asteroid")

    # I want candy
    spawn_points = scatter.sphere(random.randint(5,12), 0,0,0, 1000, 4000, ring=True)
    for v in spawn_points:
        startAngle = random.randrange(0,359)
        endAngle = startAngle + random.randrange(10,20)
        depth = random.randrange(2,5)
        width = random.randrange(10,20)
        inner = random.randrange(2000,9000)
        cluster_spawn_points = scatter.ring(width, depth, 0, 0,0, inner + 500, inner, startAngle, endAngle)
        # Random type, but same for cluster
        a_type = f"danger_{1}{'a'}"
        for v2 in cluster_spawn_points:
            #keep value between -500 and 500??
    #                v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
            Terrain().spawn(self.sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_mine")
            Terrain().spawn(self.sim, v2.x, v2.y + 1000, v2.z,None, None, a_type, "behav_mine")
            Terrain().spawn(self.sim, v2.x, v2.y - 1000, v2.z,None, None, a_type, "behav_mine")
