import sbslibs
import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.pymast import PollResults


########################################################################################################
#
########################################################################################################
def task_station_building(story):
    torpedo_type_name_list = ["Homing","Nuclear","EMP","Mine"]
    while True:
        delay_time = 5
        stations = query.role("station_builder")
        # Unschedule task if no more stations
        if len(stations) == 0:
            break
        #print("Station building")
        for station_id in stations:
            blob = query.get_engine_data_set(station_id, story.sim)
        
            station_name = blob.get("name_tag",0);

            # check and set timer for building the current torpedo
            torp_build_time = blob.get("torp_build_ready_time",0)
            if None == torp_build_time: # never built a torp before
                torp_build_time = story.sim.time_tick_counter + 30 * 10 # 10 seconds?
                blob.set("torp_build_ready_time",torp_build_time,0)

            if torp_build_time <= story.sim.time_tick_counter: # done building!
                torp_type = blob.get("torpedo_build_type",0)
                cur_count = blob.get("torpedo_count", torp_type)
                blob.set("torpedo_count", cur_count+1, torp_type)

                face_desc =faces.get_face(station_id)

                text_line = "We have produced another " + torpedo_type_name_list[torp_type] + " torpedo.  We will begin work on another."
                sbs.send_comms_message_to_player_ship(0, station_id, "green", face_desc, 
                    station_name,  text_line)

                torp_build_time = story.sim.time_tick_counter + 30 * 60 * 4 #-------------  4 minutes
                blob.set("torp_build_ready_time",torp_build_time,0)
        yield story.delay(delay_time)

