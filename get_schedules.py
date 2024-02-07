import json

from constants import CURRENT_PATH
from schools import get_schools, find_school_by_id
from schedules import fetch_schedule
from stats import get_stats

def _main():
  schools = get_schools()

  school_id = 0

  if school_id == 0:
    for index, school in enumerate(schools, start=1):
      if "schedule_saved" not in school or not school["schedule_saved"]:
        print(f"{index} of {len(schools)} - {school['id']} {school['name']} ({school['division']})")
        fetch_schedule(school)
      else:
        print(f"{index} of {len(schools)}")
  else:
    school = find_school_by_id(schools, school_id)
    print(f"{school['name']} ({school['division']})")
    fetch_schedule(school)

  with open(f'{CURRENT_PATH}/schools.json', 'w') as file:
    json.dump(schools, file)

  get_stats()


_main()
