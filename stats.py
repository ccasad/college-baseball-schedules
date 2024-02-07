import json

from datetime import datetime
from constants import CURRENT_PATH
from schools import get_schools

def get_stats():
  stats = {
    "date_processed": datetime.now().isoformat(),
    "total": 0,
    "saved": 0,
    "not_saved": 0,
    "percent_saved": 0,
    "percent_not_saved": 0,
    "d1": {
      "saved": 0,
      "not_saved": 0,
      "total": 0,
      "percent_saved": 0,
      "percent_not_saved": 0,
    },
    "d2": {
      "saved": 0,
      "not_saved": 0,
      "total": 0,
      "percent_saved": 0,
      "percent_not_saved": 0,
    },
    "d3": {
      "saved": 0,
      "not_saved": 0,
      "total": 0,
      "percent_saved": 0,
      "percent_not_saved": 0,
    },
  }
  
  schools = get_schools()

  for school in schools:
    stats["total"] += 1
    if not school["schedule_saved"]:
      stats["not_saved"] += 1
      if school['division'] == "NCAA D1":
        stats["d1"]["not_saved"] += 1
      elif school['division'] == "NCAA D2":
        stats["d2"]["not_saved"] += 1
      elif school['division'] == "NCAA D3":
        stats["d3"]["not_saved"] += 1
    else:
      stats["saved"] += 1
      if school['division'] == "NCAA D1":
        stats["d1"]["saved"] += 1
      elif school['division'] == "NCAA D2":
        stats["d2"]["saved"] += 1
      elif school['division'] == "NCAA D3":
        stats["d3"]["saved"] += 1

  stats["d1"]["total"] = stats["d1"]["not_saved"] + stats["d1"]["saved"]
  stats["d1"]["percent_saved"] = float(format(stats["d1"]["saved"] / stats["d1"]["total"] * 100, '.1f'))
  stats["d1"]["percent_not_saved"] = float(format(stats["d1"]["not_saved"] / stats["d1"]["total"] * 100, '.1f'))
  stats["d2"]["total"] = stats["d2"]["not_saved"] + stats["d2"]["saved"]
  stats["d2"]["percent_saved"] = float(format(stats["d2"]["saved"] / stats["d2"]["total"] * 100, '.1f'))
  stats["d2"]["percent_not_saved"] = float(format(stats["d2"]["not_saved"] / stats["d2"]["total"] * 100, '.1f'))
  stats["d3"]["total"] = stats["d3"]["not_saved"] + stats["d3"]["saved"]
  stats["d3"]["percent_saved"] = float(format(stats["d3"]["saved"] / stats["d3"]["total"] * 100, '.1f'))
  stats["d3"]["percent_not_saved"] = float(format(stats["d3"]["not_saved"] / stats["d3"]["total"] * 100, '.1f'))
  stats["percent_saved"] = float(format(stats["saved"] / stats["total"] * 100, '.1f'))
  stats["percent_not_saved"] = float(format(stats["not_saved"] / stats["total"] * 100, '.1f'))

  try:
    with open(f'{CURRENT_PATH}/stats.json', 'r') as file:
      stats_original = json.load(file)
  except FileNotFoundError:
    print("The stats.json file does not exist")
  except Exception as e:
    print(f"An error occurred opening stats.json file: {e}")

  try:
    stats_original.append(stats)
    with open(f'{CURRENT_PATH}/stats.json', 'w') as file:
      json.dump(stats_original, file)
  except Exception as e:
    print(f"An error occurred writing to stats.json file: {e}")

