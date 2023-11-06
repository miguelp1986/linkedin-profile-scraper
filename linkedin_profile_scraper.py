"""
A LinkedIn profile scraper that uses Selenium to scrape LinkedIn profiles and stores the output as JSON.
"""

import argparse
import json
import os
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def linkedin_profile_scraper(profile_url):
    """Scrape a LinkedIn profile and store the output as JSON."""
    # Load LinkedIn credentials
    linkedin_username, linkedin_password = load_credentials()

    # Remove trailing slash from profile URL if present
    profile_url = profile_url.rstrip("/")

    # Initialize the Selenium driver
    driver = webdriver.Chrome()  # You'll need the Chrome WebDriver.
    driver.implicitly_wait(10)  # wait 10 seconds when finding elementss

    # Log in to LinkedIn
    login(driver, linkedin_username, linkedin_password)

    # Wait 5 seconds after logging in
    time.sleep(5)

    # Navigate to the user's LinkedIn profile
    driver.get(profile_url)

    # Wait 5 seconds for the profile page to load
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pv-text-details__left-panel"))
        )

        # Parse the profile page with BeautifulSoup and scrape information
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Collect name, header, about, experience, volunteer, education sections, and achievement sections.
        profile_data = parse_profile(soup)

        # Collect recent activities
        parse_recent_activity(driver, profile_data, profile_url)

    except Exception as e:
        print(e)

    driver.quit()

    return profile_data


def parse_profile(soup):
    """Parse LinkedIn profile with BeautifulSoup."""
    # Extract the desired information from the BeautifulSoup object
    # name, header, about, experience, volunteer, education sections, achievement (Honors & awards) sections
    profile_data = {}

    # get name and header info
    intro = soup.find('div', {'class': 'pv-text-details__left-panel'})
    name_loc = intro.find("h1")
    name = name_loc.get_text().strip()
    profile_data["name"] = name

    header_loc = intro.find("div", {'class': 'text-body-medium'})
    header = header_loc.get_text().strip()
    profile_data["header"] = header

    # get about info
    about_div = soup.find("div", {'id': 'about'})
    if about_div is not None:
        about_spans = about_div.parent.find_all('span')
        if about_spans is not None and len(about_spans) >= 3:
            about = about_spans[3].text.strip()
            profile_data["about"] = about

    # get experience info
    experience_div = soup.find('div', {"id": "experience"})
    if experience_div is not None:
        experience_section = experience_div.parent
        exp_list = experience_section.find('ul').findAll('li', {"class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        experience = []

        for each_exp in exp_list:
            col = each_exp.findNext("div", {"class": "display-flex flex-column full-width"})
            profile_title = col.findNext('div').findNext('span').findNext('span').text
            company_name = col.findNext('span', {"class": "t-14 t-normal"}).findNext('span').text

            experience.append({
                "profile_title": profile_title.replace('\n', '').strip(),
                "company_name": company_name.replace('\n', '').strip(),
            })

            spans = col.findAll('span', {"class": "t-14 t-normal t-black--light"})
            if len(spans) == 2:
                timeframe = col.findAll('span', {"class": "t-14 t-normal t-black--light"})[0].find('span').text
                location = col.findAll('span', {"class": "t-14 t-normal t-black--light"})[1].find('span').text
                experience[-1]["timeframe"] = timeframe.replace('\n', '').strip()
                experience[-1]["location"] = location.replace('\n', '').strip()

            description_dv = each_exp.find("div", {"class": "inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp full-width"})
            if description_dv is not None:
                description = description_dv.find("span").text.strip()
                experience[-1]["description"] = description

            # remove duplicate entries
            unique_experience = []
            seen_experience = set()

            for entry in experience:
                frozen_entry = frozenset(entry.items())

                if frozen_entry not in seen_experience:
                    seen_experience.add(frozen_entry)
                    unique_experience.append(entry)

        profile_data["experience"] = unique_experience

    # get education info
    education_div = soup.find("div", {"id": "education"})
    if education_div is not None:
        education = []
        education_section = education_div.parent
        education_li = education_section.find_all("li")
        for li in education_li:
            institution = li.find_all("span")[0].text.strip()
            education.append({
                "institution": institution
            })

            if len(li.find_all("span")) >= 4:
                diploma = li.find_all("span")[3].text.strip()
                education[-1]["diploma"] = diploma

        profile_data["education"] = education

    # get volunteering info
    volunteering_div = soup.find("div", {"id": "volunteering_experience"})
    if volunteering_div is not None:
        volunteering = []
        volunteering_section = volunteering_div.parent
        volunteering_ul = volunteering_section.find_all("ul")[0]
        volunteering_li = volunteering_ul.find_all("li", {"class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        for li in volunteering_li:
            role = li.find("div", {"class": "display-flex align-items-center mr1 t-bold"}).find("span").text.strip()
            organization = li.find("span", {"class": "t-14 t-normal"}).find("span").text.strip()
            volunteering.append({
                "role": role,
                "organization": organization
            })

            description = li.find("div", {"class": "pv-shared-text-with-see-more full-width t-14 t-normal t-black display-flex align-items-center"})
            if description is not None:
                description = description.find("span").text.strip()
                volunteering[-1]["description"] = description

        profile_data["volunteering"] = volunteering

    # get achievements info
    honors_div = soup.find("div", {"id": "honors_and_awards"})
    if honors_div is not None:
        achievements = []
        honors_section = honors_div.parent
        honors_li = honors_section.find_all("li", {"class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        for li in honors_li:
            title = li.find("div", {"class": "display-flex align-items-center mr1 t-bold"}).find("span").text.strip()
            issuer = li.find("span", {"class": "t-14 t-normal"}).find("span").text.strip()
            achievements.append({
                "title": title,
                "issuer": issuer
            })

        profile_data["achievements"] = achievements

    return profile_data


def parse_recent_activity(driver, profile_data, profile_url):
    """Parse LinkedIn recent activity with BeautifulSoup."""
    time.sleep(5)
    driver.get(f"{profile_url}/recent-activity/all/")
    # Wait 5 seconds for the profile page to load
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # I want to have top 10 most recent posts, post content, and link inside the post and link to the post.
    main = soup.find("main", {"class": "scaffold-layout__main"})
    li = main.find_all("li", {"class": "profile-creator-shared-feed-update__container"})
    posts = []

    # get post content
    if li is not None:
        for each_li in li:
            span = each_li.find("span", {"class": "break-words"})
            if span is not None:
                post_content = span.text.strip()
                posts.append({
                    "post_content": post_content
                    })
        profile_data["posts"] = posts


def save_profile_data(data):
    """Save profile data in a JSON file."""
    with open("output.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def load_credentials():
    """Load LinkedIn credentials from .env file."""
    load_dotenv()
    username = os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    return username, password


def login(driver, linkedin_username, linkedin_password):
    """Log in to LinkedIn."""
    driver.get("https://www.linkedin.com/login")
    driver.find_element("id", "username").send_keys(linkedin_username)
    driver.find_element("id", "password").send_keys(linkedin_password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait 5 seconds for the page to load
    time.sleep(5)
    # Check if 2FA is requesteds
    if driver.find_element("id", "input__phone_verification_pin") is not None:
        tfa_code = input("Enter 2FA code:")
        driver.find_element("id", "input__phone_verification_pin").send_keys(tfa_code)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="LinkedIn Profile Scraper")
    parser.add_argument("-p", "--profile-url", required=True, help="LinkedIn profile URL")
    args = parser.parse_args()
    profile_url = args.profile_url

    # Scrape the LinkedIn profile
    profile_data = linkedin_profile_scraper(profile_url)

    # Save profile data to file
    save_profile_data(profile_data)
