import json
import logging

from logging_config import configure_logger
from constants import CURRENT_PATH
from schools import get_schools, find_school_by_id
from schedules import fetch_schedule
from stats import get_stats

def _main():
  configure_logger()
  
  schools = get_schools()

  school_id = 0

  if school_id == 0:
    for index, school in enumerate(schools, start=1):
      if "schedule_saved" not in school or not school["schedule_saved"]:
        msg = f"{index} of {len(schools)} - {school['id']} {school['name']} ({school['division']})"
        print(msg)
        fetch_schedule(school)
        logging.info(f"{msg} - {school['schedule_saved']}")
      else:
        print(f"{index} of {len(schools)}")
  else:
    school = find_school_by_id(schools, school_id)
    msg = f"{school['name']} ({school['division']})"
    print(msg)
    fetch_schedule(school)
    logging.info(f"{msg} - {school['schedule_saved']}")

  with open(f'{CURRENT_PATH}/schools.json', 'w') as file:
    json.dump(schools, file)

  print("SCHOOLS NOT SAVED")
  for school in schools:
    if not school["schedule_saved"]:
      print(f"{school['id']} {school['name']} ({school['division']}) {school['url_main']}")

  get_stats()


_main()
