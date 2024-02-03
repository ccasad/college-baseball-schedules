from common import extract_domain, request_url
from processor_alpha import process as process_alpha
from processor_beta import process as process_beta

def fetch_schedule(school):
  success = False
  if "url_athletics" not in school:
    school['url_athletics'] = ""
    if school['url_baseball'] != "" and school['url_baseball'] is not None:
      school['url_athletics'] = extract_domain(school['url_baseball'])

  if school['url_athletics'] != "" and school['url_athletics'] is not None:
    url = f"https://{school['url_athletics']}/sports/baseball/schedule/2024"
  
    if (url != ""):
      html = request_url(url)

      # if that url doesn't work try this one
      if html == None:
        html = request_url(f"https://{school['url_athletics']}/sports/bsb/2023-24/schedule")
      
      if html != None:
        school['url_baseball'] = url
        
        if html.text:
          success = process_alpha(html.text, school)
          if not success:
            success = process_beta(school)

  school["schedule_saved"] = success
