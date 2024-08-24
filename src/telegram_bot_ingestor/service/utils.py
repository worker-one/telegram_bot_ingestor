import re
import json
from fix_busted_json import repair_json


def extract_json_from_text(message):

    if "```" in message:
        # Use a regular expression to find the JSON block within backticks
        json_block = re.search(r'```(.*?)```', message, re.DOTALL)

        if json_block:
            json_str = json_block.group(1).strip()  # Extract and clean the JSON string

            try:
                # Parse the extracted JSON string into a Python object
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError:
                print("Error: Extracted content is not valid JSON.")
                return None
        else:
            print("Error: No JSON block found in the message.")
            return None

    else:
        try:
            return eval(message)
        except:
            try:
                message = repair_json(message)
            except:
                print("Error: No JSON block found in the message.")
                return None