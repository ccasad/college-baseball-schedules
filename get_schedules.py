import requests
import json
import gspread

from bs4 import BeautifulSoup
from urllib.parse import urlparse

current_path = "."

def _is_valid_json(json_str):
  try:
    json.loads(json_str)
    return True
  except json.JSONDecodeError:
    return False


def _extract_domain(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the domain from the hostname component
    domain = parsed_url.hostname

    return domain


def _get_schools():
  # Using gspread: https://docs.gspread.org/en/latest/oauth2.html
  # service_account.json file needs to go in ~/.config/gspread
  schools = []

  try:
    with open(f'{current_path}/schools.json', 'r') as file:
      schools = json.load(file)
  except FileNotFoundError:
    print("The file does not exist.")
  except Exception as e:
    print(f"An error occurred opening file: {e}")
  
  if (schools == []):
    print("Pulling file from Google Sheets")
    gc = gspread.service_account()
    sh = gc.open("Colleges with Baseball")
    worksheet = sh.worksheet("Schools")
    schools = worksheet.get_all_records()
  
  return schools


def _clean_school(school):
  # change key names
  if "Name" in school:
    school["name"] = school.pop("Name")
  if "Ipeds No." in school:
    school["id"] = school.pop("Ipeds No.")
  if "Website" in school:
    school["url_main"] = school.pop("Website")
  if "Division" in school:
    school["division"] = school.pop("Division")
  if "Baseball Website" in school:
    school["url_baseball"] = school.pop("Baseball Website")
  if "City" in school:
    school["city"] = school.pop("City")
  if "State" in school:
    school["state"] = school.pop("State")
  if "Miles Away" in school:
    school["miles_away"] = school.pop("Miles Away")
  if "Hours Within" in school:
    school["hours_within"] = school.pop("Hours Within")

  # remove excess properties
  if "Yes/No/Maybe" in school:
    del school["Yes/No/Maybe"]
  if "Enrollment" in school:
    del school["Enrollment"]
  if "Admissions" in school:
    del school["Admissions"]
  if "Majors" in school:
    del school["Majors"]
  if "STEM" in school:
    del school["STEM"]
  if "Conference" in school:
    del school["Conference"]
  if "Coaches" in school:
    del school["Coaches"]
  if "Coaches email" in school:
    del school["Coaches email"]
  if "Schedule" in school:
    del school["Schedule"]
  if "Recruiting" in school:
    del school["Recruiting"]
  if "Is Private" in school:
    del school["Is Private"]
  if "Historically Black" in school:
    del school["Historically Black"]
  if "Recruiting Questionnaire Done" in school:
    del school["Recruiting Questionnaire Done"]
  if "Emails Sent" in school:
    del school["Emails Sent"]
  if "Response" in school:
    del school["Response"]
  if "Notes" in school:
    del school["Notes"]


def _process_using_alpha(soup, school):
  success = False
  scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
  if scripts and scripts[0] and scripts[0].contents and scripts[0].contents[0]:
    contents = scripts[0].contents[0]
    if contents and _is_valid_json(contents):
      schedule = json.loads(contents)
      if schedule:
        print(f"Number of games: {len(schedule)}")
        file_name = f"{current_path}/data/{school['id']}.json"
        with open(file_name, 'w') as file:
          print(f"Writing file: {file_name}")
          json.dump(schedule, file)
          success = True

  return success

def _process_using_beta(school):
  success = False
  
  # call https://gwsports.com/api/v2/Sports endpoint to get the schedule id
  req_api = requests.get(f"https://{school['url_athletics']}/api/v2/Sports")
  if req_api and req_api.text:
    sports = json.loads(req_api.text)
    if sports:
      for sport in sports:
        if sport and sport["shortName"] == "baseball" and sport["scheduleId"]:
          url = f"https://admin.{school['url_athletics']}/services/schedule_txt.ashx?schedule={sport['scheduleId']}"
          headers = {'Content-Type': 'text/html', 'User-Agent': 'PostmanRuntime/7.33.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
          req_schedule = requests.get(url, headers=headers)
          if req_schedule and req_schedule.text:
            # print(req_schedule.text)
            _parse_html_schedule(req_schedule.text)
          
          # print(sport)
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


def _fetch_schedule(school):
  success = False
  if "url_athletics" not in school:
    school['url_athletics'] = ""
    if school['url_baseball'] != "" and school['url_baseball'] is not None:
      school['url_athletics'] = _extract_domain(school['url_baseball'])

  if school['url_athletics'] != "" and school['url_athletics'] is not None:
    url = ""
    if school['division'] == "NCAA D1" or school['division'] == "NCAA D3":
      url = f"https://{school['url_athletics']}/sports/baseball/schedule/2024"

    if (url != ""):
      print(f"Fetching schedule for {school['name']} ({school['division']})")
      html = requests.get(url)
      
      if html and html.text:
        school['url_baseball'] = url
        soup = BeautifulSoup(html.text, 'html.parser')
        if soup:
          # success = _process_using_alpha(soup, school)
          success = _process_using_beta(school)

  school["schedule_saved"] = success




def _main():
  # schools = _get_schools()
  schools = [
    {
      "name": "George Washington University",
      "id": 131469,
      "url_main": "https://www.gwu.edu/",
      "division": "NCAA D1",
      "url_baseball": "https://gwsports.com/sports/baseball/schedule/2024",
      "city": "Washington",
      "state": "DC",
      "miles_away": 33,
      "hours_within": 1,
      "schedule_saved": False,
      "url_athletics": "gwsports.com"
    }
  ]

  schedules_saved_d1 = 0
  schedules_saved_d2 = 0
  schedules_saved_d3 = 0
  schedules_not_saved_d1 = 0
  schedules_not_saved_d2 = 0
  schedules_not_saved_d3 = 0

  for index, school in enumerate(schools, start=1):
    print(f"School {index} of {len(schools)}")
    # _clean_school(school)
    
    if "schedule_saved" not in school or not school["schedule_saved"]:
      _fetch_schedule(school)

    #   if school['division'] == "NCAA D1":
    #     schedules_not_saved_d1 += 1
    #   elif school['division'] == "NCAA D2":
    #     schedules_not_saved_d2 += 1
    #   elif school['division'] == "NCAA D3":
    #     schedules_not_saved_d3 += 1
    # else:
    #   if school['division'] == "NCAA D1":
    #     schedules_saved_d1 += 1
    #   elif school['division'] == "NCAA D2":
    #     schedules_saved_d2 += 1
    #   elif school['division'] == "NCAA D3":
    #     schedules_saved_d3 += 1

  # with open(f'{current_path}/schools.json', 'w') as file:
  #   json.dump(schools, file)

  # print(f"SAVED d1={schedules_saved_d1} d2={schedules_saved_d2} d3={schedules_saved_d3}")
  # print(f"NOT SAVED d1={schedules_not_saved_d1} d2={schedules_not_saved_d2} d3={schedules_not_saved_d3}")

  # SAVED d1=36 d2=0 d3=55
  # NOT SAVED d1=40 d2=62 d3=93

_main()
