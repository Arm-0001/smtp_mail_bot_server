# open the link in a browser provided from the command line

import sys
import selenium
import time
from selenium import webdriver


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    print(f"clicking link: {sys.argv[1]}")
    driver.get(sys.argv[1])

if __name__ == "__main__":
    main()