"""
Мини сервер с использованием asyncio.
Из-за нового синтаксиса async/await нужен python 3.5 для запуска

Получает запрос в формате MSGPACK,
Проверяет поле test_date на соответствие заданному формату
Отсылает результат проверки в формате msgpack
"""
import re
import msgpack
from aiohttp import web
from msgpack.exceptions import UnpackException

"""
Регулярное выражение, которым будем проверять входящие данные.
т.к. в условии сказано, что это дата в формате день, месяц, год, я решил проверять также и правильность даты.
иначе можно подать серверу дату в формате 12.31.2016 (месяц, день, год) и он скажет, что всё ок.
И на 99.99.9999 тоже сказал бы, что всё ок.
"""
CHECKER = re.compile(r'(?P<day>[0-9]{2}).(?P<month>[0-9]{2}).[0-9]{4}')
# И сразу сделаем две заготовки для ответов, чтобы каждый запрос не вызывать msgpack
ANSWER_OK = msgpack.packb({'result': 'ok'})
ANSWER_ERR = msgpack.packb({'result': 'error'})

async def handle_post(request):
    # получаем тело запроса
    data = await request.read()
    # разбираем msgpack. в случае если на сервер придёт "битое" сообщение, вернём 400-ю ошибку (BadRequest)
    try:
        data = msgpack.unpackb(data, encoding='utf-8')
    except UnpackException:
        return web.HTTPBadRequest()
    # проверяем правильность поля test_date и отсылаем нужный ответ
    check_result = CHECKER.search(data['test_date'])
    if check_result:
        # теперь дополнительно проверим, чтобы день был не больше 31, а месяц - не больше 12
        if int(check_result.group('day')) <= 31 and int(check_result.group('month')) <= 12:
            return web.Response(body=ANSWER_OK)
    return web.Response(body=ANSWER_ERR)

# Создаём сервер
app = web.Application()
# Добавляем обработчик запросов
app.router.add_route('POST', '/', handle_post)
# запускаем сервер на порту 9999.
# Сервер "Вежливо" выключается по Ctrl+C, отправив ответы на все запросы, которые в момент выключения успели поступить.
web.run_app(app, port=9999)
