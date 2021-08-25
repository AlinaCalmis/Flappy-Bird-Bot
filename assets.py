
# init game
FPS = 60
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

PIPE_GAP = 100
IMAGES, SOUNDS, HIT_MASKS = {}, {}, {}
BASE_H = SCREEN_HEIGHT * 0.79
PLAYER_H = 24
PLAYER_W = 34
BACKGROUND_W = 288
BASE_W = 336
PIPE_W = 52
PIPE_H = 320

MODE = 'easy'

EASY = 100
MEDIUM = 60
HARD = 10

ELEVATION = 200


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

