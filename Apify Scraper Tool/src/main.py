from bs4 import BeautifulSoup
import re
import urllib.parse
import requests
from apify import Actor




def build_search_urls(keywords, pages, base_url="https://www.google.com/search", query_prefix="site:linkedin.com/in/"):
  urls = []
  encoded_keywords = [urllib.parse.quote(f'"{keyword}"') for keyword in keywords]
  query = f"{query_prefix}+({' + '.join(encoded_keywords)})"
  for page in range(pages):
      start_parameter = page * 10
      urls.append(f"{base_url}?q={query}&start={start_parameter}")
  return urls




def fetch_linkedin_profiles(urls):
  linkedin_url_pattern = re.compile(r'https://www\.linkedin\.com/in/[\w-]+/?')
  linkedin_profiles = []
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}




  for url in urls:
      print(url)
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
          soup = BeautifulSoup(response.content, 'html.parser')
          links = soup.find_all('a', href=True)
          for link in links:
              match = linkedin_url_pattern.search(link['href'])
              if match:
                  profile_url = match.group(0)
                  linkedin_profiles.append(profile_url)




  return linkedin_profiles




async def main() -> None:
  async with Actor() as actor:
      actor_input = await actor.get_input() or {}
      keywords = actor_input.get('keywords', ["Chief Product Officer", "United States", "Insurance"])
      pages = actor_input.get('pages', 1)




      urls = build_search_urls(keywords, pages)
      linkedin_profiles = fetch_linkedin_profiles(urls)
      if linkedin_profiles:
          for profile_url in linkedin_profiles:
              await actor.push_data({"linkedin_profile": profile_url})
          actor.log.info(f'Found and pushed {len(linkedin_profiles)} LinkedIn profiles individually.')
      else:
          actor.log.info('No LinkedIn profiles found.')




if __name__ == "__main__":
  Actor.run(main)