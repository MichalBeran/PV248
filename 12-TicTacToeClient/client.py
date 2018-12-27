#!/usr/bin/python3

import sys
import aiohttp
import asyncio


class GameInfo:
    def __init__(self):
        self.host = 'localhost'
        self.port = 9001
        self.selected_game_id = None
        self.selected_player = None
        self.next_player = None
        self.winner = None
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.player_waiting = False

    def reset_game(self):
        self.selected_game_id = None
        self.selected_player = None
        self.winner = None
        self.next_player = None
        self.player_waiting = False


game_info = GameInfo()


def run_in_foreground(task, *, loop=None):
    if loop is None:
        if sys.platform.startswith('win'):
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()
    return loop.run_until_complete(asyncio.ensure_future(task, loop=loop))


def sync_wait(task, loop=None):
    if loop is None:
        if sys.platform.startswith('win'):
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()
    return loop.run_until_complete(task)


@asyncio.coroutine
async def draw_board():
    global game_info
    await get_status()
    if len(game_info.board) > 0:
        for i in range(0, len(game_info.board)):
            for j in range(0, len(game_info.board[0])):
                if game_info.board[i][j] == 1:
                    print('X', end='')
                elif game_info.board[i][j] == 2:
                    print('O', end='')
                else:
                    print('_', end='')
            print(end='\n')
        await asyncio.sleep(1)
    if game_info.next_player != game_info.selected_player:
        if not game_info.player_waiting:
            print('waiting for other player')
            game_info.player_waiting = True
    else:
        game_info.player_waiting = False


async def get_status():
    global game_info
    result = await call_status()
    if result is not None:
        try:
            game_info.board = result['board']
        except Exception:
            pass
        try:
            game_info.next_player = result['next']
        except Exception:
            pass
        try:
            game_info.winner = result['winner']
        except Exception:
            pass


async def call_status():
    global game_info
    url = 'http://' + game_info.host + ':' + str(game_info.port) + '/status?game=' + str(game_info.selected_game_id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url) as resp:
                try:
                    result = await resp.json()
                    return result
                except Exception as e:
                    # print(e, 'draw', resp.status, str(game_info.selected_game_id))
                    return None
        except Exception as e:
            return None


@asyncio.coroutine
async def join_to_game(input_id):
    global game_info
    url = 'http://' + game_info.host + ':' + str(game_info.port) + '/status?game=' + str(input_id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url) as resp:
                if resp.status == 200:
                    game_info.selected_game_id = input_id
                    game_info.selected_player = 2
                try:
                    json = await resp.json()
                    error = json['error']
                    return error
                except Exception:
                    pass
                return None
        except Exception as e:
            game_info.selected_game_id = None
            game_info.selected_player = None
            return None


async def start_new_game(name):
    global game_info
    json = await start_game_request(name)
    game_info.selected_player = 1
    game_info.selected_game_id = json['id']


async def start_game_request(name):
    global game_info
    url = 'http://' + game_info.host + ':' + str(game_info.port) + '/start?name=' + str(name)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url) as resp:
                if resp.status == 200:
                    try:
                        return await resp.json()
                    except:
                        pass
        except Exception as e:
            print(e)


async def get_games():
    global game_info
    url = 'http://' + game_info.host + ':' + str(game_info.port) + '/list'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url) as resp:
                # print(await resp.json())
                return await resp.json()
        except Exception as e:
            print(e)
            return []


async def make_move(x, y):
    global game_info
    json = await make_move_request(x, y)
    if json is not None:
        if not json['status'] == 'ok':
            print(json['message'])


async def make_move_request(x, y):
    global game_info
    url = 'http://' + game_info.host + ':' + str(game_info.port) + '/play?game=' + str(game_info.selected_game_id) + '&player=' + str(game_info.selected_player) + '&x=' + str(x) + '&y=' + str(y)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url) as resp:
                if resp.status == 200:
                    try:
                        return await resp.json()
                    except:
                        pass
        except Exception as e:
            print(e)


async def text_loop():
    global game_info
    while game_info.selected_game_id is None:
        try:
            games = await get_games()
            print('Type new to start a new game or type id of selected game to join')
            if len(games) > 0:
                print('Select game to join:')
                for item in games:
                    print(str(item['id']) + ' ' + item['name'])
            else:
                print('no games to join')
            input_string = input()
            input_array = input_string.split(' ')
            if input_array[0] == 'new':
                if len(input_array) > 1:
                    name = ' '.join('%s' % item for item in input_array[1:])
                    await start_new_game(name)
                else:
                    await start_new_game('')
            else:
                if len([item for item in games if str(item['id']) == input_string]) > 0:
                    resp = await join_to_game(input_string)
                    if resp is not None:
                        print(resp)
                else:
                    print('This game is not listed')
            # run_in_foreground(draw_board())
            while game_info.selected_game_id is not None:
                try:
                    await draw_board()
                    # asyncio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)
                    if game_info.winner is not None:
                        if game_info.winner != 0:
                            if game_info.selected_player == game_info.winner:
                                print('you win')
                            else:
                                print("you lose")
                        else:
                            print('draw')
                        game_info.reset_game()
                    elif game_info.next_player == game_info.selected_player:
                        if game_info.selected_player == 1:
                            game_symbol = 'X'
                        else:
                            game_symbol = 'O'
                        input_string = input('your turn (' + game_symbol + ')')
                        # input_string = await ainput('your turn (' + game_symbol + ')')
                        array = input_string.split(' ')
                        if len(array) == 2:
                            await make_move(array[0], array[1])
                        else:
                            print('cannot read x and y. Write two coordinates separated by space.')
                    await asyncio.sleep(1)
                except KeyboardInterrupt:
                    exit(0)
        except KeyboardInterrupt:
            exit(0)


def text_ui():
    if sys.platform.startswith('win'):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    loop.create_task(text_loop())
    # loop.create_task(draw_board())
    loop.run_forever()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        game_info.host = (sys.argv[1])
        game_info.port = (sys.argv[2])
        text_ui()
    else:
        print("Wrong number of arguments")