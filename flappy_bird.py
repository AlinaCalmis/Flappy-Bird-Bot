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

sys.path.append(os.getcwd())

# init bot
bot = Learning()

FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

PIPE_GAP = 100
IMAGES, SOUNDS, HIT_MASKS = {}, {}, {}
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

# list of backgrounds
BACKGROUNDS = (
    'flappy-bird-assets/sprites/background-day.png',
    'flappy-bird-assets/sprites/background-night.png',
)

# list of pipes
PIPES = (
    'flappy-bird-assets/sprites/pipe-red.png',
    'flappy-bird-assets/sprites/pipe-green.png',
)


def main():
    global SCREEN, FPS_CLOCK, FPS

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
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
        # select random background
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS[rand_bg]).convert()

        # select random player
        rand_player = random.randint(0, len(PLAYERS) - 1)

        IMAGES['player'] = (
            pygame.image.load(PLAYERS[rand_player][0]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][1]).convert_alpha(),
            pygame.image.load(PLAYERS[rand_player][2]).convert_alpha(),
        )

        # select random pipe
        pipe_index = random.randint(0, len(PIPES) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(pygame.image.load(PIPES[pipe_index]).convert_alpha(), 180),
            pygame.image.load(PIPES[pipe_index]).convert_alpha(),
        )

        # hitmask for pipes
        HIT_MASKS['pipe'] = (
            game.get_hitmask(image_alpha=IMAGES['pipe'][0]),
            game.get_hitmask(image_alpha=IMAGES['pipe'][1]),
        )

        # hitmask for player
        HIT_MASKS['player'] = (
            game.get_hitmask(image_alpha=IMAGES['player'][0]),
            game.get_hitmask(image_alpha=IMAGES['player'][1]),
            game.get_hitmask(image_alpha=IMAGES['player'][2]),
        )

        # print(HIT_MASKS['pipe'][0])

        start_game = welcome_animation()
        # print(start_game.items())
        main_game(start_game)


def welcome_animation():
    """Show welcome animation"""
    # player_index = 0
    # player_generation = cycle([0, 1, 2, 1])
    # loops = 0
    #
    # player_x = int(SCREEN_WIDTH * 2)
    # player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)
    #
    # message_x = int((SCREEN_WIDTH - IMAGES['message'].get_width()) / 2)
    # message_y = int(SCREEN_HEIGHT * 0.12)
    #
    # shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    #
    # base_x = 0
    #
    # player_flap = {'val': 0, 'dir': 1}
    #
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
    #             SOUNDS['wing'].play()
    #             return {
    #                 'player_y': player_y + player_flap['val'],
    #                 'base_x': base_x,
    #                 'player_generation': player_generation
    #             }
    #
    #     if (loops + 1) % 5 == 0:
    #         player_index = player_generation.__next__()
    #     loops += (loops + 1) % 30
    #     base_x = - ((-base_x + 3) % shift)
    #     playerShm(player_flap)
    #     # print(loops)
    #
    #     SCREEN.blit(IMAGES['background'], (0, 0))
    #     SCREEN.blit(IMAGES['player'][player_index], (player_x, player_y + player_flap['val']))
    #     SCREEN.blit(IMAGES['message'], (message_x, message_y))
    #     SCREEN.blit(IMAGES['base'], (base_x, BASEH))
    #
    #     pygame.display.update()
    #     FPS_CLOCK.tick(FPS)

    player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)
    player_generation = cycle([0, 1, 2, 1])
    return {
        'player_y': player_y,
        'base_x': 0,
        'player_generation': player_generation
    }


def main_game(info):
    score = player_id = loops = 0
    player_generation = info['player_generation']
    player_x, player_y = int(SCREEN_WIDTH * 0.2), info['player_y']

    base_x = info['base_x']
    shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    pipe1 = getRandomPipe()
    pipe2 = getRandomPipe()

    # list of upper pipes
    upper_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': pipe1[0]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe2[0]['y']}
    ]

    # list of lower pipes
    lower_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': pipe1[1]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': pipe2[1]['y']}
    ]

    pipe_vel_x = -4

    player_vel_y = -9
    player_max_vel = 10
    player_min_vel = -8
    player_acc_y = 1
    player_flap_speed = -9
    player_flapped = False

    # if len(STATE_HISTORY) < 20:
    #     STATE_HISTORY.clear()
    # resume_from_history = len(STATE_HISTORY) > 0
    # initial_len_history = len(STATE_HISTORY)
    resume_from = 0
    # current_score = STATE_HISTORY[-1][5]
    # print_/score = False

    while True:
        # if resume_from_history:
        #     if resume_from == 0:
        #         player_x, player_y, player_vel_y, lower_pipes, upper_pipes, score, player_index = STATE_HISTORY[
        #             resume_from]
        #     else:
        #         lower_pipes, upper_pipes = STATE_HISTORY[resume_from][3], STATE_HISTORY[resume_from][4]
        #     resume_from += 1
        # else:
        #     STATE_HISTORY.append([player_x, player_y, player_vel_y, copy.deepcopy(lower_pipes), copy.deepcopy(
        #         upper_pipes), score, player_index])

        if -player_x + lower_pipes[0]['x'] > 30:
            my_pipe = lower_pipes[0]
        else:
            my_pipe = lower_pipes[1]

        for event in pygame.event.get():

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                # if print_score:
                #     print('')
                bot.qvalues_to_json()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > -2 * IMAGES['player'][0].get_width():
                    player_vel_y = player_flap_speed
                    player_flapped = True
                    SOUNDS['wing'].play()

        if bot.act(-player_x + my_pipe['x'], -player_y + my_pipe['y'], player_vel_y):
            if player_y > -2 * IMAGES['player'][0].get_width():
                player_vel_y = player_flap_speed
                player_flapped = True
                SOUNDS['wing'].play()

        crash_test = did_collide(player_id, player_x, player_y, upper_pipes, lower_pipes)

        if crash_test:
            bot.update_qvalues(score)
            bot.qvalues_to_json()
            return

        # check for score
        player_mid_pos = player_x + IMAGES["player"][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe["x"] + IMAGES["pipe"][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                SOUNDS["point"].play()

        # player_id basex change
        if (loops + 1) % 3 == 0:
            player_id = player_generation.__next__()
        loops = (loops + 1) % 30
        base_x = -((-base_x + 100) % shift)

        # player's movement
        if player_vel_y < player_max_vel and not player_flapped:
            player_vel_y += player_acc_y
        if player_flapped:
            player_flapped = False
        playerHeight = IMAGES["player"][player_id].get_height()
        player_y += min(player_vel_y, BASEH - player_y - playerHeight)

        # move pipes to left
        for upper, lower in zip(upper_pipes, lower_pipes):
            upper['x'] += pipe_vel_x
            lower['x'] += pipe_vel_x

        # add new pipe when first pipe is about exit
        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = getRandomPipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # remove first pipe if it is out of the screen
        if upper_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        SCREEN.blit(IMAGES['background'], (0, 0))

        for upper, lower in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (upper['x'], upper['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lower['x'], lower['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASEH))
        SCREEN.blit(IMAGES['player'][player_id], (player_x, player_y))

        # show_score(score)
        # print(score)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def did_collide(id, player_x, player_y, upper_pipes, lower_pipes):
    if player_y > BASEH - 25 or player_y < 0:
        SOUNDS['hit'].play()
        return True

    height = IMAGES['pipe'][0].get_height()
    width = IMAGES['pipe'][0].get_width()

    player_rectangle = pygame.Rect(player_x, player_y, IMAGES['player'][0].get_width(),
                                   IMAGES['player'][0].get_height())

    for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
        upper_rectangle = pygame.Rect(upper_pipe['x'], upper_pipe['y'], width, height)
        lower_rectangle = pygame.Rect(lower_pipe['x'], lower_pipe['y'], width, height)

        player = HIT_MASKS['player'][id]
        upper = HIT_MASKS['pipe'][0]
        lower = HIT_MASKS['pipe'][1]

        upper_collision = get_collision(player_rectangle, upper_rectangle, player, upper)
        lower_collision = get_collision(player_rectangle, lower_rectangle, player, lower)

        if upper_collision or lower_collision:
            SOUNDS['hit'].play()
            return True

    return False


def get_collision(player_rectangle, pipe_rectangle, p_hitmask, pipe_hitmask):
    rect = player_rectangle.clip(pipe_rectangle)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - player_rectangle.x, rect.y - player_rectangle.y
    x2, y2 = rect.x - pipe_rectangle.x, rect.y - pipe_rectangle.y

    for x in range(rect.width):
        for y in range(rect.height):
            if p_hitmask[x1 + x][y1 + y] and pipe_hitmask[x2 + x][y2 + y]:
                return True

    return False


def getRandomPipe():
    """Returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEH * 0.6 - PIPE_GAP))
    gapY += int(BASEH * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREEN_WIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPE_GAP},  # lower pipe
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
    x = 0
    # while x < 100:
    main()
        # x += 1
        # print(x)