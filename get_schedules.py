import json

from constants import CURRENT_PATH
from schools import get_schools, get_stats
from schedules import fetch_schedule

def _main():
  schools = get_schools()

  for index, school in enumerate(schools, start=1):
    print(f"{index} of {len(schools)} - {school['name']} ({school['division']})")
    if "schedule_saved" not in school or not school["schedule_saved"]:
      fetch_schedule(school)

  with open(f'{CURRENT_PATH}/schools.json', 'w') as file:
    json.dump(schools, file)

  get_stats(schools)


_main()
