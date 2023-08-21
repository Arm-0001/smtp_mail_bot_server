import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import requests
import json
import os
import random
import colorama
import sys
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

referral_link = "https://vy.tc/qXkon52"
# get referral link from command line
if len(sys.argv) > 1:
    referral_link = sys.argv[1]
print(f"Using referral link: {referral_link}")
domain = "coolkids.bio"

with open("names.txt") as f:
    names = f.readlines()

def generate_random_name():
    name = names[random.randint(0, len(names)-1)].strip() + " " + names[random.randint(0, len(names)-1)].strip()
    return name

def main(index):
    print(f"{Fore.GREEN}[{index}] Starting...")
    fullname = generate_random_name()
    print(Fore.GREEN + f"[{index}] Name: {fullname}" + Fore.RESET)
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get("https://vy.tc/qXkon52")
    wait = WebDriverWait(driver, 10)

    try:
        print(f"[{index}] Started for {fullname}...")
        first_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[7]/div[1]/div[3]/button")))
        first_button.click()
        name_form = wait.until(EC.element_to_be_clickable((By.NAME, "Entries[full_name]")))
        name_form.send_keys(fullname)
        email_form = wait.until(EC.element_to_be_clickable((By.NAME, "Entries[email]")))
        email_form.send_keys(f"{fullname.replace(' ', '')}@{domain}")
        terms_checkbox = wait.until(EC.element_to_be_clickable((By.NAME, "terms_text")))
        terms_checkbox.click()
        print(f"[{index}] Entered name and email, sending email")
        driver.find_element(By.XPATH, "/html/body/div[3]/div[4]/div/div/div/div[2]/form/fieldset/button").click()
        print("Waiting for confirmation...")

    except Exception as e:
        print(Fore.RED + f"An error occurred: {str(e)}" + Fore.RESET)
    finally:
        driver.quit()
        # close thread
        print(f"{Fore.GREEN}[{index}] Finished" + Fore.RESET)

if __name__ == "__main__":
    print(Fore.GREEN + "Starting..." + Fore.RESET)
    for i in range(0, 100000000):
        t = threading.Thread(target=main, args=(i,))
        t.start()
        time.sleep(5)
        # print active threads
        print(f"{Fore.GREEN}Active threads: {threading.active_count()}" + Fore.RESET)
