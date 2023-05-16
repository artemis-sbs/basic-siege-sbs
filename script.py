# start of my python script program file


import sbslibs
import sbs
import random
import sbs_utils.faces as faces
import sbs_utils.scatter as scatter
import sbs_utils.names as names
from sbs_utils.handlerhooks import *
from sbs_utils.gui import Gui
from sbs_utils.pages.start import ClientSelectPage, StartPage
from sbs_utils.objects import PlayerShip, Npc, Terrain
import sbs_utils.query as query
from sbs_utils.pymast.pymaststory import PyMastStory
from sbs_utils.pymast.pymaststorypage import PyMastStoryPage
from sbs_utils.pymast.pollresults import PollResults
from sbs_utils.pymast.pymasttask import label
from docking_tasks import task_player_docking
from station_tasks import task_station_building



#enemies_to_make = 5
origin_station_id = 0

class SiegeStory(PyMastStory):
    def __init__(self):
        super().__init__()
        self.start_text = "Mission: Basic Siege written in PyMast"
        self.enemy_count = 5
        self.player_count = 0

    @label()
    def start_server(self):
        self.gui_section("area: 0, 10, 99, 90;")
        self.gui_text(self.start_text)
        self.gui_section("area: 60, 75, 99, 89;row-height: 30px")
        slider = self.gui_slider(self.enemy_count, f"low:0; high: 20;show_number:True", None)
        self.gui_row()
        text = self.gui_text(f"Enemy count: {self.enemy_count}")
        
        def on_message(__,event ):
            if event.sub_tag==slider.tag:
                self.enemy_count = int(slider.value+0.4)
                text.value = f"Enemy count: {self.enemy_count}"
                slider.value = self.enemy_count
                return True
            return False

        yield self.await_gui({
            "Start Mission": self.start
        }, on_message=on_message)

    @label()      
    def client_change(self, sim, event):
        if event.sub_tag=="change_console":
            yield self.jump(self.start_client)

    @label()
    def start_client(self):
        # Have change_console route here
        #
        # Events are not workign properly
        #
        self.watch_event("client_change", self.client_change)
        players = []
        pick_player = None
        for player in query.to_object_list(query.role("__PLAYER__")):
            players.append(player.name)
        if self.player_count != players:
            if len(players):
                player = players[0]
                players = ",".join(players)
                self.gui_section("area: 25, 65, 39, 90;row-height: 45px;")
                pick_player = self.gui_radio(players, player, True)

        self.gui_section("area: 75, 65, 99, 90;")
        console = self.gui_radio("Helm, Weapons, Comms, Engineering, Science", "Helm", True)

        def console_selected():
            pass

        yield self.await_gui({
            "Accept": console_selected
        })

        if pick_player is None:
            yield self.jump(self.start_client)
        player_name = pick_player.value
        console_sel = console.value.lower()
        # Keep running the console
        while True:
            self.assign_player_ship(player_name)
            self.gui_console(console_sel)

            yield self.await_gui()
            
            

    @label()
    def start(self):
        print("Start")

        sbs.create_new_sim()
        self.build_world()
        sbs.resume_sim()
                
        # Example story functions define inside the story
        self.schedule_task(self.task_end_game)
        self.schedule_task(self.task_npc_targeting)
        self.schedule_task(self.task_science_scan)
        self.schedule_task(self.task_comms)
        # Example story functions define outside the story
        self.schedule_task(task_station_building)
        self.schedule_task(task_player_docking)

    @label()
    def task_end_game(self):
        #print(self.__class__)
        #-------------------------------------------------------------------------------
        if len(query.role("Raider")) <= 0:
            # no enemy ships left in list!
            self.start_text = "You have won!^All enemies have been destroyed."
            sbs.pause_sim()
            yield self.jump(self.start_server)
            return

        #-------------------------------------------------------------------------------
        if len(query.role("__PLAYER__")) <= 0:
            self.start_text = "All your base are belong to us. All PLayer ships have been lost!"
            sbs.pause_sim()
            yield self.jump(self.start_server)
            return

        
        yield self.delay(5)
        yield self.jump(self.task_end_game)

    @label()
    def task_science_scan(self):
        #task, player_id, npc_id_or_filter, scans ) -> None:
        players = query.role('__PLAYER__')
        for player in players:
            self.schedule_science(player, None, {
                "scan": self.scan_default,
                "bio": self.scan_bio,
                "intel": self.scan_intel,
                "signl": self.scan_signl
            })

    def scan_default(self, event):
        return "This space object is now scanned, in the most general way. This text was generated by the script."
    
    def scan_intel(self, event):
        return "This space object is detailed in the ship's computer banks. This text was generated by the script."
    
    def scan_bio(self, event):
        return "This space object has indeterminate life signs. This text was generated by the script."
    def scan_signl(self, event):
        return "This space object radiating signals. This text was generated by the script."

    @label()
    def task_comms(self):
        #task, player_id, npc_id_or_filter, scans ) -> None:
        players = query.role('__PLAYER__')
        for player in players:
            self.schedule_comms(player, lambda id: query.has_role(id, "Station"), {
                "Hail": self.comms_station_hail,
                "Build Homing": self.comms_build_homing,
                "Build Nuke": self.comms_build_nuke,
                "Build EMP": self.comms_build_emp,
                "Build Mine": self.comms_build_mine,
            })

            self.schedule_comms(player, lambda id: query.has_role(id, "Raider"), {
                "Hail": self.comms_raider_hail,
                "Taunt": ("red", self.comms_raider_taunt),
                "Surrender": ("yellow", self.comms_raider_surrender),
            })

    @label()
    def comms_station_hail(self, comms):
        player = comms.get_player()
        other = comms.get_other()
        torpedo_type_text_name = [ "HOMING",	"NUKE",	"EMP",	"MINE" ]
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
        text_line = "Hello, " + player.comms_id + ".  We stand ready to assist.^"
        text_line += "You have full docking priviledges.^"
        text_line += "   {} Homing ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.HOMING))
        text_line += "   {} Nuclear ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.NUKE))
        text_line += "   {} EMP ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.EMP))
        text_line += "   {} Mine ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.MINE))

        torp_type = blob2.get("torpedo_build_type",0)
        if torp_type is None:
            text_line += "We have nothing in production^"
        else:
            text_line += "{} in production^".format(torpedo_type_text_name[torp_type])

        comms.have_other_tell_player(text_line)
    
    def comms_build_homing(self, comms):
        player = comms.get_player()
        other = comms.get_other()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on homing production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.HOMING)
        comms.have_other_tell_player(text_line)

    def comms_build_nuke(self, comms):
        player = comms.get_player()
        other = comms.get_other()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on nuke production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.NUKE)
        comms.have_other_tell_player(text_line)

    def comms_build_emp(self, comms):
        player = comms.get_player()
        other = comms.get_other()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on EMP production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.EMP)
        comms.have_other_tell_player(text_line)

    def comms_build_mine(self, comms):
        player = comms.get_player()
        other = comms.get_other()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on mine production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.MINE)
        comms.have_other_tell_player(text_line)


    def comms_raider_hail(self, comms):
        comms.have_other_tell_player("We will destroy you, disgusting Terran scum!")

    def comms_raider_taunt(self, comms):
        player = comms.get_player()
        if player is None:
            return
        text_line = f"You are a foolish Terran, { player.comms_id}.  We know that the taunt functionality is not currently implemented.^"
        comms.have_other_tell_player(text_line)

    def comms_raider_surrender(self, comms):
        comms.have_other_tell_player("We will never surrender, disgusting Terran scum!")

    @label()
    def task_npc_targeting(self):
        raiders = query.role('Raider')
        if len(raiders)==0:
            return

        for raider in raiders:
            the_target = query.closest(raider, query.role("__PLAYER__"), 2000)
            if the_target is None:
                the_target = query.closest(raider, query.role("Station"))
            if the_target is not None:
                query.target(self.sim, raider, the_target, True)

        yield self.delay(5)
        yield self.jump(self.task_npc_targeting)


    #######################################################################################################
    #######################################################################################################
    #######################################################################################################
    @label()
    def  build_world(self):
        sim = self.sim
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



        
       
        enemyTypeNameList = ["kralien_dreadnaught","kralien_battleship","skaraan_defiler","cargo_ship","arvonian_carrier","torgoth_behemoth"]
        enemy_prefix = "KLMNQ"

        enemy = 0
        enemy_count = self.enemy_count
        if enemy_count <1:
            enemy_count = 1

        spawn_points = scatter.sphere(int(enemy_count), 0,0,0, 8000, 8000+250*enemy_count, ring=True)
        
        
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
        
        ####################
        # MAP TERRAIN	
        # make a few random clusters of nebula
        spawn_points = scatter.sphere(random.randint(3,7), 0,0,0, 1000, 8500, ring=True)
        for v in spawn_points:
            v_end = v.rand_offset(3500, 5000)
            cluster_spawn_points = scatter.line(random.randint(4,12), v.x, 0,v.z, v_end.x, 0, v_end.z)
            for v2 in cluster_spawn_points:
                # Move it around about 150 
                v2 = v2.rand_offset(550)
                # Keep y reasonable
                if v2.y != 0:
                    v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
                Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, "nebula", "behav_nebula")

        # make a few random clusters of Asteroids
        spawn_points = scatter.sphere(random.randint(4,10), 0,0,0, 2500, 8000, ring=True)
        asteroid_types = names.plain_asteroid_keys()
        print(f"Plain {len(asteroid_types)}")
        for v in spawn_points:
            # Get another point relative to this one
            # between 500 and 2000 away
            v_end = v.rand_offset(2500, 5000)
            cluster_spawn_points = scatter.line(random.randint(5,15), v.x, 0,v.z, v_end.x, 0, v_end.z)
            for v2 in cluster_spawn_points:
                # Move it around about 150 
                v2 = v2.rand_offset(350)
                # Keep y reasonable
                if v2.y != 0:
                    v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
                a_type = random.choice(asteroid_types)
                Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_asteroid")

        # I want candy
        spawn_points = scatter.sphere(random.randint(2,7), 0,0,0, 6000, 10000, ring=True)
        for v in spawn_points:
            for v in spawn_points:
                cluster_spawn_points = scatter.rect_fill(random.randrange(3,5), random.randrange(3,5), v.x, 0,v.z, random.randrange(2000,3000), random.randrange(2000,3000), True)
                # Random type, but same for cluster
                a_type = "danger_2b"
                for v2 in cluster_spawn_points:
                    #keep value between -500 and 500??
                    if v2.y!=0:
                        v2.y = abs(v2.y) % 500 * (v2.y/abs(v2.y))
                    Terrain().spawn(sim, v2.x, v2.y, v2.z,None, None, a_type, "behav_mine")


class StoryPage(PyMastStoryPage):
    story = SiegeStory()

Gui.server_start_page_class(StoryPage)
Gui.client_start_page_class(StoryPage)

