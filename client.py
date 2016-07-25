import msgpack
import requests

# Адрес проверяющего сервера
CHECK_SERVER_URL = 'http://127.0.0.1:9999/'
# Вот у нас откуда-то есть список строк с датами, которые мы будем проверять.
dates_for_test = ['25.07.2016', '25.07.16']

for date in dates_for_test:
    print('Отправляем на проверку дату формата {}'.format(date))
    # Собираем структуру для отправки
    test_data = {'test_date': date}
    # Запаковываем msgpack'ом
    request_data = msgpack.packb(test_data)
    # И отсылаем на сервер. Заодно делаем простую проверку, на случай если сервер не работает.
    try:
        request_result = requests.post(CHECK_SERVER_URL, data=request_data)
    except requests.exceptions.RequestException:
        print('Не удалось связаться с сервером.')
        continue
    # Ещё отдельно проверим случай, когда сервер доступен, но возвращает код ошибки
    if request_result.status_code == 200:
        result = msgpack.unpackb(request_result.content, encoding='utf-8')
        print('Результат проверки: {}'.format(result))
    else:
        print('Во время обработки запроса произошла ошибка {} - {}'.format(request_result.status_code,
                                                                           request_result.reason))
