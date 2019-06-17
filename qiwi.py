import requests
import json
import time
# PRIVATE KEY
api_access_token = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImY3M3htZy0wMCIsInVzZXJfaWQiOiI3OTMxOTc5MjIzOCIsInNlY3JldCI6ImE5NjY4OWE4OTJhZjczYzE2MTdiODdhZGE5MzM3MGE4NTVkYzYyYzJlZjc4ZjU5MzY0Nzg5ZjY4N2JkZTIxYjkifX0='
# qiwi kassa api https://developer.qiwi.com/ru/bill-payments/?shell#api-qiwi-
s = requests.Session()
s.headers['authorization'] = 'Bearer ' + api_access_token
timestamp = int(time.time())

# Выставление счета
val = format(10.0, '.2f')
bill_id = str(timestamp * 1000)
app_json_props = {
    "amount": {
        "currency": "RUB",
        "value": val
    },
    "comment": "Test",
    "expirationDateTime": "2019-06-15T14:30:00+03:00",
    "customer": {
        "phone": "+79319792238",
        "email": "kirill98s@bk.ru"
    },
    "customFields": {}
}
# customer - на какой киви переводить деньги
h1 = s.put('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id, json=app_json_props)
print(json.loads(h1.text))
print()

# Уведомеления об оплате счетов (нужен сервер для уведомлений!)


# Проверка статуса оплаты счета
h3 = s.get('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id)
print(json.loads(h3.text))
print()

# Отмена неоплаченного счета
h4 = s.post('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id + '/reject')
print(json.loads(h4.text))
print()

# Возврат средств
app_json_refund = {
    "amount": {
        "currency": "RUB",
        "value": 1
    }
}
refund_id = str(timestamp * 1011)
h5 = s.get('https://api.qiwi.com/partner/bill/v1/bills/' + bill_id + '/refunds/'+refund_id, json=app_json_refund)
print(json.loads(h5.text))
print()

# Статус возврата
h6 = s.get('https://api.qiwi.com/partner/bill/v1/bills/'+bill_id+'/refunds/'+refund_id)
print(json.loads(h6.text))
print()
