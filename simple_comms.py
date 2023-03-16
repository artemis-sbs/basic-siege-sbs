# start of my python script program file
import sbslibs
import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.spaceobject import SpaceObject


def player_comms_selected(sim, player_id, event):
        # This function checks for things that a player might select, such as a science target or weapons target.
    # It could also check for things that Comms has selected, but to keep things simple the Comms code has been taken out.
    selected = sim.get_space_object(event.selected_id)
    my_ship  = sim.get_space_object(event.origin_id)
    if selected is None or my_ship is None:
        return
    other_ship = sim.get_space_object(event.selected_id)
    blob = other_ship.data_set
    other_name = blob.get("name_tag",0)
    if None != other_name:
        # always give the comms player a hail button; that works on everything with a name
        face_text = faces.get_face(event.selected_id)
        sbs.send_comms_selection_info(event.origin_id, face_text, "white", blob.get("name_tag",0))
        sbs.send_comms_button_info(event.origin_id, "white", "Hail", "hail_tag")

    if query.has_role(event.selected_id, "Station"):
        to_station_comms_selected(sim, player_id, event)
    elif query.has_role(event.selected_id, "Raider"):
        to_raider_comms_selected(sim, player_id, event)
    # elif query.has_role(event.selected_id, "__PLAYER__"):
    #     to_player_comms_selected(sim, player_id, event)

def to_player_comms_message(sim, message, player_id, event):
    comms_ship_so = SpaceObject.get(event.origin_id)
    obj_selected_so = SpaceObject.get(event.selected_id)

    target_name = obj_selected_so.comms_id
    face_desc = faces.get_face(obj_selected_so.id)

    if "hail_tag" == message:
        sbs.send_comms_message_to_player_ship(comms_ship_so.id, obj_selected_so.id, "gray", face_desc, target_name, 
            "Yes, we are " + target_name + ", a player ship.")



def player_comms_message(sim, message, player_id, event):
    comms_ship_so = SpaceObject.get(event.origin_id)
    obj_selected_so = SpaceObject.get(event.selected_id)

    if comms_ship_so is None:
        # Remove handlers
        return
    
    if obj_selected_so is None:
        return
    
    if obj_selected_so.has_role("Station"):
        to_station_comms_message(sim, message, player_id, event)
    elif obj_selected_so.has_role("Raider"):
        to_raider_comms_message(sim, message, player_id, event)
    if obj_selected_so.has_role("__PLAYER__"):
        to_player_comms_message(sim, message, player_id, event)

    
    

def to_station_comms_selected(sim, player_id, event):
    sbs.send_comms_button_info(event.origin_id, "white", "Build Homing", "torp_homing_tag");
    sbs.send_comms_button_info(event.origin_id, "white", "Build Nuke", "torp_nuke_tag");
    sbs.send_comms_button_info(event.origin_id, "white", "Build Emp", "torp_emp_tag");
    sbs.send_comms_button_info(event.origin_id, "white", "Build Mine", "torp_mine_tag");

def to_station_comms_message(sim, button_tag, player_id, event):
    comms_ship_so = SpaceObject.get(event.origin_id)
    obj_selected_so = SpaceObject.get(event.selected_id)
    
    torpedo_type_text_name = [ "HOMING",	"NUKE",	"EMP",	"MINE" ]
    comms_ship_id = event.origin_id
    obj_selected_id = event.selected_id
    blob2 = obj_selected_so.get_engine_data_set(sim)
    comms_name = comms_ship_so.comms_id
    target_name = obj_selected_so.comms_id

    face_desc = faces.get_face(obj_selected_id)

    match button_tag: 
        case "hail_tag":
            text_line = "Hello, " + comms_name + ".  We stand ready to assist.^"
            text_line += "You have full docking priviledges.^"

            text_line += "   {} Homing ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.HOMING))
            text_line += "   {} Nuclear ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.NUKE))
            text_line += "   {} EMP ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.EMP))
            text_line += "   {} Mine ready^".format(blob2.get("torpedo_count", sbs.TORPEDO.MINE))

            text_line += "{} in production^".format(torpedo_type_text_name[blob2.get("torpedo_build_type",0)])

            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, 
                target_name,  text_line)
        case "torp_homing_tag":
            text_line = "We read you, " + comms_name + ".  We will focus on homing production.^"
            blob2.set("torpedo_build_type",sbs.TORPEDO.HOMING)
            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, target_name, text_line)
        case "torp_nuke_tag":
            text_line = "We read you, " + comms_name + ".  We will focus on nuclear torp production.^"
            blob2.set("torpedo_build_type",sbs.TORPEDO.NUKE)
            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, target_name, text_line)
        case "torp_emp_tag":
            text_line = "We read you, " + comms_name + ".  We will focus on EMP production.^"
            blob2.set("torpedo_build_type",sbs.TORPEDO.EMP)
            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, target_name, text_line)
        case "torp_mine_tag":
            text_line = "We read you, " + comms_name + ".  We will focus on mine production.^"
            blob2.set("torpedo_build_type",sbs.TORPEDO.MINE)
            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, target_name, text_line)
        case "docking_tag":
            text_line = "We read you, " + comms_name + ".  We're standing by for expedited docking.^"
            sbs.send_comms_message_to_player_ship(comms_ship_id, obj_selected_id, "gray", face_desc, target_name, text_line)


def to_raider_comms_selected(sim, player_id, event):
    sbs.send_comms_button_info(event.origin_id, "white", "You're Ugly", "taunt_tag")
    sbs.send_comms_button_info(event.origin_id, "white", "Surrender now", "surrender_tag")


def to_raider_comms_message(sim, button_tag, player_id, event):
    comms_ship_so = SpaceObject.get(event.origin_id)
    obj_selected_so = SpaceObject.get(event.selected_id)

    face_desc = faces.get_face(obj_selected_so.id)

    match button_tag:
        case "taunt_tag":
            text_line = "You are a foolish Terran, " + comms_ship_so.comms_id + ".  We know that the taunt functionality is not currently implemented.^"
            sbs.send_comms_message_to_player_ship(comms_ship_so.id, obj_selected_so.id, "gray", face_desc, obj_selected_so.comms_id, text_line)
        case "hail_tag":
            sbs.send_comms_message_to_player_ship(comms_ship_so.id, obj_selected_so.id, "gray", face_desc, obj_selected_so.comms_id, 
                "We will destroy you, disgusting Terran scum!")







