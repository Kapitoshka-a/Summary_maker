import pytest
from unittest.mock import MagicMock, call, patch
from io import StringIO
import cloudscraper
from openai import OpenAI
import csv
from main import collect_pages, generate_summary, create_google_ads_csv

OPENAI_API_KEY = 'sk-MOCKAPIKEY'
GPT_MODEL = "gpt-4-turbo"


@pytest.fixture
def mock_openai():
    return MagicMock(spec=OpenAI)


@pytest.fixture
def mock_cloudscraper():
    return MagicMock(spec=cloudscraper.CloudScraper)


@pytest.fixture
def mock_csv_writer(mocker):
    return mocker.patch('csv.writer')


def test_collect_pages(mock_cloudscraper):
    mock_scraper_instance = MagicMock(spec=cloudscraper.CloudScraper)
    mock_scraper_instance.get.side_effect = [
        MagicMock(content="<html><title>Test Title</title></html>"),
        MagicMock(content="<html><title>Test Title 2</title></html>")
    ]
    mock_cloudscraper.create_scraper.return_value = mock_scraper_instance

    url = "http://example.com"
    pages = collect_pages(url)

    assert len(pages) == 1
    assert pages[0]['url'] == url


@patch('openai.OpenAI')
def test_generate_summary(mock_openai_class):
    mock_openai_instance = MagicMock()
    mock_openai_class.return_value = mock_openai_instance

    mock_openai_instance.chat.completions.create.return_value.choices[0].message.content = "This is a generated summary."

    summary = generate_summary("Sample text")

    assert summary is not None


def test_create_google_ads_csv(mock_csv_writer):
    mock_csv_file = StringIO()
    mock_csv_writer.return_value = csv.writer(mock_csv_file)

    pages = [{'url': 'http://example.com', 'html': '<html><title>Test Title</title></html>'}]
    site_url = "http://example.com"
    site_summary = "This is a test summary."

    create_google_ads_csv(pages, site_url, site_summary)

    expected_calls = [
        call(['Campaign', 'Ad Group', 'Headline', 'Summary', 'Final URL']),
        call([site_url, 'Default Ad Group', 'Test Title', site_summary, 'http://example.com'])
    ]
    mock_csv_writer().writerow.assert_has_calls(expected_calls)


if __name__ == "__main__":
    pytest.main()
