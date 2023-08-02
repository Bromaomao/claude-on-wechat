import requests
import json
import re
import time

class Claude:
  def __init__(self,org_uuid,con_uuid,cookie):
    self.org_uuid = org_uuid
    self.con_uuid = con_uuid
    self.cookie = cookie
  def send_message(self, query):
    url = "https://claude.ai/api/append_message"
    payload = json.dumps({
      "completion": {
        "prompt": query,
        "timezone": "Asia/Singapore",
        "model": "claude-2",
        "incremental": True
      },
      "organization_uuid": self.org_uuid,
      "conversation_uuid": self.con_uuid,
      "text": query,
      "attachments": []
    })
    headers = {
      'Accept': 'text/event-stream, text/event-stream',
      'Accept-language': 'zh-CN,zh',
      'Content-type': 'application/json',
      'Cookie': self.cookie,
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Referer': f'https://claude.ai/chat/{self.con_uuid}',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
      'TE': 'trailers'
    }

    try:
      response = requests.request("POST", url, headers=headers, data=payload,stream = True)
    except Exception as error:
      print(error)
      return False

    if len(response.text) >=60:
      return True
    return False

  def chat_conversation_history(self):
    url = f"https://claude.ai/api/organizations/{self.org_uuid}/chat_conversations/{self.con_uuid}"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        # "Accept-Encoding":"gzip, deflate, br",
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.request("GET", url, headers=headers)
    response.encoding = 'utf-8'
    return response.json()

def get_last_answer(history,cache):

  max_index = 0
  for i in history["chat_messages"]:
    if i["index"] > max_index:
      max_index = i["index"]
      body = i
  if max_index not in cache:
    cache.append(max_index)
    answer = body["text"]
    return answer,cache
  return None,cache

def main(org_uuid,con_uuid,cookie):

    claude = Claude(org_uuid, con_uuid,cookie)
    cache = []
    while True:
      query = input("human:")

      result = claude.send_message(query)
      if result:
        print("send success")
      else:
        continue

      try_time_current = 0

      #最大重试次数
      try_time_max = 5

      while True:

          history = claude.chat_conversation_history()
          # print(history)

          answer,cache = get_last_answer(history, cache)
          print("cache :" ,cache)
          if answer == None or answer == query:
            time.sleep(1)
            try_time_current += 1
            if try_time_current > try_time_max:
                answer = "消息获取失败"
                break
            continue

          else:
              break

      print("robot: ", answer)



if __name__ == '__main__':
    org_uuid= "3dd1bb7a-0f77-4f74-8261-c54ac5990c86"
    con_uuid= "ecc769bc-427b-466b-843c-1b7bf9b44295"
    cookie = "sessionKey=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; intercom-device-id-lupk8zyo=b37192f8-c3a5-408d-8525-60ad8c2cc57c; intercom-session-lupk8zyo=dEZVQTB1a20zQU4wS3YyMmlwV1gyN1RXVE9pcmVOWUhHOWp6Y3p3Y0k1YWtGM01Wc0N6ZW1iOUM1UFg3c1N3dC0tdjJyemxyQlFhOTNoZk9BRjNjaFhnUT09--bf0e6b06b07e08f83dbbd100632107f4f1347279; __cf_bm=zGAhp9yifa_bhBcwLqaug2ds.LTLiScAn1X2FjXnb5I-1690833261-0-AaCi1Jk/9x5rE3846W+OJYayvb6bvo0xvHo6/L7D08JyitQWJYGruxGV+gF+yPe77UO86Js5iEjPdp1LInA3CMQ="
    # claude = Claude(org_uuid, con_uuid,cookie)
    # history = claude.chat_conversation_history()
    # print(history)
    main(org_uuid,con_uuid,cookie)