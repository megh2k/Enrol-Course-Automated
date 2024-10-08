import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time
import copy
import emailSender
from dotenv import load_dotenv

load_dotenv()

driver = webdriver.Chrome()

rem = "https://wrem.sis.yorku.ca/Apps/WebObjects/REM.woa/wa/DirectAction/rem"
vsb = 'https://schedulebuilder.yorku.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=0&sort' \
      '=none&filters=iiiiiiii&bbs=&ds=&cams=0_1_2_3_4_5_6_7_8&locs=any '

driver.get(vsb)

username = os.getenv('username')
password = os.getenv('password')

# enter all course catalogue numbers in form of string, each separated by a comma
# eg: {'ABC', 'XYZ', '123'}
catalogue_numbers = {}

duplicate = copy.copy(catalogue_numbers)

# 2FA login
driver.find_element(By.ID, 'mli').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_element(By.NAME, 'dologin').click()

time.sleep(15)


def add_course(catalogue_number):
    # Select Fall/Winter 24 from options, click Continue
    select = Select(driver.find_element(By.NAME, '5.5.1.27.1.11.0'))
    select.select_by_value('2')
    driver.find_element(By.XPATH, '//input[@value="Continue"]').click()

    # click Add a Course
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@title="Add a Course"]'))
    ).click()

    # Enter catalogue number, click Add Course
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
    ).send_keys(catalogue_number)
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()

    # Are you sure? Yes
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@value="Yes"]'))
    ).click()

    # 2 possibilities, either failed or succeeded

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'bodytext'))
    )
    result = driver.find_element(By.XPATH, '//b[text()="Result:"]/../../../td[2]/span')
    print("Result: " + result.text)

    if result.text == "The course has been successfully added.":
        driver.find_element(By.XPATH, '//input[@value="Continue"]').click()
        return True

    else:
        reason = driver.find_element(By.XPATH, '//b[text()="Reason:"]/../../../td[2]/span')
        print("Reason: " + reason.text)
        driver.find_element(By.XPATH, '//input[@value="Continue"]').click()
        return False


try:
    print("Start Time =", datetime.now().strftime("%H:%M:%S"))
    # All courses have not been added successfully yet
    successful = False
    error = 0
    total_errors = 0

    while successful is False:
        for course in catalogue_numbers:

            available = False
            time.sleep(int(os.getenv('WAIT_TIME')))
            driver.get(vsb)

            try:

                fall_winter_24 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'term_2024102119'))
                )
                fall_winter_24.click()

                code_number = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'code_number')))
                code_number.send_keys(course)

                add_course_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'addCourseButton')))
                add_course_button.click()

                box_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//h4[@class="course_title"]')))
                title = box_element.get_attribute("innerText")
                element = driver.find_element(By.XPATH, '//span[text()="' + course + '"]/../../span[text()]')
                seats = element.get_attribute("innerText")
                time.sleep(1)

                # if we reached till here => no errors found => set error to 0
                error = 0

            except:
                total_errors += 1
                error += 1
                print('error: ', error)
                print("Current Time =", datetime.now().strftime("%H:%M:%S"))

                # if this is the first error, skip this round, maybe a page refresh will fix it
                if error == 1:
                    # do nothing
                    print('error == 1')

                # if refresh didn't solve the issue => login again probably required
                elif error == 2:
                    try:

                        print('Login again required')
                        driver.find_element(By.ID, 'mli').send_keys(username)
                        driver.find_element(By.ID, 'password').send_keys(password)
                        driver.find_element(By.NAME, 'dologin').click()
                        time.sleep(10)
                    except:
                        # if login again wasn't required => site under maintenance
                        print('except in error == 2')

                # website probably under maintenance, wait for 15 minutes
                else:
                    print('Site probably under maintenance')
                    print('This happens usually between 12 AM - 1 AM')
                    time.sleep(900)

                continue  # skip this round, go to the next element in the loop for a page refresh

            if seats == "Seats: Available":

                print('seats available!!! for ' + title)
                driver.get(rem)
                time.sleep(1)
                available = add_course(course)

                # if course could not be added using REM => wait 15 minutes before continuing
                if available is False:
                    print("Trying again in 15 minutes!")
                    print("Current Time =", datetime.now().strftime("%H:%M:%S"))
                    emailSender.send_email(title + ' is reserved')
                    time.sleep(900)

                # if course was added => remove from duplicate
                else:
                    emailSender.send_email(title + ' has been added successfully')
                    duplicate.remove(course)

        if duplicate:
            catalogue_numbers = copy.copy(duplicate)
        else:
            successful = True
            print('\nAll courses have been added successfully!')

finally:
    print("End Time =", datetime.now().strftime("%H:%M:%S"))
    # driver.close()
