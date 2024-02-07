import requests
import json
# import brotli
# import gzip

# from io import BytesIO
from datetime import datetime
from common import is_valid_json, extract_domain
from constants import CURRENT_PATH

def process(school):
  success = False
  
  for url in school['url_athletics']:
    req_api = requests.get(f"{url}/api/v2/Sports")
    if req_api and req_api.text and is_valid_json(req_api.text):
      sports = json.loads(req_api.text)
      if sports:
        for sport in sports:
          if sport and sport["shortName"] == "baseball" and sport["scheduleId"]:
            domain = extract_domain(url)
            schedule_url = f"https://admin.{domain}/services/schedule_txt.ashx?schedule={sport['scheduleId']}"
            headers = {'Content-Type': 'text/plain; charset=utf-8', 'User-Agent': 'PostmanRuntime/7.33.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
            response = requests.get(schedule_url, headers=headers)

            if response.status_code == 200:
              # note: some responses are encoded using Brotli compression 
              # response.headers.get("Content-Encoding") == "br"
              # but since installing brotli via pip3 it automatically gets
              # used by the requests module to decodes the response correctly
              
              if response and response.text:
                schedule = _parse_html_schedule(response.text)

                if schedule != None:
                  file_name = f"{CURRENT_PATH}/schedules/{school['id']}.json"
                  with open(file_name, 'w') as file:
                    json.dump(schedule, file)

                  school["processor"] = "beta"
                  success = True
                  break
            else:
              print(f"Error getting content with status code: {response.status_code}")
    if success:
      break
    
  return success

def _parse_html_schedule(text):
  schedule_data = None

  try:
    if text:
      # Split the schedule text into lines
      schedule_lines = text.strip().split('\n\r')

      # Extract column headers from the first line with extra spaces
      header_line = schedule_lines[10]

      # Initialize an empty list to store column names
      columns = []

      # Use a loop to find the start indices of each column name
      start = 0
      for col_name in header_line.split():
        # Find the starting index of the current column name
        start_idx = header_line.find(col_name)

        # Find the end index of the current column (start index of the next column or end of line)
        end_idx = header_line.find(
          header_line.split()[header_line.split().index(col_name) + 1],
          start
        ) - 1 if header_line.split().index(col_name) + 1 < len(header_line.split()) else len(header_line) - 1

        # Add the column name (including spaces) and indices to the list
        columns.append((col_name, start_idx, end_idx))

        # Update the start index for the next iteration
        start = end_idx + 2  # Adding 2 to skip the space

      # Print column names and start/end indices (for debugging purposes)
      # for name, start_idx, end_idx in columns:
      #   print(f"Column: {name}, Start: {start_idx}, End: {end_idx}")

      # Initialize an empty list to store schedule data
      schedule_data = []

      # Parse the remaining lines starting from index 9
      for line in schedule_lines[11:]:
        # Initialize an empty dictionary for the current line
        schedule_entry = {}

        # Iterate over the columns
        for col_name, start_idx, end_idx in columns:
          # Extract the substring for the current column and strip any leading/trailing whitespaces
          column_value = line[start_idx:end_idx].strip()

          # Add the extracted value to the dictionary
          schedule_entry[col_name] = column_value

        # Append the dictionary to the schedule data list
        schedule_data.append(schedule_entry)

      # Clean the structured schedule data
      for event in schedule_data:
        clean_event(event)
        
    else:
      print("No text found")
  except Exception as e:
    print(f"An unexpected error occurred parsing html schedule: {e}")
  
  return schedule_data

def clean_event(event):
  if "Date" in event:
    event["date"] = event.pop("Date")
    d = event["date"]
    d = d.replace(" (Mon)", ", 2024")
    d = d.replace(" (Tue)", ", 2024")
    d = d.replace(" (Wed)", ", 2024")
    d = d.replace(" (Thu)", ", 2024")
    d = d.replace(" (Fri)", ", 2024")
    d = d.replace(" (Sat)", ", 2024")
    d = d.replace(" (Sun)", ", 2024")

    t = event["Time"]
    t = t.replace("TBA", "12:00 am")
    t = t.replace("TBD", "12:00 am")
    t = t.replace("Noon", "12:00 pm")
    t = t.replace("noon", "12:00 pm")
    t = t.replace(".", "")
    if ":" not in t:
      t = t.replace(" ", ":00 ")

    parsed_datetime = datetime.strptime(f"{d} {t}", "%b %d, %Y %I:%M %p")
    event["date"] = parsed_datetime.strftime("%Y-%m-%dT%H:%M:%S")

  if "At" in event:
    event["at_home"] = event.pop("At")
    event["at_home"] = True if event["at_home"] == "Home" else False
  if "Opponent" in event:
    event["opponent"] = event.pop("Opponent")
  if "Location" in event:
    event["location"] = event.pop("Location")

  if "Tournament" in event:
    del event["Tournament"]
  if "Result" in event:
    del event["Result"]
  if "Time" in event:
    del event["Time"]
