import os
import json

from src.plugins import refereeing_matches

TEMP_MEMORY = {}

def goal_time_checker(stadium_id):
    global TEMP_MEMORY

    secondary_temp_memory = json.loads(os.environ["memory"])

    if TEMP_MEMORY == {} or TEMP_MEMORY["picture"]["id"] != secondary_temp_memory["picture"]["id"]:
        TEMP_MEMORY = secondary_temp_memory

    else:
        if secondary_temp_memory["picture"]["max_time"] == 0:
            # Send the next picture
            refereeing_matches.goal_detector(stadium_id=stadium_id)

        else:
            secondary_temp_memory["picture"]["max_time"] -= 1
            os.environ["memory"] = json.dumps(secondary_temp_memory)