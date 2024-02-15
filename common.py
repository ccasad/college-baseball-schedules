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
  url_pattern = re.compile(r'https?://\S+?\.(?:com|edu|org|net)')

  # Find all matches in the text
  matches = re.findall(url_pattern, text)
  
  if matches:
    return matches[0]
  else:
    return None

def request_url(url, headOnly=False):
  success = None
  try:
    headers = {'Content-Type': 'text/plain; charset=utf-8', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
    if headOnly:
      response = requests.head(url, headers=headers, timeout=15, allow_redirects=True)
    else:
      response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    
    response.raise_for_status()  # Raise an HTTPError for bad responses
    if response.text:
      success = {
        'url': response.url,
        'text': response.text
      }
    elif response.url:
      success = {
        'url': response.url,
        'text': None
      }
  except requests.exceptions.HTTPError as http_err:
    logging.info(f"request_url() in common.py: HTTP error occurred: {http_err}")
  except requests.Timeout:
    logging.info(f"request_url() in common.py: Request timed out")
  except requests.exceptions.RequestException as req_err:
    logging.info(f"request_url() in common.py: Request error occurred: {req_err}")
  except Exception as e:
    logging.info(f"request_url() in common.py: An unexpected error occurred: {e}")
  
  return success
