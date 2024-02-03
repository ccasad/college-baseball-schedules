import json
import gspread  # Using gspread: https://docs.gspread.org/en/latest/oauth2.html
                # service_account.json file needs to go in ~/.config/gspread

from constants import CURRENT_PATH
from common import is_valid_json

  # schools = [
  #   {
  #     "name": "George Washington University",
  #     "id": 131469,
  #     "url_main": "https://www.gwu.edu/",
  #     "division": "NCAA D1",
  #     "url_baseball": "https://gwsports.com/sports/baseball/schedule/2024",
  #     "city": "Washington",
  #     "state": "DC",
  #     "miles_away": 33,
  #     "hours_within": 1,
  #     "schedule_saved": False,
  #     "url_athletics": "gwsports.com"
  #   }
  # ]

def get_schools():
  schools = []

  try:
    with open(f'{CURRENT_PATH}/schools.json', 'r') as file:
      if is_valid_json(file):
        schools = json.load(file)
      else:
        print("The schools.json file is not valid JSON")
  except FileNotFoundError:
    print("The schools.json file does not exist")
  except Exception as e:
    print(f"An error occurred opening file: {e}")
  
  if (schools == []):
    try:
      print("Pulling file from Google Sheets")
      gc = gspread.service_account()
      sh = gc.open("Colleges with Baseball")
      worksheet = sh.worksheet("Schools")
      schools = worksheet.get_all_records()
      if schools:
        for school in schools:
          _clean_google_sheet_school(school)

    except gspread.exceptions.SpreadsheetNotFound:
      print("Google Spreadsheet does not exist")
    except gspread.exceptions.WorksheetNotFound:
      print("Google Worksheet does not exist")
    except Exception as e:
      print(f"An error occurred opening the Google Sheets file: {e}")

  return schools


def _clean_google_sheet_school(school):
  # change key names
  if "Name" in school:
    school["name"] = school.pop("Name")
  if "Ipeds No." in school:
    school["id"] = school.pop("Ipeds No.")
  if "Website" in school:
    school["url_main"] = school.pop("Website")
  if "Division" in school:
    school["division"] = school.pop("Division")
  if "Baseball Website" in school:
    school["url_baseball"] = school.pop("Baseball Website")
  if "City" in school:
    school["city"] = school.pop("City")
  if "State" in school:
    school["state"] = school.pop("State")
  if "Miles Away" in school:
    school["miles_away"] = school.pop("Miles Away")
  if "Hours Within" in school:
    school["hours_within"] = school.pop("Hours Within")

  # remove excess properties
  if "Yes/No/Maybe" in school:
    del school["Yes/No/Maybe"]
  if "Enrollment" in school:
    del school["Enrollment"]
  if "Admissions" in school:
    del school["Admissions"]
  if "Majors" in school:
    del school["Majors"]
  if "STEM" in school:
    del school["STEM"]
  if "Conference" in school:
    del school["Conference"]
  if "Coaches" in school:
    del school["Coaches"]
  if "Coaches email" in school:
    del school["Coaches email"]
  if "Schedule" in school:
    del school["Schedule"]
  if "Recruiting" in school:
    del school["Recruiting"]
  if "Is Private" in school:
    del school["Is Private"]
  if "Historically Black" in school:
    del school["Historically Black"]
  if "Recruiting Questionnaire Done" in school:
    del school["Recruiting Questionnaire Done"]
  if "Emails Sent" in school:
    del school["Emails Sent"]
  if "Response" in school:
    del school["Response"]
  if "Notes" in school:
    del school["Notes"]


def get_stats(schools):
  schedules_saved_d1 = 0
  schedules_saved_d2 = 0
  schedules_saved_d3 = 0
  schedules_not_saved_d1 = 0
  schedules_not_saved_d2 = 0
  schedules_not_saved_d3 = 0

  for index, school in enumerate(schools, start=1):
    print(f"School {index} of {len(schools)}")

  #   if school['division'] == "NCAA D1":
  #     schedules_not_saved_d1 += 1
  #   elif school['division'] == "NCAA D2":
  #     schedules_not_saved_d2 += 1
  #   elif school['division'] == "NCAA D3":
  #     schedules_not_saved_d3 += 1
  # else:
  #   if school['division'] == "NCAA D1":
  #     schedules_saved_d1 += 1
  #   elif school['division'] == "NCAA D2":
  #     schedules_saved_d2 += 1
  #   elif school['division'] == "NCAA D3":
  #     schedules_saved_d3 += 1

  # print(f"SAVED d1={schedules_saved_d1} d2={schedules_saved_d2} d3={schedules_saved_d3}")
  # print(f"NOT SAVED d1={schedules_not_saved_d1} d2={schedules_not_saved_d2} d3={schedules_not_saved_d3}")

  # SAVED d1=36 d2=0 d3=55
  # NOT SAVED d1=40 d2=62 d3=93