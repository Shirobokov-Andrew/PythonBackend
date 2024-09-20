import json
import math


async def app(scope, receive, send):
    if scope['type'] == 'http' and scope['method'] == 'GET':
        if scope['path'] == '/factorial':
            await factorial(scope, send)
        elif scope['path'].startswith('/fibonacci'):
            await fibonacci(scope, send)
        elif scope['path'].startswith('/mean'):
            await mean(receive, send)
        else:
            await send_answer(send, status_code=404, content_type=b'text/plain', body=b'404 Not Found')
    else:
        await send_answer(send, status_code=404, content_type=b'text/plain', body=b'404 Not Found')


async def send_answer(send,
                      status_code: int = 404,
                      content_type: bytes = b'text/plain',
                      body: bytes = b'404 Not Found',
                      ):
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', content_type)],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def factorial(scope, send):
    query_str = scope['query_string'].decode('utf-8')
    n = query_str.lstrip('n=')

    try:
        n = int(n)
    except ValueError:
        await send_answer(send, status_code=422, content_type=b'text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type=b'text/plain', body=b'400 Bad Request')
        return

    result = json.dumps({'result': math.factorial(n)}).encode('utf-8')
    await send_answer(send, status_code=200, content_type=b'application/json', body=result)


async def fibonacci(scope, send):
    n = scope['path'].lstrip('/fibonacci/')

    try:
        n = int(n)
    except ValueError:
        await send_answer(send, status_code=422, content_type=b'text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type=b'text/plain', body=b'400 Bad Request')
        return

    a, b = 1, 1
    for i in range(2, n):
        a, b = b, a + b

    if n == 0:
        b = 0

    result = json.dumps({"result": b}).encode('utf-8')
    await send_answer(send, status_code=200, content_type=b'application/json', body=result)


async def mean(receive, send):
    request = await receive()
    body = request['body']
    if len(body) == 0:
        await send_answer(send, status_code=422, content_type=b'text/plain', body=b'422 Unprocessable Entity')
        return

    numbers = json.loads(body)

    if isinstance(numbers, list):
        if not numbers:
            await send_answer(send, status_code=400, content_type=b'text/plain', body=b'400 Bad Request')
            return
        elif not all(isinstance(n, (float, int)) for n in numbers):
            await send_answer(send, status_code=404, content_type=b'text/plain', body=b'422 Unprocessable Entity')
            return
        else:
            mean_value = sum(numbers) / len(numbers)
            result = json.dumps({"result": mean_value}).encode('utf-8')
            await send_answer(send, status_code=200, content_type=b'application/json', body=result)
    else:
        await send_answer(send, status_code=404, content_type=b'text/plain', body=b'422 Unprocessable Entity')

