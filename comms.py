import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label
from sbs_utils import faces
from sbs_utils import fs


class CommsRouter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_comms_select(self.handle_comms)
        self.taunt_data = fs.load_json_data(fs.get_mission_dir_filename("taunts.json"))

    @label()
    def handle_comms(self):
        #=========== route_comms  ========
        # start the comms for the players and stations
        # Each ship will have its of thread for comms
        # this enables them to have a unique path
        
        if self.task.COMMS_SELECTED_ID == self.task.COMMS_ORIGIN_ID:
            # This is the same ship
            yield self.jump(self.internal_comms)
        elif query.has_roles(self.task.COMMS_SELECTED_ID, "tsn, friendly"):
            yield self.jump(self.friendly_comms)
        elif query.has_roles(self.task.COMMS_SELECTED_ID, "tsn, Station"):
            self.task.torpedo_build_type = sbs.TORPEDO.HOMING
            yield self.jump(self.station_comms)
        elif query.has_role(self.task.COMMS_SELECTED_ID, "Raider"):
            yield self.jump(self.npc_comms)

#================ internal_comms ==================
    @label()
    def internal_comms(self):
        #
        # Setup faces for the departments
        #
        self.task.doctor = faces.random_terran()
        self.task.biologist = faces.random_terran()
        self.task.counselor = faces.random_terran()
        self.task.major = faces.random_terran()
        yield self.jump(self.internal_comms_loop)

    # ================ internal_comms_loop ==================
    @label()
    def internal_comms_loop(self):
        def button_sickbay(story, comms):
            comms.receive("The crew health is great!", face=story.task.doctor, color="blue", title="sickbay")
        def button_security(story, comms):
            comms.receive("All secure", face=story.task.major, color="red", title="security")
        def button_exobiology(story, comms):
            comms.receive("Testing running, one moment", face=story.task.biologist, color="green", title="exobiology")
        def button_counselor(story, comms):
            comms.receive("Something is disturbing the crew", face=story.task.counselor, color="cyan", title="counselor")
            yield story.task.delay(seconds=2, use_sim=True)
            comms.receive("Things feel like they are getting worse", face=story.task.counselor, color="cyan", title="counselor")
        
        yield self.await_comms({
            "sickbay": button_sickbay,
            "security": button_security,
            "exobiology": button_exobiology,
            "counselor": button_counselor,
        })
        # loop
        yield self.jump(self.internal_comms_loop)

        # -> internal_comms_loop

    @label()
    def station_comms(self):
        #task, player_id, npc_id_or_filter, scans ) -> None:
        print("STart station comms")
        yield self.await_comms({
            "Hail": self.comms_station_hail,
            "Build Homing": self.comms_build_homing,
            "Build Nuke": self.comms_build_nuke,
            "Build EMP": self.comms_build_emp,
            "Build Mine": self.comms_build_mine,
        })
        yield self.jump(self.station_comms)

    @label()
    def npc_comms(self):
        yield self.await_comms({
            "Hail": self.comms_raider_hail,
            "Taunt": ("red", self.comms_taunts),
            "Surrender": ("yellow", self.comms_raider_surrender),
        })
        yield self.jump(self.npc_comms)

    @label()
    def comms_station_hail(self, comms):
        player = comms.get_origin()
        other = comms.get_selected()
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

        comms.receive(text_line)
    
    def comms_build_homing(self, comms):
        player = comms.get_origin()
        other = comms.get_selected()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on homing production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.HOMING)
        comms.receive(text_line)

    def comms_build_nuke(self, comms):
        player = comms.get_origin()
        other = comms.get_selected()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on nuke production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.NUKE)
        comms.receive(text_line)

    def comms_build_emp(self, comms):
        player = comms.get_origin()
        other = comms.get_selected()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on EMP production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.EMP)
        comms.receive(text_line)

    def comms_build_mine(self, comms):
        player = comms.get_origin()
        other = comms.get_selected()
        if player is None or other is None:
            return
        blob2 = other.get_engine_data_set(self.sim)
    
        text_line = f"We read you, {player.comms_id}.  We will focus on mine production.^"
        blob2.set("torpedo_build_type",sbs.TORPEDO.MINE)
        comms.receive(text_line)


    def comms_raider_hail(self, comms):
        comms.receive("We will destroy you, disgusting Terran scum!")

    def comms_raider_surrender(self, comms):
        comms.receive("We will never surrender, disgusting Terran scum!")

    #================ friendly_comms ==================
    @label()
    def friendly_comms(self):
        comms_client_id = self.task.EVENT.client_id
        def give_orders(story, comms):
            story.reroute_gui_client(comms_client_id, story.friendly_give_orders)

        yield self.await_comms({
            "Give Orders": give_orders
        })
            

        yield self.jump(self.friendly_comms)

    @label()
    def comms_taunts(self, comms):
        #
        # Skip if the loading of taunts failed
        #
        if self.taunt_data is None:
            self.task.end()

        races = ["kralien", "arvonian", "torgoth", "skaraan", "ximni"]
        race = None
        for test in races:
            if query.has_role(self.task.COMMS_SELECTED_ID, test):
                race = test
                break
            
        if race is None:
            # No Taunt for you
            yield self.jump(self.npc_comms)
        #
        # Present taunts
        #
        name = query.to_object(self.task.COMMS_ORIGIN_ID).name
        taunt_trait=query.get_inventory_value(self.task.COMMS_SELECTED_ID, "taunt_trait")
        enrage_value=0

        def taunt_button(self, comms, data):
            # Need to format the data
            msg = data['transmit']
            msg = msg.format(name=name)
            comms.transmit(msg)
            # failure
            if taunt_trait!=0:
                msg = data['failure']
                msg = msg.format(name=name)
                comms.receive(msg)
            # success
            else:
                msg = data['success']
                msg = msg.format(name=name)
                comms.receive(msg)
                enrage_value=self.task.sim.time_tick_counter+30*120
                query.set_inventory_value(self.task.COMMS_SELECTED_ID, "enrage_value",(enrage_value, self.task.COMMS_ORIGIN_ID))

        buttons = {}
        for data in self.taunt_data[race]:
            buttons[data['button']] =  lambda s,c: taunt_button(s,c,data)


        yield self.await_comms(
            buttons
        )
        yield self.jump(self.npc_comms)
        