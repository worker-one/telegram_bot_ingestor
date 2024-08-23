import re
import json
from fix_busted_json import repair_json

def extract_json_from_text(text):
    if "```" in text:
        regex = r"```({.*?})```"
        match = re.search(regex, text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                json_dict = json.loads(json_str)
                return json_dict
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
        else:
            print("No JSON block found in the text.")
            return None

    json_dict = repair_json(text)
    return json_dict
