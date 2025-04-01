import boto3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs
import time
import argparse
import json

def upload_cafe24(access_token, id, category, image_url):
  print(f"id: {id}, category: {category}, image_url: {image_url}")
  try:
    post_url = "https://suraktantan.cafe24api.com/api/v2/admin/boards/9/articles"
    headers = {
      "Authorization": f"Bearer {access_token}",
      "Content-Type": "application/json",
      "X-Cafe24-Api-Version": "2025-03-01"
    }

    if category == "7":
      post_data = {
        "shop_no": 1,
        "requests": [
          {
            "writer": id,
            "title": "Re(we)탄탄 챌린지 도전!",
            "content": "contents",
            "client_ip": "127.0.0.1",
            "secret": "T",
            "member_id": id,
            "reply_user_id": "admin",
            "reply_status": "N",
            "board_category_no": int(category),
            "category_no": int(category),
            "attach_file_urls": [
                {
                    "name": image_url.split('/')[-1],
                    "url": image_url
                }
            ]
          }
        ]
      }
    else:
      post_data = {
        "shop_no": 1,
        "requests": [
          {
            "writer": id,
            "title": "하루탄탄 챌린지 도전!",
            "content": "contents",
            "client_ip": "127.0.0.1",
            "secret": "T",
            "member_id": id,
            "reply_user_id": "admin",
            "reply_status": "N",
            "board_category_no": int(category),
            "category_no": int(category),
            "attach_file_urls": [
                {
                    "name": image_url.split('/')[-1],
                    "url": image_url
                }
            ]
          }
        ]
      }

    json_data = json.dumps(post_data)

    post_response = requests.post(post_url, headers=headers, data=json_data)
    post_response.raise_for_status()
    post_response_data = post_response.json()
    print(f"Post response: {post_response_data}")

  except requests.exceptions.RequestException as e:
    print(f"HTTP 요청 에러 발생: {e}")

  except json.JSONDecodeError as e:
    print(f"JSON 디코딩 에러 발생: {e}")
    if 'post_response' in locals():
      if hasattr(post_response, 'text'):
        print(f"게시글 작성 응답 내용 (JSON 디코딩 에러 분석): {post_response.text}")


def get_access_token(code):
  api_endpoint = "https://suraktantan.cafe24api.com/api/v2/oauth/token"

  headers = {
    "Authorization": "Basic dDhyY1hsVFVCUnl2eWRWT1JGR0o4QTpuc0RFc0FLWU9OMnVRd0NvZzVleFdG",
    "Content-Type": "application/x-www-form-urlencoded"
  }

  data = {
    "grant_type": "authorization_code",
    "code": code.strip(),
    "redirect_uri": "https://suraktantan.cafe24.com/board/consult/list.html"
  }

  try:
    response = requests.post(api_endpoint, headers=headers, data=data)
    response.raise_for_status()
    token_data = response.json()
    access_token = token_data.get('access_token')

    return access_token

  except requests.exceptions.RequestException as e:
    print(f"토큰 요청 에러 발생: {e}")
    return None


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_auth_code(driver, id, category, image_url):
  try:
    target_url = "https://eclogin.cafe24.com/Shop/"
    driver.get(target_url)
    time.sleep(2)

    driver.find_element(By.ID, "mall_id").send_keys("suraktantan")
    time.sleep(0.5)
    driver.find_element(By.ID, "userpasswd").send_keys("b9347711")
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, "button.btnStrong.large").click()
    time.sleep(3)

    url = "https://suraktantan.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id=t8rcXlTUBRyvydVORFGJ8A&state=stth_img&redirect_uri=https://suraktantan.cafe24.com/board/consult/list.html&scope=mall.read_community,mall.write_community"
    driver.get(url)
    time.sleep(3)

    final_url = driver.current_url
    # print("Redirected URL:", final_url)

    query_params = parse_qs(urlparse(final_url).query)
    code = query_params.get("code", [""])[0]
    print("Authorization Code:", code)

    access_token = get_access_token(code)
    print("Access Token:", access_token)
    
    upload_cafe24(access_token, id, category, image_url)

  finally:
    driver.quit()

def main():
  parser = argparse.ArgumentParser(description='Cafe24 API')
  parser.add_argument('--id', type=str, required=True, help='id')
  parser.add_argument('--category', type=str, required=True, help='category')
  parser.add_argument('--image_url', type=str, required=True, help='image_url')
  args = parser.parse_args()

  driver = create_driver()
  try:
    get_auth_code(driver, args.id, args.category, args.image_url)
  except Exception as e:
    print(f"❌ Error: {str(e)}")
  finally:
    driver.quit()

if __name__ == "__main__":
  main()
