import re
import json
from fix_busted_json import repair_json


def extract_json_from_text(text):
    print(text)
    try:
        return eval(text)
    except:
        if "```" in text:
            # Regular expression to match the JSON block inside the text
            json_blocks = re.findall(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_blocks:
                return json.loads(repair_json(json_blocks[0]))
            
            else:
                print("No JSON block found.")
                return None
        else:
            return None