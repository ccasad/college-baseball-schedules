import json

from constants import CURRENT_PATH
from common import is_valid_json
from bs4 import BeautifulSoup

def process(html, school):
  success = False
  soup = BeautifulSoup(html, 'html.parser')
  scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
  if scripts and scripts[0] and scripts[0].contents and scripts[0].contents[0]:
    contents = scripts[0].contents[0]
    if contents and is_valid_json(contents):
      schedule = json.loads(contents)
      if schedule:
        file_name = f"{CURRENT_PATH}/schedules/{school['id']}.json"
        with open(file_name, 'w') as file:
          json.dump(schedule, file)
          school["processor"] = "alpha"
          success = True

  return success
