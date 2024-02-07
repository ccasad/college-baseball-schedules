import json
import gspread  # Using gspread: https://docs.gspread.org/en/latest/oauth2.html
                # service_account.json file needs to go in ~/.config/gspread

from common import extract_domain, request_url
from bs4 import BeautifulSoup
from constants import CURRENT_PATH


def get_schools():
  schools = []

  try:
    with open(f'{CURRENT_PATH}/schools.json', 'r') as file:
      schools = json.load(file)
  except FileNotFoundError:
    print("The schools.json file does not exist")
  except Exception as e:
    print(f"An error occurred opening schools.json file: {e}")
  
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


def find_school_by_id(schools, school_id):
  for school in schools:
    if school.get("id") == school_id:
      return school
  return None


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


def get_athletics_url(school):
  if "url_athletics" not in school or school['url_athletics'] == "":
    school['url_athletics'] = None

  if school['url_athletics'] is None:
    if school['url_baseball'] != "" and school['url_baseball'] is not None:
        school['url_athletics'] = [f"https://{extract_domain(school['url_baseball'])}"]

    if school['url_athletics'] is None:
      if school['url_main'] != "" and school['url_main'] is not None:
        find_athletics_url(school)

  if school["url_athletics"] is not None:
    for url in school["url_athletics"]:
      if not url.startswith("http"):
        school["url_athletics"] = f"https://{url}"
      if url.endswith('/'):
        school["url_athletics"] = url[:-1]  # Remove the last forward slash

  if school['url_main'] != "" and school['url_main'] is not None:
    if not school["url_main"].startswith("http"):
      school["url_main"] = f"https://{school['url_main']}"

    if school["url_main"].endswith('/'):
      school["url_main"] = school["url_main"][:-1]  # Remove the last forward slash


def find_athletics_url(school):
  url = school['url_main']
  if not school["url_main"].startswith("http"):
    url = f"https://{school['url_main']}"
    school['url_main'] = url

  html = request_url(url)
  if html:
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    if len(links) > 0:
      urls = []
      for link in links:
        for content in link.contents:
          c = str(content).lower()
          if "athletics" in c:
            if link and link['href']:
              if link['href'].startswith("http") or "." in link['href']:
                urls.append(f"https://{extract_domain(link['href'])}")
              else:
                urls.append(f"{school['url_main']}{link['href']}")

      school["url_athletics"] = urls
          