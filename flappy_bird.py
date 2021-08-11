import copy
import random
import sys
import os
from collections import deque
from itertools import cycle

import pygame
from pygame.constants import *

from learning import Learning
import game as game

bot = Learning()

FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

PIPEGAP = 100
IMAGES, SOUNDS, HITMASKS = {}, {}, {}
BASEH = SCREEN_HEIGHT * 0.79
STATE_HISTORY = deque(maxlen=70)

PLAYERS = (
    # blue bird
    (
        'flappy-bird-assets/sprites/bluebird-downflap.png',
        'flappy-bird-assets/sprites/bluebird-midflap.png',
        'flappy-bird-assets/sprites/bluebird-upflap.png',
    ),
    # red bird
    (
        'flappy-bird-assets/sprites/redbird-downflap.png',
        'flappy-bird-assets/sprites/redbird-midflap.png',
        'flappy-bird-assets/sprites/redbird-upflap.png',
    ),
    # yellow bird
    (
        'flappy-bird-assets/sprites/yellowbird-downflap.png',
        'flappy-bird-assets/sprites/yellowbird-midflap.png',
        'flappy-bird-assets/sprites/yellowbird-upflap.png',
    ),
)

BACKGROUNDS = (
    'flappy-bird-assets/sprites/background-day.png',
    'flappy-bird-assets/sprites/background-night.png',
)

PIPES = (
    'flappy-bird-assets/sprites/pipe-red.png',
    'flappy-bird-assets/sprites/pipe-green.png',
)


def main():
    global SCREEN, FPSCLOCK, FPS
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    IMAGES['numbers'] = (
        pygame.image.load('flappy-bird-assets/sprites/0.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/1.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/2.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/3.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/4.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/5.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/6.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/7.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/8.png').convert_alpha(),
        pygame.image.load('flappy-bird-assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('flappy-bird-assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('flappy-bird-assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('flappy-bird-assets/sprites/base.png').convert_alpha()

    if 'win' in sys.platform:
        sound_ext = '.wav'

    else:
        sound_ext = '.ogg'

        SOUNDS['die'] = pygame.mixer.Sound('flappy-bird-assets/audio/die' + sound_ext)
        SOUNDS['hit'] = pygame.mixer.Sound('flappy-bird-assets/audio/hit' + sound_ext)
        SOUNDS['point'] = pygame.mixer.Sound('flappy-bird-assets/audio/point' + sound_ext)
        SOUNDS['swoosh'] = pygame.mixer.Sound('flappy-bird-assets/audio/swoosh' + sound_ext)
        SOUNDS['wing'] = pygame.mixer.Sound('flappy-bird-assets/audio/wing' + sound_ext)

    while True:
        # select random background sprites
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS[rand_bg]).convert()

        # select random player sprites
        rand_player = random.randint(0, len(PLAYERS) - 1)

        IMAGES['player'] = (
            pygame.image.load(PLAYERS[rand_player][0]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][1]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][2]).convert_alpha(),
        )

        pipeindex = random.randint(0, len(PIPES) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(pygame.image.load(PIPES[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES[pipeindex]).convert_alpha(),
        )
        # hitmask for pipes
        HITMASKS['pipe'] = (
            game.get_hitmask(image_alpha=IMAGES['pipe'][0]),
            game.get_hitmask(image_alpha=IMAGES['pipe'][1]),
        )

        start_game = welcome_animation()
        print(start_game.items())
        main_game()


def welcome_animation():
    player_index = 0
    player_generation = cycle([0, 1, 2, 1])
    loops = 0

    player_x = int(SCREEN_WIDTH * 2)
    player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)

    message_x = int((SCREEN_WIDTH - IMAGES['message'].get_width()) / 2)
    message_y = int(SCREEN_HEIGHT * 0.12)

    shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    base_x = 0

    player_flapp = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return {
                    'player_y': player_y + player_flapp['val'],
                    'base_x': base_x,
                    'player_generation': player_generation
                }

        if (loops + 1) % 5 == 0:
            player_index = player_generation.__next__()
        loops += (loops + 1) % 30
        base_x = - ((-base_x + 3) % shift)
        playerShm(player_flapp)
        print(loops)

        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['player'][player_index], (player_x, player_y + player_flapp['val']))
        SCREEN.blit(IMAGES['message'], (message_x, message_y))
        SCREEN.blit(IMAGES['base'], (base_x, BASEH))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

        # player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)
        # player_generation


def main_game(info):
    score = player_index = loops = 0
    player_generation = info['player_generation']
    player_x, player_y = int(SCREEN_WIDTH * 0.2), info['player_y']

    base_x = info['base_x']
    shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    pipe1 = getRandomPipe()
    pipe2 = getRandomPipe()

    upper_pipes = [
        {'x':SCREEN_WIDTH + 200, 'y': pipe1[0]['y']},
        {'x':SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe2[0]['y']}
    ]

    lower_pipes = [
        {'x':SCREEN_WIDTH + 200, 'y': pipe1[0]['y']},
        {'x':SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe2[0]['y']}
    ]

    pipe_vel_y = -4

    player_vel_y = -9
    player_max_vel = 10
    player_min_vel = -8
    player_acc_y = 1
    player_flap_speed = -9
    player_flapped = False


    if (len(STATE_HISTORY) < 20):
        STATE_HISTORY.clear()
    resume_from_history = len(STATE_HISTORY) > 0
    initial_len_history = len(STATE_HISTORY)
    resume_from = 0
    current_score = STATE_HISTORY[-1][5]
    print_score = False

    while True:
        if resume_from_history:
            if resume_from == 0:
                player_x, player_y, player_vel_y, lower_pipes, upper_pipes, score, player_index = STATE_HISTORY[resume_from]
            else:
                lower_pipes, upper_pipes = STATE_HISTORY[resume_from][3], STATE_HISTORY[resume_from][4]
            resume_from += 1
        else:
            STATE_HISTORY.append([player_x, player_y, player_vel_y, copy.deepcopy(lower_pipes), copy.deepcopy(
                upper_pipes), score, player_index])


def getRandomPipe():
    """Returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
    ]



def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


if __name__ == '__main__':
    main()
