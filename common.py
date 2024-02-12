import json
import requests
import re
import logging

from urllib.parse import urlparse


def is_valid_json(json_str):
  try:
    json.loads(json_str)
    return True
  except json.JSONDecodeError:
    return False
  

def extract_domain(url, ignore_subdomain=False):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the domain from the hostname component
    domain = parsed_url.hostname

    # Ignore subdomains if specified
    if ignore_subdomain and domain:
      parts = domain.split('.')
      if len(parts) >= 2:
        domain = parts[-2] + '.' + parts[-1]

    return domain


def find_url(text):
  # Define a regex pattern for matching URLs
  url_pattern = re.compile(r'https?://\S+?\.(?:com|edu)')

  # Find all matches in the text
  matches = re.findall(url_pattern, text)
  
  if matches:
    return matches[0]
  else:
    return None

def request_url(url):
  success = None
  try:
    headers = {'Content-Type': 'text/plain; charset=utf-8', 'User-Agent': 'PostmanRuntime/7.33.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    if response.text:
      success = response.text
  except requests.exceptions.HTTPError as http_err:
    logging.info(f"request_url() in common.py: HTTP error occurred: {http_err}")
  except requests.Timeout:
    logging.info(f"request_url() in common.py: Request timed out")
  except requests.exceptions.RequestException as req_err:
    logging.info(f"request_url() in common.py: Request error occurred: {req_err}")
  except Exception as e:
    logging.info(f"request_url() in common.py: An unexpected error occurred: {e}")
  
  return success
