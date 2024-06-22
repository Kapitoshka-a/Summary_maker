import cloudscraper
from bs4 import BeautifulSoup
from openai import OpenAI
import csv
import os
from typing import Dict, List


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4-turbo"
SEED = 1
TEMPERATURE = 0.7

user = OpenAI(api_key=OPENAI_API_KEY)


def collect_pages(url: str) -> List[Dict[str, str]]:
    scraper = cloudscraper.create_scraper()
    pages = []
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        pages.append({
            'url': url,
            'html': soup.prettify()
        })

        links = soup.find_all('a', href=True)
        for link in links[0:1]:
            href = link['href']
            if href.startswith('/'):
                href = url + href
            if href.startswith(url):
                response = scraper.get(href)
                soup = BeautifulSoup(response.content, 'html.parser')
                pages.append({
                    'url': href,
                    'html': soup.prettify()
                })
    except Exception as e:
        print(f"Помилка при зборі сторінок: {e}")
    return pages


def generate_summary(text: str) -> str:
    response = user.chat.completions.create(
        model=GPT_MODEL,
        messages=[{'role': 'user', 'content': f'generate me a short summary about this site using this text - {text}'}],
        temperature=TEMPERATURE,
        max_tokens=150,
    )
    summary = response.choices[0].message.content
    return summary


def create_google_ads_csv(pages: List[Dict[str, str]], site_url: str, site_summary: str) -> None:
    with (open('google_ads.csv', mode='w', newline='', encoding='utf-8') as file):
        writer = csv.writer(file)
        writer.writerow(['Campaign', 'Ad Group', 'Headline', 'Summary', 'Final URL'])
        for page in pages:
            url = page['url']
            soup = BeautifulSoup(page['html'], 'html.parser')
            title = soup.find('title').text if soup.find('title') else 'Title not found'
            writer.writerow([site_url, 'Default Ad Group', title, site_summary, url])


def main() -> None:
    site_url = input("Введіть URL сайту: ")
    pages = collect_pages(site_url)

    if not pages:
        print("Не вдалося зібрати сторінки з сайту.")
        return

    full_text = ' '.join([page['html'] for page in pages])
    print(full_text)
    site_summary = generate_summary(full_text)

    create_google_ads_csv(pages, site_url, site_summary)
    print("CSV файл з оголошеннями для Google Ads створено як 'google_ads.csv'.")


if __name__ == "__main__":
    main()
