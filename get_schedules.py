import requests
import json

from bs4 import BeautifulSoup

current_path = "./recruiting/scheduler"
failed_schools = []

def _is_valid_json(json_str):
  try:
    json.loads(json_str)
    return True
  except json.JSONDecodeError:
    return False
  
def _fetch_schedule(school):
  url = f"{school['url']}/sports/baseball/schedule/2024"
  print(f"Fetching schedule for {school['name']}")
  html = requests.get(url)
  success = False
  if html and html.text:
    soup = BeautifulSoup(html.text, 'html.parser')
    if soup:
      scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
      if scripts and scripts[0] and scripts[0].contents and scripts[0].contents[0]:
        contents = scripts[0].contents[0]
        if contents and _is_valid_json(contents):
          schedule = json.loads(contents)
          if schedule:
            print(f"Number of games: {len(schedule)}")
            file_name = f"{current_path}/data/{school['abbrev'].lower()}.json"
            with open(file_name, 'w') as file:
              print(f"Writing file: {file_name}")
              json.dump(schedule, file)
              success = True
          else:
            print("schedule doesn't exist")
        else:
          print("JSON is not valid")
      else:
        print("scripts[0].contents[0] doesn't exist")
    else:
      print("soup doesn't exist")
  else:
    print("html or html.text doesn't exist")

  if not success:
    failed_schools.append(school)

schools_dict = [
  { "id": 1, "name": "University of Delaware", "abbrev": "UDEL", "url": "https://bluehens.com" },
  { "id": 2, "name": "George Mason University", "abbrev": "GMU", "url": "https://gomason.com" },
  { "id": 3, "name": "University of Maryland College Park", "abbrev": "UM", "url": "https://umterps.com" },
  { "id": 4, "name": "Towson University", "abbrev": "UT", "url": "https://towsontigers.com" },
  { "id": 5, "name": "University of Maryland Baltimore County", "abbrev": "UMBC", "url": "https://umbcretrievers.com" },
  { "id": 6, "name": "US Naval Academy", "abbrev": "NAVY", "url": "https://navysports.com" },
  { "id": 7, "name": "Eastern Shore University", "abbrev": "ESU", "url": "https://easternshorehawks.com" },
  { "id": 8, "name": "Coppin State University", "abbrev": "CSU", "url": "https://coppinstatesports.com" },
  { "id": 9, "name": "Mount St. Mary's University", "abbrev": "MSMU", "url": "https://mountathletics.com" }
]

for school in schools_dict:
  _fetch_schedule(school)

if len(failed_schools) > 0:
  with open(f'{current_path}/failed_schools.json', 'w') as file:
    json.dump(failed_schools, file)
    
print("DONE")
