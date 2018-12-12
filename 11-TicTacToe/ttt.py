#!/usr/bin/python3

import sys
from aiohttp import web
import asyncio


class RunningGames:
    def __init__(self):
        self.games = {}

    def new_game(self, name):
        game_id = len(self.games.keys())
        if game_id not in self.games.keys():
            self.games[game_id] = (str(name), GameBoard())
            return game_id
        else:
            return None

    def get_game_by_id(self, game_id):
        try:
            return self.games[game_id][1]
        except Exception:
            return None

    def get_list(self):
        output = []
        for key, value in self.games.items():
            if value[1].waiting_for_player:
                dict = {}
                dict['id'] = int(key)
                dict['name'] = value[0]
                output.append(dict)
        return output


class GameBoard:
    def __init__(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.next = 1
        self.locked = False
        self.winner = None
        self.waiting_for_player = True

    def lock_n_move(self, player, x, y):
        if not self.locked:
            self.locked = True
            result = self.make_move(player, x, y)
            self.locked = False
            return result
        else:
            return False

    def make_move(self, player, x, y):
            if int(player) != self.next:
                return False, "Next player should be " + str(self.next)
            elif self.winner is not None:
                return False, "Game is over"
            else:
                if int(x) > len(self.board[0]) - 1 or int(y) > len(self.board) - 1:
                    return False, "Out of range"
                else:
                    if self.board[int(x)][int(y)] == 0:
                        self.board[int(x)][int(y)] = int(player)
                        if int(player) == 2:
                            self.waiting_for_player = False
                        if self.player_win_check(player):
                            self.winner = int(player)
                        elif not self.another_move_is_possible():
                            self.winner = 0
                        self.next = (int(player) %2) + 1
                        return True, None
                    else:
                        return False, "Field is already taken"

    def player_win_check(self, player):
        player = int(player)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.board[i][j] == player:
                    if (self.board[i][0] == player and self.board[i][1] == player and self.board[i][2] == player) or (self.board[0][j] == player and self.board[1][j] == player and self.board[2][j] == player):
                        return True
        if(self.board[0][0] == player and self.board[1][1] == player and self.board[2][2] == player) or (self.board[0][2] == player and self.board[1][1] == player and self.board[2][0] == player):
            return True
        return False

    def another_move_is_possible(self):
        i = 0
        j = 0
        for i in range(0, 3):
            for j in range(0, 3):
                if self.board[i][j] == 0:
                    return True
        return False

    def get_winner(self):
        return self.winner

    def get_status(self):
        if self.winner is None:
            return self.board, self.next
        else:
            return self.board, self.winner


allGames = RunningGames()


@asyncio.coroutine
async def handle_start(request):
    # print("start")
    try:
        name = request.query['name']
    except Exception:
        name = ''
        # error = {}
        # error['error'] = 'request does not contain name parameter'
        # return web.json_response(status=404, data=error)
    json = {}
    json['id'] = int(allGames.new_game(name))
    return web.json_response(status=200, data=json)


@asyncio.coroutine
async def handle_status(request):
    # print("status")
    try:
        game_id = request.query['game']
    except Exception:
        error = {}
        error['error'] = 'request does not contain game parameter'
        return web.json_response(status=404, data=error)
    try:
        int(game_id)
    except Exception:
        error = {}
        error['error'] = 'cannot parse game id'
        return web.json_response(status=400, data=error)
    json = {}
    game = allGames.get_game_by_id(int(game_id))
    if game is None:
        error = {}
        error['error'] = 'No game with id ' + str(game_id)
        return web.json_response(status=400, data=error)
    if game.get_winner() is None:
        json['board'], json['next'] = game.get_status()
    else:
        json['board'], json['winner'] = game.get_status()
    return web.json_response(status=200, data=json)


@asyncio.coroutine
async def handle_play(request):
    # print("play")
    try:
        game_id = request.query['game']
        player = request.query['player']
        x = request.query['x']
        y = request.query['y']
    except Exception:
        error = {}
        error['error'] = 'request does not contain game, player or coordinates parameters'
        return web.json_response(status=400, data=error)
    try:
        int(game_id)
        int(player)
        int(x)
        int(y)
    except Exception:
        error = {}
        error['error'] = 'cannot parse game id, player or coordinates integers'
        return web.json_response(status=400, data=error)
    game = allGames.get_game_by_id(int(game_id))
    if game is None:
        error = {}
        error['error'] = 'No game with id ' + str(game_id)
        return web.json_response(status=400, data=error)
    json = {}
    success, message = game.make_move(player, int(x), int(y))
    if success:
        json['status'] = "ok"
    else:
        json['status'] = 'bad'
        json['message'] = message
    return web.json_response(status=200, data=json)


@asyncio.coroutine
async def handle_list(request):
    # print("list")
    list = allGames.get_list()
    return web.json_response(status=200, data=list)


def aio_server(port):
    app = web.Application()
    app.router.add_route('GET', '/start{tail:.*}', handle_start)
    app.router.add_route('GET', '/status{tail:.*}', handle_status)
    app.router.add_route('GET', '/play{tail:.*}', handle_play)
    app.router.add_route('GET', '/list{tail:.*}', handle_list)
    web.run_app(app, host='localhost', port=port)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        aio_server(int(sys.argv[1]))
    else:
        print("Wrong number of arguments")