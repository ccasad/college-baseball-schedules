import logging
import json
import icalendar

from constants import CURRENT_PATH
from common import is_valid_json, request_url
from bs4 import BeautifulSoup

def process(school):
  success = False

  if school['url_athletics'] is not None:
    for url in school['url_athletics']:
      athletic_url = f"{url}/sports/baseball/schedule/2024"
      if (not success and athletic_url != ""):
        try:
          html = request_url(athletic_url)

          if html != None:
            if html:
              soup = BeautifulSoup(html, 'html.parser')
              scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
              if scripts and scripts[0] and scripts[0].contents and scripts[0].contents[0]:
                contents = scripts[0].contents[0]
                if contents and is_valid_json(contents) and "awayTeam" in contents:
                  schedule = json.loads(contents)
                  if schedule and len(schedule) > 10:
                    for event in schedule:
                      clean_event(event)

                    file_name = f"{CURRENT_PATH}/schedules/{school['id']}.json"
                    with open(file_name, 'w') as file:
                      json.dump(schedule, file)
                      school["processor"] = "alpha"
                      school['url_athletics'] = url
                      success = True
          else:
            # see if the ical file is available
            cal_data = request_url(f"{url}/sports/bsb/2023-24/schedule?print=ical")

            if cal_data:
              # Parse the iCal data
              cal = icalendar.Calendar.from_ical(cal_data)

              # Iterate through events in the calendar
              event = None
              events = []
              for component in cal.walk():
                if component.name == "VEVENT":
                  event = clean_calendar_event(component)
                  events.append(event)
          
              if len(events) > 0:
                file_name = f"{CURRENT_PATH}/schedules/{school['id']}.json"
                with open(file_name, 'w') as file:
                  json.dump(events, file)
                  school["processor"] = "alpha"
                  school['url_athletics'] = url
                  success = True

        except Exception as e:
          logging.error(f"process() in processor_alpha.py: An unexpected error occurred: {e}")
        
  return success


def clean_calendar_event(component):
  event = {}
  if component.get("dtstart"):
    date_time = component.get("dtstart").dt
    if date_time:
      event["date"] = date_time.strftime("%Y-%m-%dT%H:%M:%S")

  if component.get("summary"):
    if " vs. " in component.get("summary"):
      event["at_home"] = True
      parts = component.get("summary").split(" vs. ", 1)
      if len(parts) == 2:
        event["opponent"] = parts[1]
    else:
      event["at_home"] = False
      parts = component.get("summary").split(" at ", 1)
      if len(parts) == 2:
        event["opponent"] = parts[1]

  if component.get("location"):
    event["location"] = component.get("location")

  return event


def clean_event(event):
  if "startDate" in event:
    event["date"] = event.pop("startDate")

  if "name" in event:
    name = event["name"]
    event["at_home"] = True if " Vs " in name else False

    if event["at_home"]:
      if "awayTeam" in event and "name" in event["awayTeam"]:
        event["opponent"] = event["awayTeam"]["name"]
    else:
      if "homeTeam" in event and "name" in event["homeTeam"]:
        event["opponent"] = event["homeTeam"]["name"]
    
  if "location" in event and "name" in event["location"]:
    event["location"] = event["location"]["name"]

  if "@context" in event:
    del event["@context"]
  if "name" in event:
    del event["name"]
  if "url" in event:
    del event["url"]
  if "homeTeam" in event:
    del event["homeTeam"]
  if "awayTeam" in event:
    del event["awayTeam"]
  if "endDate" in event:
    del event["endDate"]
  if "eventStatus" in event:
    del event["eventStatus"]
  if "description" in event:
    del event["description"]
  if "image" in event:
    del event["image"]
  if "@type" in event:
    del event["@type"]

