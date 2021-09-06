import argparse
import os
import pickle
import random
import sys
from itertools import cycle

import pygame

from assets import *
from learning import Learning

import matplotlib.pyplot as plt

sys.path.append(os.getcwd())

sys.path.append(os.getcwd())

parser = argparse.ArgumentParser('flappy_bird_learn.py')
parser.add_argument('--mode', type=str, default='easy', help='choose the level of hardness')

args = parser.parse_args()

MODE = args.mode

# init bot
bot = Learning(mode=MODE)


def main():
    global HIT_MASKS

    with open('data/hit_masks.pkl', 'rb') as hit_masks:
        HIT_MASKS = pickle.load(hit_masks)
    hit_masks.close()

    while True:
        start_game = welcome_animation()

        game_info = main_game(start_game)

        show_game_over_screen(game_info)


def welcome_animation():
    player_y = int((SCREEN_HEIGHT - PLAYER_H) / 2)
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
    shift = BASE_W - BACKGROUND_W

    pipe1 = get_random_pipe()
    pipe2 = get_random_pipe()

    if MODE == 'easy':
        mode_x = ELEVATION - EASY / 2
    elif MODE == 'medium':
        mode_x = ELEVATION - MEDIUM / 2
    elif MODE == 'hard':
        mode_x = ELEVATION - HARD / 2
    else:
        mode_x = ELEVATION - EXTRA / 2

    # list of upper pipes
    upper_pipes = [
        {'x': SCREEN_WIDTH + mode_x, 'y': pipe1[0]['y']},
        {'x': SCREEN_WIDTH + ELEVATION + (SCREEN_WIDTH / 2), 'y': pipe2[0]['y']}
    ]

    # list of lower pipes
    lower_pipes = [
        {'x': SCREEN_WIDTH + mode_x, 'y': pipe1[1]['y']},
        {'x': SCREEN_WIDTH + ELEVATION + (SCREEN_WIDTH / 2), 'y': pipe2[1]['y']}
    ]

    pipe_vel_x = -4

    player_vel_y = -9
    player_max_vel = 10
    player_min_vel = -8
    player_acc_y = 1
    player_flap_speed = -9
    player_flapped = False

    while True:

        if -player_x + lower_pipes[0]['x'] > -30:
            my_pipe = lower_pipes[0]
        else:
            my_pipe = lower_pipes[1]

        if bot.act(-player_x + my_pipe['x'], -player_y + my_pipe['y'], player_vel_y):
            if player_y > -2 * PLAYER_H:
                player_vel_y = player_flap_speed
                player_flapped = True

        crash_test = did_collide(player_id, player_x, player_y, upper_pipes, lower_pipes)

        if crash_test:
            bot.update_qvalues()
            bot.qvalues_to_json(force=False)
            return {
                'y': player_y,
                'base_x': base_x,
                'upper_pipes': upper_pipes,
                'lower_pipes': lower_pipes,
                'score': score,
                'player_velocity': player_vel_y,
            }

        # check for score
        player_mid_pos = player_x + PLAYER_W / 2
        for pipe in upper_pipes:
            if MODE == 'extra':
                pipe_mid_pos = pipe["x"] + EXTRA_PIPE_W / 2
            else:
                pipe_mid_pos = pipe["x"] + PIPE_W / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1

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
        player_height = PLAYER_H
        player_y += min(player_vel_y, BASE_H - player_y - player_height)

        # move pipes to left
        for upper, lower in zip(upper_pipes, lower_pipes):
            upper['x'] += pipe_vel_x
            lower['x'] += pipe_vel_x

        # add new pipe when first pipe is about exit
        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # remove first pipe if it is out of the screen
        if MODE == 'extra':
            width = EXTRA_PIPE_W
        else:
            width = PIPE_W
        if upper_pipes[0]['x'] < -width:
            upper_pipes.pop(0)
            lower_pipes.pop(0)


def did_collide(id, player_x, player_y, upper_pipes, lower_pipes):
    if player_y > BASE_H - 25 or player_y < 0:
        return True

    height = PIPE_H
    width = EXTRA_PIPE_W if MODE == 'extra' else PIPE_W

    player_rectangle = pygame.Rect(player_x, player_y, PLAYER_W,
                                   PLAYER_H)

    for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
        upper_rectangle = pygame.Rect(upper_pipe['x'], upper_pipe['y'], width, height)
        lower_rectangle = pygame.Rect(lower_pipe['x'], lower_pipe['y'], width, height)

        player = HIT_MASKS['player'][id]
        upper = HIT_MASKS['pipe'][0]
        lower = HIT_MASKS['pipe'][1]

        upper_collision = get_collision(player_rectangle, upper_rectangle, player, upper)
        lower_collision = get_collision(player_rectangle, lower_rectangle, player, lower)

        if upper_collision or lower_collision:
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


def get_random_pipe():
    """Returns a randomly generated pipe"""
    if MODE == 'easy':
        mod_x = EASY  # change for increase or decrease x distance between pipes default --> 10
    elif MODE == 'medium':
        mod_x = MEDIUM
    elif MODE == 'hard':
        mod_x = HARD
    else:
        mod_x = EXTRA
    mod_y = mod_x / 3  # change for increase or decrease y distance between pipes default --> 0

    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_H * 0.6 - PIPE_GAP))
    gap_y += int(BASE_H * 0.2)
    pipe_height = PIPE_H
    pipe_x = SCREEN_WIDTH + mod_x

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height - mod_y},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPE_GAP + mod_y},  # lower pipe
    ]


def player_shm(player_movement):
    """oscillates the value of player_movement['val'] between 8 and -8"""
    if abs(player_movement['val']) == 8:
        player_movement['dir'] *= -1

    if player_movement['dir'] == 1:
        player_movement['val'] += 1
    else:
        player_movement['val'] -= 1


def show_game_over_screen(crash_info):
    score = crash_info['score']
    print(str(bot.game_cnt - 1) + '|' + str(score))
    REPS.append(bot.game_cnt)
    SCORES.append(score)
    bot.qvalues_to_json(force=True)
    # if bot.game_cnt == REPEATS:
    #     # plot()
    #     bot.qvalues_to_json(force=True)
    #     sys.exit()


def get_hitmask(image_alpha):
    """Returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image_alpha.get_width()):
        mask.append([])
        for y in range(image_alpha.get_height()):
            mask[x].append(bool(image_alpha.get_at((x, y))[3]))
    return mask


# def plot():
#     plt.scatter(REPS,SCORES, label="stars", color="green",
#                 marker="*", s=30)
#     plt.xlabel("Repetitions")
#     plt.ylabel("Scores")
#
#     plt.title(f'{MODE}_learning')
#     plt.show()


if __name__ == '__main__':
    main()
