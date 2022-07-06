import os
import time
import json

from src.plugins import refereeing_matches
from src.sql.models import MatchModel

MAX_TIME = 30
TEMP_MEMORY = {}

def goal_time_checker(stadium_id, match: MatchModel):
    
    time.sleep(1)
    secondary_temp_memory = json.loads(os.environ["memory"])

    if TEMP_MEMORY == {} or TEMP_MEMORY["picture"]["id"] != secondary_temp_memory["picture"]["id"] :
        TEMP_MEMORY = secondary_temp_memory

    else:
        if MAX_TIME == 0:
            # Set things about the nex picture
            next_image_number = TEMP_MEMORY["picture"]["number"] + 1
            next_image_type = match.match_images[ TEMP_MEMORY["picture"]["number"] + 1 ].image_type

            # Send the next picture
            sent_pic = refereeing_matches.send_image_match(match, stadium_id, next_image_number)

            # Save the picture in memory
            TEMP_MEMORY["picture"] = {
                "id": sent_pic.message_id,
                "type": match.match_images[next_image_number].image_type,
                "name": match.match_images[next_image_number].image_name,
                "number": next_image_number
            }

            os.environ["memory"] = json.dumps(TEMP_MEMORY)

            # Set max time for the next picture
            MAX_TIME = 30 if next_image_type == "speed" else 45 if next_image_type == "info" else 60

        else:
            MAX_TIME -= 1