import logging
import json
import icalendar

from constants import CURRENT_PATH
from common import request_url

def process(school, url):
  success = False

  athletic_url = f"{url}/sports/bsb/2023-24/schedule?print=ical"

  try:
    response_ical = request_url(athletic_url)

    if response_ical:
      # Parse the iCal data
      cal = icalendar.Calendar.from_ical(response_ical)

      # Iterate through events in the calendar
      event = None
      events = []
      for component in cal.walk():
        if component.name == "VEVENT":
          event = clean_event(component)
          events.append(event)
  
      if len(events) > 0:
        file_name = f"{CURRENT_PATH}/schedules/{school['id']}.json"
        with open(file_name, 'w') as file:
          json.dump(events, file)
          school["processor"] = "gamma"
          school['url_athletics'] = url
          success = True

  except Exception as e:
    logging.error(f"process() in processor_gamma.py: An unexpected error occurred: {e}")
  
  return success


def clean_event(component):
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

