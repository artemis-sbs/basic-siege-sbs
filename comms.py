import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label

class CommsRouter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_comms_select(self.handle_comms)

    @label()
    def handle_comms(self):
        #=========== route_comms  ========
        # start the comms for the players and stations
        # Each ship will have its of thread for comms
        # this enables them to have a unique path
        if query.has_roles(self.task.COMMS_SELECTED_ID, "tsn, Station"):
            self.task.torpedo_build_type = sbs.TORPEDO.HOMING
            yield self.jump(self.station_comms)
        elif query.has_role(self.task.COMMS_SELECTED_ID, "Raider"):
            yield self.jump(self.npc_comms)

    @label()
    def station_comms(self):
        #task, player_id, npc_id_or_filter, scans ) -> None:
        self.await_comms({
            "Hail": self.comms_station_hail,
            "Build Homing": self.comms_build_homing,
            "Build Nuke": self.comms_build_nuke,
            "Build EMP": self.comms_build_emp,
            "Build Mine": self.comms_build_mine,
        })
        yield self.jump(self.station_comms)

    @label()
    def npc_comms(self):
        self.await_comms({
            "Hail": self.comms_raider_hail,
            "Taunt": ("red", self.comms_raider_taunt),
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

    def comms_raider_taunt(self, comms):
        player = comms.get_origin()
        
        if player is None:
            return
        text_line = f"You are a foolish Terran, { player.comms_id}.  We know that the taunt functionality is not currently implemented.^"
        comms.receive(text_line)

    def comms_raider_surrender(self, comms):
        comms.receive("We will never surrender, disgusting Terran scum!")