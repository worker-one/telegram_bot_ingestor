import re
import json


def extract_json(message):
    try:
        return eval(message)
    except:
        # Regular expression pattern to extract JSON block
        pattern = r'```\s*(\{.*?\})\s*```'

        # Find the JSON block in the message
        match = re.search(pattern, message, re.DOTALL)

        if match:
          json_block = match.group(1)
          try:
              # Parse the JSON block to a dictionary
              json_data = json.loads(json_block)
              return json_data
          except json.JSONDecodeError as e:
              print("Failed to decode JSON:", e)
        else:
            raise ValueError("No JSON block found in the message.")


def extract_json_list(message):
    try:
        return eval(message)
    except:
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