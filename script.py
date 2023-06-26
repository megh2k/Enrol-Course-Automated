from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


import time

options = Options()
options.add_experimental_option('detach', True)


driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

driver.get('https://wrem.sis.yorku.ca/Apps/WebObjects/REM.woa/wa/DirectAction/rem')

# Enter username and password to sign in York Passport
username = ""
password = ""

driver.find_element(By.ID, 'mli').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_element(By.NAME, 'dologin').click()

time.sleep(5)
driver.implicitly_wait(5)


# Logged in successfully

# Select Fall/Winter 24 from options, click Continue
select = Select(driver.find_element(By.NAME, '5.5.1.27.1.11.0'))
select.select_by_value('3')
driver.find_element(By.NAME, '5.5.1.27.1.13').click()

time.sleep(2)
driver.implicitly_wait(2)


# Start Loop

flag = False

while flag == False:
    # click Add a Course
    driver.find_element(By.NAME, '5.1.27.1.23').click()
    time.sleep(2)
    driver.implicitly_wait(2)

    # Enter the course catalogue number as a string
    catalogue_number = ""

    # Enter catalogue number, click Add Course
    driver.find_element(By.NAME, '5.1.27.7.7').send_keys(catalogue_number)
    driver.find_element(By.NAME, '5.1.27.7.9').click()

    time.sleep(2)
    driver.implicitly_wait(2)

    # Are you sure? Yes
    driver.find_element(By.NAME, '5.1.27.11.11').click()

    time.sleep(2)
    driver.implicitly_wait(2)


    # 2 possibilities, either failed or succedded

    # check if failed
    results_text = driver.find_elements(By.CLASS_NAME, 'bodytext')
    success = "The course has been successfully added."

    for x in results_text:
        if x.text == success:

            # Course added successfully, click continue and exit loop
            driver.find_element(By.NAME, '5.1.27.23.9').click()
            flag = True
            break

    # value did not change => course failed to be added
    if flag == False:

        # Failed, click continue, start loop again
        driver.find_element(By.NAME, '5.1.27.27.11').click()
        print("Course could now be added, trying again in 30 sec :)")
        time.sleep(30)
        driver.implicitly_wait(30)

    else:
        print("Successfully added the course")

driver.close()
