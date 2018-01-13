# Scoring API
требования:
- python 2.7

запуск сервера:

```python api.py [--port\-p <порт default=8080>] [--log\-p <путь_до_лог_файла default=sys.stderr>]```

## Краткое описание:
API подсчета скора, в ответ на HTTP POST запрос пользователя с json-ом вида:

`{"account": "<имя компании партнера>", "login": "<имя пользователя>", "method": "<имя метода>",
"token": "<аутентификационный токен>", "arguments": {<словарь с аргументами вызываемого метода>}}`

возвращает ответ также в виде json:

OK:

```{"code": <числовой код>, "response": {<ответ вызываемого метода>}}```

Ошибка:

```{"code": <числовой код>, "error": {<сообщение об ошибке>}}```

## Методы
### online_score.
### Аргументы
- phone ‑ строка или число, длиной 11, начинается с 7, опционально, может быть пустым
- email ‑ строка, в которой есть @, опционально, может быть пустым
- first_name ‑ строка, опционально, может быть пустым
- last_name ‑ строка, опционально, может быть пустым
- birthday ‑ дата в формате DD.MM.YYYY, с которой прошло не больше 70 лет, опционально, может быть
пустым
- gender ‑ число 0, 1 или 2, опционально, может быть пустым

### Пример:

`$ curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score",
"token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e3",
"arguments": {"phone": "78001234567", "email": "user@domain", "first_name": "Имя", 
"last_name": "Фамилия", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/`

`{"code": 200, "response": {"score": 5.0}}`

### clients_interests.
### Аргументы
- client_ids ‑ массив числе, обязательно, не пустое
- date ‑ дата в формате DD.MM.YYYY, опционально, может быть пустым

### Пример:

`$ curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", 
"method": "clients_interests", "token": 
"d3573aff1555cd67dccf21b95fe8c4dc8732f33fd4e32461b7fe6a71d83c947688515e36774c00fb630b039fe2223c991f045
 "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/`
 
 `{"code": 200, "response": {"1": ["books", "hi-tech"], "2": ["pets", "tv"], "3": ["travel", "music"], 
"4": ["cinema", "geek"]}}`
