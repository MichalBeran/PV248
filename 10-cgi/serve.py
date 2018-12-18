#!/usr/bin/python3

import sys
import os
from aiohttp import web
import asyncio


directory = '/'


@asyncio.coroutine
async def handle_get_request(request):
    # asyncio.create_subprocess_shell()
    # os.popen()
    path = request.path
    system_path = directory + path
    if os.path.isfile(system_path):
        if system_path.endswith(".cgi"):
            if request.headers.get("Authorization") is None:
                auth_type = ''
            else:
                auth_type = request.headers.get("Authorization")

            if request.content_type is None:
                content_type = ''
            else:
                content_type = request.content_type

            for header in request.headers:
                header_name = header.upper().replace('-', '_')
                os.putenv('HTTP_' + header_name, request.headers[header])

            os.putenv('AUTH_TYPE', auth_type)
            os.putenv('CONTENT_TYPE', content_type)
            os.putenv('GATEWAY_INTERFACE', 'CGI/1.1')
            os.putenv('PATH_INFO', request.url.raw_path)
            os.putenv('QUERY_STRING', request.query_string)
            os.putenv('REMOTE_ADDR', '127.0.0.1')
            os.putenv("REQUEST_METHOD", request.method)
            os.putenv("SERVER_NAME", '127.0.0.1')
            os.putenv("SERVER_PORT", str(request.PORT))
            os.putenv("SERVER_PROTOCOL", 'HTTP/1.1')
            software = 'Python ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(
                sys.version_info[2])
            os.putenv("SCRIPT_NAME", os.path.basename(str(request.url)))
            os.putenv("SERVER_SOFTWARE", software)
            if request.content_length is not None:
                os.putenv('CONTENT_LENGTH', str(request.content_length))
            else:
                os.putenv('CONTENT_LENGTH', str(0))
            data = await asyncio.create_subprocess_shell(system_path, stdout=asyncio.subprocess.PIPE)
            output = await data.stdout.read()
            parsed = output.decode().split("\n\n")
            return web.Response(text=parsed[1])
        else:
            data = await asyncio.create_subprocess_shell("cat " + system_path, stdout=asyncio.subprocess.PIPE)
            output = await data.stdout.read()
            return web.Response(text=output.decode())
    elif os.path.isdir(system_path):
        return web.Response(text="only directory found", status=403)
    else:
        return web.Response(text="no file found", status=404)


@asyncio.coroutine
async def handle_post_request(request):
    path = request.path
    body = request.body
    system_path = directory + path
    if os.path.isfile(system_path):
        if system_path.endswith(".cgi"):
            if request.headers.get("Authorization") is None:
                auth_type = ''
            else:
                auth_type = request.headers.get("Authorization")

            if request.content_type is None:
                content_type = ''
            else:
                content_type = request.content_type
            os.putenv('AUTH_TYPE', auth_type)
            os.putenv('CONTENT_TYPE', content_type)
            os.putenv('GATEWAY_INTERFACE', 'CGI/1.1')
            os.putenv('PATH_INFO', request.url.raw_path)
            os.putenv('QUERY_STRING', request.query_string)
            os.putenv('REMOTE_ADDR', '127.0.0.1')
            os.putenv("REQUEST_METHOD", request.method)
            os.putenv("SERVER_NAME", '127.0.0.1')
            os.putenv("SERVER_PORT", str(request.PORT))
            os.putenv("SERVER_PROTOCOL", 'HTTP/1.1')
            software = 'Python ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(
                sys.version_info[2])
            os.putenv("SCRIPT_NAME", os.path.basename(str(request.url)))
            os.putenv("SERVER_SOFTWARE", software)
            if request.content_length is not None:
                os.putenv('CONTENT_LENGTH', str(request.content_length))
            else:
                os.putenv('CONTENT_LENGTH', str(0))
            data = await asyncio.create_subprocess_shell(system_path, stdin=body, stdout=asyncio.subprocess.PIPE)
            output = await data.stdout.read()
            parsed = output.decode().split("\n\n")
            return web.Response(text=parsed[1])
        else:
            data = await asyncio.create_subprocess_shell("cat " + system_path, stdout=asyncio.subprocess.PIPE)
            output = await data.stdout.read()
            return web.Response(text=output.decode())
    elif os.path.isdir(system_path):
        return web.Response(text="only directory found", status=403)
    else:
        return web.Response(text="no file found", status=404)


def aio_server(port):
    if sys.platform.startswith('win'):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    app = web.Application()
    app.router.add_route('GET', '/{tail:.*}', handle_get_request)
    app.router.add_route('POST', '/{tail:.*}', handle_post_request)
    web.run_app(app, host='localhost', port=port)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        directory = sys.argv[2]
        aio_server(int(sys.argv[1]))
    else:
        print("Wrong number of arguments")