#!/usr/bin/python3

import sys
import aiohttp
import asyncio
import pygame
from pygame.locals import *


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

##################### PYGAME #####################


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = pygame.font.Font(None, 24).render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.update()
                # Re-render the text.
                # self.txt_surface = pygame.font.Font(None, 24).render(self.text, True, self.color)
        return None

    def update(self):
        # Resize the text and box if the text is too long.
        if len(self.text) > 22:
            self.txt_surface = pygame.font.Font(None, 24).render('...' + self.text[-20:], True, self.color)
        else:
            self.txt_surface = pygame.font.Font(None, 24).render(self.text, True, self.color)
        width = max(275, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


def gui_init_menu(game):
    background = pygame.Surface(game.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    return background


def gui_click_menu(game, game_list):
    global game_info
    # games = sync_wait(get_games())
    (mouseX, mouseY) = pygame.mouse.get_pos()
    index = get_button_clicked(mouseX, mouseY)
    if index is not None:
        if index < 0:
            # sync_wait(start_new_game('new'))
            gui_new_game_loop(game)
        else:
            if index < len(game_list):
                sync_wait(join_to_game(game_list[index]['id']))


def get_button_clicked(mouseX, mouseY):
    if mouseX > 10 and mouseX < 280:
        # button_index = int((mouseY - 10) / 30)
        # print(button_index)
        # return button_index - 1
        for i in range(0, 11):
            if (mouseY > (30 * i) + 10) and (mouseY < (30 * i) + 30):
                return i - 1
    return None


def draw_button(game, position, text, button_color, text_color):
    pygame.draw.rect(game, button_color, (10, position, 280, 20))
    font = pygame.font.Font(None, 24)
    button_text = font.render(text, 1, text_color)
    game.blit(button_text, (25, position + 3))


def gui_show_menu(game, menu, game_list):
    menu.fill((250, 250, 250), (0, 300, 300, 25))
    game.blit(menu, (0,0))
    # games = sync_wait(get_games())
    draw_button(game, 10, 'start a new game', (77, 77, 77), (250, 250, 250))

    for index in range(0, len(game_list)):
        position = (30 * index) + 40
        draw_button(game, position, str(game_list[index]['id']) + ' - ' + str(game_list[index]['name']), (0, 0, 240),(250, 250, 250))
    pygame.display.flip()


def gui_new_game_loop(game):
    running = True
    text_input = InputBox(10, 60, 280, 30)
    while running:
        for menu_event in pygame.event.get():
            if menu_event.type is QUIT:
                exit(0)
            elif menu_event.type is MOUSEBUTTONDOWN:
                clicked = gui_click_new_game_menu()
                if clicked == 1:
                    running = False
                if clicked == 2:
                    sync_wait(start_new_game(text_input.text))
                    running = False
            input_response = text_input.handle_event(menu_event)
            if input_response is not None:
                sync_wait(start_new_game(text_input.text))
                running = False
        text_input.update()
        gui_show_new_game_menu(game, text_input)


def gui_show_new_game_menu(game, text_input):
    background_colour = (250, 250, 250)
    game.fill(background_colour)
    font = pygame.font.Font(None, 24)
    text_input.draw(game)
    pygame.draw.rect(game, (77, 77, 77), (10, 100, 130, 20))
    button_text = font.render('CANCEL', 1, (250, 250, 250))
    game.blit(button_text, (40, 103))
    pygame.draw.rect(game, (77, 77, 77), (155, 100, 130, 20))
    button_text = font.render('OK', 1, (250, 250, 250))
    game.blit(button_text, (205, 103))
    pygame.display.flip()


def gui_click_new_game_menu():
    (mouseX, mouseY) = pygame.mouse.get_pos()
    if (mouseX > 10) and (mouseX < 130) and (mouseY > 100) and (mouseY < 120):
        return 1
    if (mouseX > 155) and (mouseX < 285) and (mouseY > 100) and (mouseY < 120):
        return 2
    return 0


def gui_init_board(game):
    background = pygame.Surface(game.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # vertical lines...
    pygame.draw.line(background, (0, 0, 0), (100, 0), (100, 300), 2)
    pygame.draw.line(background, (0, 0, 0), (200, 0), (200, 300), 2)

    # horizontal lines...
    pygame.draw.line(background, (0, 0, 0), (0, 100), (300, 100), 2)
    pygame.draw.line(background, (0, 0, 0), (0, 200), (300, 200), 2)

    return background


def gui_draw_status(board):
    global game_info
    sync_wait(get_status())
    if game_info.winner is None:
        if game_info.selected_player == game_info.next_player:
            message = 'your turn'
        else:
            message = 'opponent\'s turn'
    else:
        if game_info.winner != 0:
            if game_info.selected_player == game_info.winner:
                message = 'you win'
            else:
                message = 'you lose'
        else:
            message = 'draw'

    # render the status message
    font = pygame.font.Font(None, 24)
    text = font.render(message, 1, (10, 10, 10))

    # copy the rendered message onto the board
    board.fill((250, 250, 250), (0, 300, 300, 25))
    board.blit(text, (10, 300))

    if len(game_info.board) > 0:
        for i in range(0, len(game_info.board)):
            for j in range(0, len(game_info.board[0])):
                draw_symbol(board, i, j, game_info.board[i][j])


def draw_symbol(board, boardRow, boardCol, player):
    # center of the square
    centerX = (boardCol * 100) + 50
    centerY = (boardRow * 100) + 50

    if player == 1:
        # cross
        pygame.draw.line(board, (0, 0, 0), (centerX - 22, centerY - 22), (centerX + 22, centerY + 22), 2)
        pygame.draw.line(board, (0, 0, 0), (centerX + 22, centerY - 22), (centerX - 22, centerY + 22), 2)
    if player == 2:
        # circle
        pygame.draw.circle(board, (0, 0, 0), (centerX, centerY), 44, 2)


def gui_show_board(game, board):
    gui_draw_status(board)
    game.blit(board, (0, 0))
    pygame.display.flip()


def position_on_board(mouseX, mouseY):
    if mouseY < 100:
        row = 0
    elif mouseY < 200:
        row = 1
    else:
        row = 2

    if mouseX < 100:
        col = 0
    elif mouseX < 200:
        col = 1
    else:
        col = 2

    return row, col


def gui_click_board():
    global game_info
    (mouseX, mouseY) = pygame.mouse.get_pos()
    (row, col) = position_on_board(mouseX, mouseY)
    if game_info.winner is None:
        sync_wait(make_move(row, col))
    else:
        game_info.reset_game()


def gui():
    global game_info
    pygame.init()
    game = pygame.display.set_mode((300, 325))
    pygame.display.set_caption('Tic Tac Toe Client')
    # create the game menu
    menu = gui_init_menu(game)

    # main event loop
    running = True
    while running:
        game_list = sync_wait(get_games())
        for menu_event in pygame.event.get():
            if menu_event.type is QUIT:
                running = False
            elif menu_event.type is MOUSEBUTTONDOWN:
                gui_click_menu(game, game_list)
            # update the display
            gui_show_menu(game, menu, game_list)

            while game_info.selected_game_id is not None:
                board = gui_init_board(game)
                for event in pygame.event.get():
                    if event.type is QUIT:
                        game_info.selected_game_id = None
                        running = False
                    elif event.type is MOUSEBUTTONDOWN:
                        gui_click_board()
                    # update the display
                    gui_show_board(game, board)

##################### PYGAME #####################


if __name__ == "__main__":
    if len(sys.argv) == 3:
        game_info.host = (sys.argv[1])
        game_info.port = (sys.argv[2])
        text_ui()
        # gui()
    else:
        print("Wrong number of arguments")