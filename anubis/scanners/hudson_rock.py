from urllib.parse import urlsplit

import requests


def search_hudsonrock(self, target):
  print("Searching HudsonRock")
  try:
    res = requests.get("https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain=" + target)
    urls = res.json().get('data', {}).get('all_urls', [])
  except Exception as e:
    self.handle_exception(e, "Error searching HudsonRock")
    return

  for url_entry in urls:
    try:
      # Entries are full URLs (https://sso.example.com/login); keep the host
      domain = urlsplit(url_entry.get('url', '')).hostname
    except (AttributeError, ValueError):
      continue
    if domain and domain.endswith("." + target) and domain not in self.domains:
      self.domains.append(domain)
      if self.options["--verbose"]:
        print("HudsonRock Found Domain:", domain)
