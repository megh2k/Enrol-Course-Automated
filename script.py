from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time
import getpass
import copy

options = Options()
options.add_experimental_option('detach', True)

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

rem = "https://wrem.sis.yorku.ca/Apps/WebObjects/REM.woa/wa/DirectAction/rem"
vsb = 'https://schedulebuilder.yorku.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=0&sort' \
      '=none&filters=iiiiiiii&bbs=&ds=&cams=0_1_2_3_4_5_6_7_8&locs=any '

driver.get(vsb)

username = input("Username:")
password = getpass.getpass()
# enter all course catalogue numbers in form of string, each seperated by a comma
# eg: {'ABC', 'XYZ', '123'}

catalogue_numbers = {}
duplicate = copy.copy(catalogue_numbers)

driver.find_element(By.ID, 'mli').send_keys(username)
driver.find_element(By.ID, 'password').send_keys(password)
driver.find_element(By.NAME, 'dologin').click()


def add_course(catalogue_number):
    # Select Fall/Winter 24 from options, click Continue
    select = Select(driver.find_element(By.NAME, '5.5.1.27.1.11.0'))
    select.select_by_value('3')
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

    while successful is False:
        for course in catalogue_numbers:

            available = False
            driver.get(vsb)

            # if reloading page leads to sign up for York Account, autofill information and continue
            try:
                fall_winter_24 = WebDriverWait(driver, 120).until(
                    EC.presence_of_element_located((By.ID, 'term_2023102119'))
                )
                fall_winter_24.click()

            # York 2FA login required
            except:
                print('Login again required')
                print("Current Time =", datetime.now().strftime("%H:%M:%S"))
                driver.find_element(By.ID, 'mli').send_keys(username)
                driver.find_element(By.ID, 'password').send_keys(password)
                driver.find_element(By.NAME, 'dologin').click()
                fall_winter_24 = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, 'term_2023102119'))
                )
                fall_winter_24.click()

            driver.find_element(By.ID, 'code_number').send_keys(course)
            driver.find_element(By.ID, 'addCourseButton').click()

            time.sleep(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[text()="' + course + '"]/../../span[text()]'))
            )

            element = driver.find_element(By.XPATH,
                                          '//span[text()="' + course + '"]/../../span[text()]')

            title = driver.find_element(By.XPATH, '//h4[@class="course_title"]').text
            print('\n'+title)
            if element.text == "Seats: Available":

                print('seats available!!!')
                driver.get(rem)
                time.sleep(1)
                available = add_course(course)

                # if course could not be added using REM => wait 15 minutes before continuing
                if available is False:
                    print("Trying again in 15 minutes!")
                    print("Current Time =", datetime.now().strftime("%H:%M:%S"))
                    time.sleep(900)

                # if course was added => remove from duplicate
                else:
                    duplicate.remove(course)
            else:
                print('seats not available :(')

        if duplicate:
            catalogue_numbers = copy.copy(duplicate)
        else:
            successful = True
            print('\nAll courses have been added successfully!')

finally:
    print("End Time =", datetime.now().strftime("%H:%M:%S"))
    driver.close()
