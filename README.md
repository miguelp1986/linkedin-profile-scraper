# LinkedIn Profile Scraper

This script is a LinkedIn profile scraper that uses Selenium to scrape LinkedIn profiles and stores the output as JSON file.

Create an `.env` file with your LinkedIn credentials. See `.env_example` for an example

Install Python dependencies:

```
pip install -r requirements.txt
```


```
usage: linkedin_profile_scraper.py [-h] -p PROFILE_URL

LinkedIn Profile Scraper

options:
  -h, --help            show this help message and exit
  -p PROFILE_URL, --profile-url PROFILE_URL
                        LinkedIn profile URL
```

Example command:

```
python linkedin_profile_scraper.py --profile-url "https://www.linkedin.com/in/{username}/"
```

You will prompted for your 2FA code if you have it enabled in your LinkedIn account.
