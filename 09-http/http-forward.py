#!/usr/bin/python3

import sys
import json
import ssl
import aiohttp
from aiohttp import web
import asyncio
from urllib.parse import urlparse


upstream = '127.0.0.1'
default_timeout = 1


def return_invalid_json():
    result_json = {}
    result_json['code'] = 'invalid json'
    return web.json_response(data=result_json)

def dict_parser(multi_dict):
    result = {}
    for k, v in multi_dict.items():
        result[str(k)] = str(v)
    return result


def get_url(url_string, default_method='http'):
    result = urlparse(url_string, scheme=default_method)
    if result.netloc == '':
        result = urlparse('//' + url_string, scheme=default_method)
    return result.geturl()


async def check_ssl(url, headers):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    conn = aiohttp.TCPConnector(ssl_context=ssl_context)
    res_json = {}

    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.head(url=url, headers=headers, allow_redirects=True) as resp:
                print(resp)
                print(resp.status)
                print(resp.headers)
                print((await resp.text()).encode())
        except asyncio.TimeoutError:
            res_json['code'] = 'timeout'
        except ssl.SSLError:
            res_json['valid'] = False
    return res_json
    # res = http.client.HTTPSConnection(host=url, port=443, context = ssl_context)
    #
    # print(res._check_hostname)
    # print('check', res)


async def get_request(url, headers, req_timeout, verify_ssl):
    res_json = {}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=req_timeout), connector=conn) as session:
        try:
            async with session.get(url=url, headers=headers, allow_redirects=True) as resp:
                print(resp)
                print(resp.status)
                print(resp.headers)
                print((await resp.text()).encode())
                res_json['code'] = resp.status
                res_json['headers'] = dict_parser(resp.headers)
                try:
                    res_json['json'] = await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    pass
                if 'json' not in res_json.keys():
                    res_json['content'] = (await resp.read()).decode()
        except asyncio.TimeoutError:
            res_json['code'] = 'timeout'
    return web.json_response(data=res_json)


async def post_request(url, headers, req_timeout, data_content):
    res_json = {}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=req_timeout), connector=conn) as session:
        try:
            async with session.post(url=url, headers=headers, data=data_content, allow_redirects=True) as resp:
                print(resp)
                print(resp.status)
                print(resp.headers)
                res_json['code'] = resp.status
                res_json['headers'] = dict_parser(resp.headers)
                res_content = (await resp.read()).decode()
                try:
                    res_json['json'] = await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    pass
                if 'json' not in res_json.keys():
                    res_json['content'] = (await resp.read()).decode()
        except asyncio.TimeoutError:
            res_json['code'] = 'timeout'
    return web.json_response(data=res_json)


@asyncio.coroutine
async def handle_get(request):
    print(request.headers)
    print(await request.read())
    result = dict_parser(request.headers)
    print(result)
    del result['Host']
    print('headers', result)
    print('url:', get_url(upstream))
    response_result = await get_request(url=get_url(upstream), headers=result, req_timeout=default_timeout, verify_ssl=False)
    return response_result


@asyncio.coroutine
async def handle_post(request):
    print(request.headers)
    print(request.method)
    print('request', (await request.read()).decode())
    con = (await request.read()).decode()
    try:
        json_content = json.loads(con)
    except json.decoder.JSONDecodeError:
        return return_invalid_json()

    if "type" not in json_content:
        return return_invalid_json()
    elif json_content['type'] != 'GET' and json_content['type'] != 'POST':
        return return_invalid_json()
    if "url" not in json_content:
        return return_invalid_json()
    if json_content['type'] == 'POST':
        if "content" not in json_content:
            return return_invalid_json()
    if "headers" not in json_content:
        headers = {}
        headers['Accept'] = '*/*'
    else:
        headers = json_content['headers']
    if "timeout" not in json_content:
        timeout = default_timeout
    else:
        timeout = json_content['timeout']
    print('content url', json_content['url'])
    print(await request.read())
    url = get_url(json_content['url'])
    print("parsed url", url)
    verify_ssl = False
    # if url.scheme == 'https':
    #     verify_ssl = True
    #     await check_ssl(content['url'], None)
    if json_content['type'] == 'GET':
        return await get_request(url, headers, timeout, verify_ssl=False)
    elif json_content['type'] == 'POST':
        return await post_request(url, headers, timeout, json_content['content'])
    else:
        return web.Response(text="INVALID REQUEST", status=400)


def aio_server(port):
    app = web.Application()
    app.router.add_route('GET', '/', handle_get)
    app.router.add_route('POST', '/', handle_post)

    # loop = asyncio.get_event_loop()
    # f = loop.create_server(app.make_handler(), '127.0.0.1', port)
    # srv = loop.run_until_complete(f)
    # print('serving on', srv.sockets[0].getsockname())
    # try:
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     pass

    web.run_app(app, host='localhost', port=port)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        upstream = sys.argv[2]
        aio_server(int(sys.argv[1]))
    else:
        print("Wrong number of arguments")