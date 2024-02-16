import json


with open(f'./schools_merged.json', 'r') as file:
  schools = json.load(file)

for school in schools:

  try:
    with open(f'./schedules/{school["id"]}.json', 'r') as file:
      schedule = json.load(file)
  except FileNotFoundError:
    print(f'The {school["id"]}.json file does not exist')
  except Exception as e:
    print(f'An error occurred opening {school["id"]}.json file: {e}')
  
  print(school["name"])
  print(json.dumps(schedule))
