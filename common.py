import json
import requests

from urllib.parse import urlparse


def is_valid_json(json_str):
  try:
    json.loads(json_str)
    return True
  except json.JSONDecodeError:
    return False
  

def extract_domain(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the domain from the hostname component
    domain = parsed_url.hostname

    return domain


def request_url(url):
  success = None
  try:
    headers = {'Content-Type': 'text/plain; charset=utf-8', 'User-Agent': 'PostmanRuntime/7.33.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    if response.text:
      success = response.text
  except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
  except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  
  return success
