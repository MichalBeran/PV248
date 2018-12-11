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
    query = request.query_string
    os.putenv("QUERY_STRING", str(query))
    system_path = directory + path
    if os.path.isfile(system_path):
        if system_path.endswith(".cgi"):
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