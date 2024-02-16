import json


with open(f'./schools.json', 'r') as file:
  schools_original = json.load(file)
with open(f'./schools_from_mysql.json', 'r') as file:
  schools_mysql = json.load(file)

schools_merged = []

for original in schools_original:
  merged = {}
  for mysql in schools_mysql:
    if original["id"] == mysql["ipeds_id"]:
      merged = {**original, **mysql}
      break

  merged["url_baseball"] = None
  merged["is_private"] = True if merged["is_private"] == 1 else False
  merged["is_hist_black"] = True if merged["is_hist_black"] == 1 else False
  merged["miles_away"] = None if merged["miles_away"] == "" else merged["miles_away"]
  merged["hours_within"] = 7 if merged["hours_within"] == "6+" else merged["hours_within"]
  merged["team_logo_svg_url"] = None if merged["team_logo_svg_url"] == "null" else merged["team_logo_svg_url"]
  merged["team_name"] = None if merged["team_name"] == "undefined" else merged["team_name"]
  merged["team_wiki_url"] = None if merged["team_wiki_url"] == "undefined" else merged["team_wiki_url"]
  
  del merged["ipeds_id"]
  del merged["naics_code"]
  del merged["naics_desc"]
  del merged["main_website_url"]
  schools_merged.append(merged)

print(schools_merged)

with open(f"./schools_merged.json", 'w') as file:
  json.dump(schools_merged, file)

# ORIGINAL 
# {
#   "name": "Marshall University",
#   "id": 237525,
#   "url_main": "https://www.marshall.edu",
#   "division": "NCAA D1",
#   "url_baseball": null,
#   "city": "Huntington",
#   "state": "WV",
#   "miles_away": "",
#   "hours_within": "6+",
#   "url_athletics": "https://www.herdzone.com",
#   "schedule_saved": true,
#   "processor": "beta"
# }

# MYSQL 
# {
#   "ipeds_id": 490805,
#   "name": "Purdue University Northwest",
#   "naics_code": 611310,
#   "naics_desc": "Colleges, Universities, And Professional Schools",
#   "ncaa_org_id": 30222,
#   "ncaa_division": 2,
#   "ncaa_conf_id": 854,
#   "ncaa_conf_name": "Great Lakes Intercollegiate Athletic Conference",
#   "ncaa_region": "Midwest Region",
#   "street": "2200 169th Street",
#   "city": "Hammond",
#   "state": "IN",
#   "zip": 32767,
#   "latitude": 41.5803,
#   "longitude": -87.4738,
#   "is_private": 0,
#   "is_hist_black": 0,
#   "total_enrollment": 10473,
#   "main_website_url": "www.pnw.edu",
#   "school_wiki_url": "/wiki/Purdue_University_Northwest",
#   "school_seal_svg_url": "https://upload.wikimedia.org/wikipedia/en/6/61/Purdue_University_seal.svg",
#   "team_name": "undefined",
#   "team_colors": "#E6B10E,#000000",
#   "team_logo_svg_url": "null",
#   "team_wiki_url": "undefined"
# }
