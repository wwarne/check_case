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

# Регулярное выражение, которым будем проверять входящие данные
CHECKER = re.compile(r'[0-9]{2}.[0-9]{2}.[0-9]{4}')
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
    if CHECKER.search(data['test_date']):
        return web.Response(body=ANSWER_OK)
    else:
        return web.Response(body=ANSWER_ERR)

# Создаём сервер
app = web.Application()
# Добавляем обработчик запросов
app.router.add_route('POST', '/', handle_post)
# запускаем сервер на порту 9999.
# Сервер "Вежливо" выключается по Ctrl+C, отправив ответы на все запросы, которые в момент выключения успели поступить.
web.run_app(app, port=9999)
