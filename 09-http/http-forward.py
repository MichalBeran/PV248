#!/usr/bin/python3

import sys
import json
import ssl
import socket
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
        if str(k) in result.keys():
            result[str(k)] += ', ' + str(v)
        else:
            result[str(k)] = str(v)
    return result


def get_url(url_string, default_method='http'):
    result = urlparse(url_string, scheme=default_method)
    if result.netloc == '':
        result = urlparse('//' + url_string, scheme=default_method)
    return result.geturl()


# check if invalid or no cert at all - ex http
async def check_ssl(url_host, url_port):
    res_json = {}
    ssl_context = ssl.create_default_context()
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_REQUIRED
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.settimeout(timeout)
    wrappedSocket = ssl_context.wrap_socket(socket.socket(), server_hostname=url_host)
    try:
        wrappedSocket.connect((url_host, url_port))
    except ssl.CertificateError:
        # print('SSL CERT ERROR')
        res_json['certificate valid'] = False
    except ssl.SSLError as e:
        # print('SSL ERROR', e.filename, '|', e.filename2, '|', e.library, '|', e.strerror)
        return {}
    except Exception as e:
        # print('unknown ERROR', e)
        return {}

    cert = wrappedSocket.getpeercert()
    issued_to = []
    for altName in cert['subjectAltName']:
        issued_to.append(altName[1])
    res_json['certificate valid'] = True
    res_json['certificate for'] = issued_to
    wrappedSocket.close()
    return res_json


async def get_request(url, headers, req_timeout):
    res_json = {}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=req_timeout), connector=conn) as session:
        try:
            async with session.get(url=url, headers=headers, allow_redirects=True) as resp:
                res_json['code'] = resp.status
                res_json['headers'] = dict_parser(resp.headers)
                try:
                    res_json['json'] = await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    pass
                if 'json' not in res_json.keys():
                    res_json['content'] = await resp.text()
                try:
                    ssl_json = await check_ssl(resp.url.host, resp.url.port)
                    for key, value in ssl_json.items():
                        res_json[key] = value
                except Exception:
                    pass
        except asyncio.TimeoutError:
            res_json['code'] = 'timeout'
    return web.json_response(data=res_json)


async def post_request(url, headers, req_timeout, data_content):
    res_json = {}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=req_timeout), connector=conn) as session:
        try:
            async with session.post(url=url, headers=headers, data=data_content, allow_redirects=True) as resp:
                res_json['code'] = resp.status
                res_json['headers'] = dict_parser(resp.headers)
                try:
                    res_json['json'] = await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    pass
                if 'json' not in res_json.keys():
                    res_json['content'] = await resp.text()
                try:
                    ssl_json = await check_ssl(resp.url.host, resp.url.port)
                    for key, value in ssl_json.items():
                        res_json[key] = value
                except Exception:
                    pass
        except asyncio.TimeoutError:
            res_json['code'] = 'timeout'
    return web.json_response(data=res_json)


@asyncio.coroutine
async def handle_get(request):
    # print(request.headers)
    # print(await request.read())
    result = dict_parser(request.headers)
    del result['Host']
    # print('headers', result)
    url, https = get_url(upstream)
    response_result = await get_request(url=url, headers=result, req_timeout=default_timeout)
    return response_result


@asyncio.coroutine
async def handle_post(request):
    # print(request.headers)
    # print(request.method)
    # print('request', (await request.read()).decode())
    con = (await request.read()).decode()
    try:
        json_content = json.loads(con)
    except Exception:
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
    # print('content url', json_content['url'])
    # print(await request.read())
    url = get_url(json_content['url'])
    if json_content['type'] == 'GET':
        return await get_request(url, headers, timeout)
    elif json_content['type'] == 'POST':
        return await post_request(url, headers, timeout, json_content['content'])
    else:
        return web.Response(text="INVALID REQUEST", status=400)


def aio_server(port):
    app = web.Application()
    app.router.add_route('GET', '/{tail:.*}', handle_get)
    app.router.add_route('POST', '/{tail:.*}', handle_post)

    web.run_app(app, host='localhost', port=port)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        upstream = sys.argv[2]
        aio_server(int(sys.argv[1]))
    else:
        print("Wrong number of arguments")