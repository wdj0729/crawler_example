from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import *
import pickle
from selenium.common.exceptions import *

path = "./chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")

# UserAgent값을 바꿔줍시다!
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

driver = webdriver.Chrome(path)
driver.maximize_window()

driver.implicitly_wait(3)

# 셰어킴 홈페이지
driver.get("https://sharekim.com/search?location=37.60747912093436,126.9543820360534,9&category=[1]")

# 무한 스크롤
houselist_str = """document.body.getElementsByClassName("house-list-wrap")[0].scrollTop = document.body.getElementsByClassName("house-list-wrap")[0].scrollHeight"""

while True:
    wrap_elem = driver.find_element_by_xpath("""//*[@id="root"]/div[3]/div[2]/div[1]/div[2]""")
    initial_wrap_height = wrap_elem.size['height']

    driver.execute_script(houselist_str)

    sleep(0.5)

    after_exec_wrap_height = wrap_elem.size['height']

    if initial_wrap_height == after_exec_wrap_height:
        break

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

house_list_warp_elem = driver.find_element_by_xpath("""//*[@id="root"]/div[3]/div[2]/div[1]/div[2]""")
house_lists_elem = house_list_warp_elem.find_elements_by_tag_name("a")

detail_link_list = []

for house in house_lists_elem:
    detail_link_list.append(house.get_property("href"))
    
# 중복 제거
detail_link_list = list(set(detail_link_list))

# content 담은 리스트 
data_list = []

#인덱스
i=1

for item in detail_link_list:
    print("주소:",item)
    print("인덱스:",i)

    driver2 = webdriver.Chrome(path,options=options)
    driver2.maximize_window()

    driver2.implicitly_wait(3)
    # 셰어킴 상세페이지
    driver2.get(item)

    while True:
        # Scroll down to bottom                               
        driver2.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        sleep(0.5)
                                            
        break

    # 매물 정보
    try: 
        product_info = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[1]/div[1]/section[1]""")
        product_info_data = product_info.text.strip()
    except NoSuchElementException:
        pass
    # 하우스 정보
    try: 
        house_info = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[1]/div[1]/section[2]""")
        house_info_data = house_info.text.strip()
    except NoSuchElementException:
        pass
    # 상세 정보
    try:
        detail_info = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[1]/div[1]/div[2]""")
        detail_info_data = detail_info.text.strip()
    except NoSuchElementException:
        pass
    # 공간 정보
    try:
        option_info = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[1]/div[1]/section[4]""")
        option_info_data = option_info.text.strip()
    except NoSuchElementException:
        pass
    # 입주 상담
    try:
        price = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[2]/div[1]/section[1]""")
        price_data = price.text.strip()
    except NoSuchElementException:
        pass
    # 입지 정보
    try:
        address = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[2]/div[1]/section[2]""")
        address_data = address.text.strip()
    except NoSuchElementException:
        pass
    # 공인중개사 연락처
    try:
        phone = driver2.find_element_by_xpath("""//*[@id="blur-wrap"]/div[3]/div[1]/div[2]/div/div[1]/div[2]/div/div[1]""")
        phone_data = phone.text.strip()
    except NoSuchElementException:
        pass

     # 딕셔너리에 데이터(리스트 형태)로 저장
    dic = {"매물 정보": product_info_data,"하우스 정보": house_info_data,"상세 정보": detail_info_data,"공간 정보": option_info_data,
             "입주 상담": price_data,"입지 정보": address_data,"공인 중개사 연락처": phone_data}
    # print("딕셔너리 :", dic)

    # 리스트에 딕셔너리 저장
    data_list.append(dic)

    i+=1

    driver2.close()

# 브라우저 종료
driver.close()

# 파일 쓰기
with open("sharekim_detail.pickle","wb") as fw:
    pickle.dump(data_list, fw)