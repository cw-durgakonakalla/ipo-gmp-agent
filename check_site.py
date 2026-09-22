import requests
import re
from bs4 import BeautifulSoup

base = 'https://www.investorgain.com'
r = requests.get(f'{base}/report/ipo-gmp-live/331/',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}, timeout=15)

soup = BeautifulSoup(r.text, 'html.parser')

# Check the streamed RSC data embedded in page
all_scripts = soup.find_all('script')
print(f'Total script tags: {len(all_scripts)}')
for s in all_scripts:
    content = s.string or ''
    if 'gmp' in content.lower() or 'ipo' in content.lower() or 'listing' in content.lower():
        print('Found relevant inline script:')
        print(content[:1000])
        print('---')

# Search JS chunks for keywords
chunks = re.findall(r'"(/_next/static/chunks/[^"]+\.js)"', r.text)
chunks = list(set(chunks))
for chunk_url in chunks:
    try:
        js = requests.get(base + chunk_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).text
        if 'gmp' in js.lower() or 'ipo-gmp' in js.lower() or 'reportTable' in js:
            print(f'\nFound keyword in chunk: {chunk_url.split("/")[-1]}')
            # Find surrounding context
            idx = js.lower().find('gmp')
            print(js[max(0,idx-100):idx+300])
    except Exception:
        pass
