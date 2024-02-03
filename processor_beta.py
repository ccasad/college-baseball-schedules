import requests
import json

from common import is_valid_json


def process(school):
  success = False
  
  req_api = requests.get(f"https://{school['url_athletics']}/api/v2/Sports")
  if req_api and req_api.text and is_valid_json(req_api.text):
    sports = json.loads(req_api.text)
    if sports:
      for sport in sports:
        if sport and sport["shortName"] == "baseball" and sport["scheduleId"]:
          url = f"https://admin.{school['url_athletics']}/services/schedule_txt.ashx?schedule={sport['scheduleId']}"
          headers = {'Content-Type': 'text/html', 'User-Agent': 'PostmanRuntime/7.33.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
          req_schedule = requests.get(url, headers=headers)
          if req_schedule and req_schedule.text:
            # _parse_html_schedule(req_schedule.text)
            school["processor"] = "beta"
            success = True
          break

  return success

def _parse_html_schedule(text):
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

    # Print the structured schedule data
    for entry in schedule_data:
      print(entry)
  else:
    print("No text found")

