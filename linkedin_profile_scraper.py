"""
I need this project done preferably in the next 2 days.
I need someone to create a python function.
I will give a user linkedin url, you will scrape all profile information similar to https://nubela.co/proxycurl/people-api but less sophisticated. (i.e. https://www.linkedin.com/in/marianebekker/
I want to have information from name, header, about, experience, volunteer, education sections, achievement sections).
I also want to scrape a list of recent activities from this person which ususally has a url like this (https://www.linkedin.com/in/marianebekker/recent-activity/all/)
I want to have top 10 most recent posts, post content, and link inside the post and link to the post.

The script will require user to login
It should work with 2FA
Use .env file for credentials

The results can be stored in csv or just return a json string from your python function.
"""

import argparse
import csv
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver


def linkedin_profile_scraper(profile_url, output_format):
    # Load LinkedIn credentials
    linkedin_username, linkedin_password = load_credentials()

    # Initialize the Selenium driver
    driver = webdriver.Chrome()  # You'll need the Chrome WebDriver.

    # Log in to LinkedIn
    driver.get("https://www.linkedin.com/login")
    driver.find_element_by_id("username").send_keys(linkedin_username)
    driver.find_element_by_id("password").send_keys(linkedin_password)
    driver.find_element_by_class_name("login__form_action_container").click()

    # Navigate to the user's LinkedIn profile
    driver.get(profile_url)

    # Parse the profile page with BeautifulSoup and scrape information
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract the desired information from the BeautifulSoup object

    # Close Selenium driver
    driver.quit()

    # Store the results in CSV or return as a JSON string
    if output_format == "csv":
        with open("output.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    elif output_format == "json":
        with open("output.csv", "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # Write data to CSV


def load_credentials():
    """Load LinkedIn credentials from .env file."""
    load_dotenv()
    username = os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    return username, password


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="LinkedIn Profile Scraper")
    parser.add_argument("--profile-url", help="LinkedIn profile URL")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format (json or csv)")
    args = parser.parse_args()
    profile_url = args.profile_url
    output_format = args.format

    # Scrape the LinkedIn profile
    linkedin_profile_scraper(profile_url, output_format)
