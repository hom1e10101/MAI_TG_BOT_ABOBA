import json
import requests

# Ваш API-ключ от Yandex Cloud
API_Key = '<API_key>'

# URL для запроса к Yandex GPT API
url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

# Заголовки запроса
headers = {
    'Authorization': f'Api-Key {API_Key}',
    'Content-Type': 'application/json'
}

# Текст запроса (промт)
prompt = """
напиши мне на английском 5 лучших кафе Москвы в районе Сокола в формате json с их адресами и рейтингом
"""

# Тело запроса
data = {
    "modelUri": "gpt://<folderID>/yandexgpt",
    "generationOptions": {
        "maxTokens": 500,  # Максимальное количество токенов в ответе
        "temperature": 0.7  # Параметр креативности (от 0 до 1)
    },
    "completionOptions": {
        # "stream": "false",
        "temperature": 0.6,
        "maxTokens": "2000",
        "reasoningOptions": {
        "mode": "DISABLED"
        }
    },
    "messages": [
    {
      "role": "system",
      "text": prompt
    }
  ]
}


# Отправка POST-запроса
response = requests.post(url, headers=headers, json=data)

# Проверка статуса ответа
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print()
    text_response = result["result"]["alternatives"][0]["message"]["text"]
    print(text_response)
    # print(json.dumps(result, indent=4, ensure_ascii=False))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
