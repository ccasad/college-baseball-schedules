import logging
import json
import gspread  # Using gspread: https://docs.gspread.org/en/latest/oauth2.html
                # service_account.json file needs to go in ~/.config/gspread

from common import extract_domain, request_url, find_url
from bs4 import BeautifulSoup
from constants import CURRENT_PATH


def get_schools():
  schools = []
  
  try:
    with open(f'{CURRENT_PATH}/schools.json', 'r') as file:
      schools = json.load(file)
      logging.info(f"get_schools() in schools.py: Successfully got schools from schools.json")
  except FileNotFoundError:
    logging.error(f"get_schools() in schools.py: The schools.json file does not exist")
  except Exception as e:
    logging.error(f"get_schools() in schools.py: An error occurred opening schools.json file: {e}")
  
  if (schools == []):
    try:
      gc = gspread.service_account()
      sh = gc.open("Colleges with Baseball")
      worksheet = sh.worksheet("Schools")
      schools = worksheet.get_all_records()
      if schools:
        for school in schools:
          _clean_google_sheet_school(school)
      logging.info(f"get_schools() in schools.py: Successfully got schools from Google Sheets")
    except gspread.exceptions.SpreadsheetNotFound:
      logging.error(f"get_schools() in schools.py: Google Spreadsheet does not exist")
    except gspread.exceptions.WorksheetNotFound:
      logging.error(f"get_schools() in schools.py: Google Worksheet does not exist")
    except Exception as e:
      logging.error(f"get_schools() in schools.py: An error occurred opening the Google Sheets file: {e}")

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
  else:
    if not isinstance(school["url_athletics"], list):
      school["url_athletics"] = [school["url_athletics"]]

  if school["url_athletics"] is not None:
    urls = []
    main_domain = extract_domain(school['url_main'], True)
    for url in school["url_athletics"]:
      # if the url has the same domain as the url_main then lets check the url to 
      # see if that url actually has the true athletics url on its page so call the
      # find_athletics_url function again passing in the url
      if main_domain in url:
        find_athletics_url(school, url)

    for url in school["url_athletics"]:    
      if not url.startswith("http"):
        url = f"https://{url}"
    
      # check for forwarded urls
      response = request_url(url, True)
      if response and response.get("url") != url:
        url = response.get("url")

      if url.endswith('/'):
        url = url[:-1]  # Remove the last forward slash

      url = url.replace("/landing/index", "")
      urls.append(url)

    school["url_athletics"] = urls

  if school['url_main'] != "" and school['url_main'] is not None:
    if not school["url_main"].startswith("http"):
      school["url_main"] = f"https://{school['url_main']}"

    if school["url_main"].endswith('/'):
      school["url_main"] = school["url_main"][:-1]  # Remove the last forward slash


def find_athletics_url(school, url=None):
  second_try = False
  if not url:
    if school['url_main'].endswith("/"):
      school["url_main"] = school["url_main"][:-1]
    url = school['url_main']
    if not school["url_main"].startswith("http"):
      url = f"https://{school['url_main']}"
      school['url_main'] = url
  else:
    second_try = True

  try:
    response = request_url(url)
    if response and response.get('text'):
      soup = BeautifulSoup(response.get('text'), 'html.parser')
      links = soup.find_all('a')

      if len(links) > 0:
        urls = []
        if url != school["url_main"]:
          urls.append(url)

        for link in links:
          for content in link.contents:
            c = str(content).lower()
            found = False
            if second_try and ("visit" in c or "explore" in c or "sports" in c or "team" in c):
              found = True
            elif not second_try and "athletics" in c:
              found = True

            if found:
              if link and link.get('href'):
                url_found = find_url(link.get('href'))
                if url_found:
                  if url_found.lower() == school["url_main"].lower() or extract_domain(url_found.lower()) == extract_domain(school["url_main"].lower(), True):
                    url_found = link.get('href')

                  urls.append(url_found.lower())
                else:
                  slash = ""
                  if not school['url_main'].endswith("/") and not link['href'].startswith("/"):
                    slash = "/"
                  urls.append(f"{school['url_main']}{slash}{link['href']}")

        if len(urls) > 0:
          if not isinstance(school["url_athletics"], list):
            school["url_athletics"] = []
          school["url_athletics"].extend(urls)
          school["url_athletics"] = list(set(school["url_athletics"]))


  except Exception as e:
    logging.error(f"find_athletics_url() in schools.py: An error occurred: {e}")
    logging.error(f"find_athletics_url() in schools.py: {school['id']} has a bad url_main")
        