import logging

from schools import get_athletics_url
from processor_alpha import process as process_alpha
from processor_beta import process as process_beta
from processor_gamma import process as process_gamma

def fetch_schedule(school):
  try:
    success = False
    
    get_athletics_url(school)

    if school['url_athletics'] is not None:
      for url in school['url_athletics']:
        if not success:
          success = process_alpha(school, url)
          if not success:
            success = process_beta(school, url)
            if not success:
              success = process_gamma(school, url)
        else:
          break

  except Exception as e:
    logging.error(f"fetch_schedule() in schedules.py: An error occurred while in fetch_schedule: {e}")

  if not success:
    school['url_athletics'] = None
    school['url_baseball'] = None

  school["schedule_saved"] = success

  