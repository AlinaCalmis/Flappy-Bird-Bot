import json
from json import JSONDecodeError
import random


class Learning:
    def __init__(self):

        # Initialize the agent
        self.previous_state = "0_0_0_0"
        self.previous_action = 0
        self.discount_factor = 0.9
        self.learning_rate = 0.8
        self.reward = {0: -1, 1: -100}
        self.epsilon = 0.9  # for epsilon greedy algorithm
        self.moves = []
        self.scores = []
        self.max_score = 0

        self.episode = 0

        self.qvalues = {}
        self.load_qvalues()

    def load_qvalues(self):
        try:
            with open("data\q_values.json", "r") as file:
                self.qvalues = json.load(file)
        except IOError:
            self.initialize_qvalues(self.previous_state)
        except JSONDecodeError:
            self.initialize_qvalues(self.previous_state)

    def initialize_qvalues(self, state):
        if self.qvalues.get(state) is None:
            self.qvalues[state] = [0, 0, 0];

    def act(self, x, y, vel):
        state = self.get_state(x, y, vel)
        self.moves.append((self.previous_state, self.previous_action, state))
        self.previous_state = state
        if random.random() <= self.epsilon:
            self.previous_action = random.choice([0, 1])
            return self.previous_action

        # Chose the best action : default is 0 (don't do anything) or 1 (flap)
        self.previous_action = 0 if self.qvalues[state][0] >= self.qvalues[state][1] else 1

        return self.previous_action

    # Update Q values using history
    def update_qvalues(self, score):
        self.episode += 1
        self.scores.append(score)
        self.max_score = max(score, self.max_score)

        history = list(reversed(self.moves))
        dead = True if int(history[0][2].split("_")[1]) > 120 else False
        t, last_flap = 0, True
        for move in history:
            t += 1
            state, action, new_state = move
            self.qvalues[state][2] += 1
            reward = self.reward[0]
            if t <= 2:
                reward = self.reward[1]
                if action:
                    last_flap = False
            elif (last_flap or dead) and action:
                reward = self.reward[1]
                last_flap = False
                dead = False

            self.qvalues[state][action] = (1 - self.learning_rate) * (self.qvalues[state][action] +
                                                                      self.learning_rate * (
                                                                              reward + self.discount_factor *
                                                                              max(self.qvalues[state][0:2])))

            if self.learning_rate > 0.1:
                self.learning_rate = 0.1

            if self.epsilon > 0:
                self.epsilon = 0

            self.moves = []

    def get_state(self, x, y, vel):
        if x < 140:
            x = int(x) - (int(x) % 10)
        else:
            x = int(x) - (int(x) % 70)

        if y < 180:
            y = int(y) - (int(y) % 10)
        else:
            y = int(y) - (int(y) % 60)

        return str(int(x)) + "_" + str(int(y)) + "_" + str(vel)

    def end_episode(self, score):
        self.episode += 1
        self.scores.append(score)
        self.max_score = max(score, self.max_score)
        history = list(reversed(self.moves))
        for move in history:
            state, action, new_state = move
            self.qvalues[state][action] = (1 - self.learning_rate) * (self.qvalues[state][action] +
                                                                      self.learning_rate * (
                                                                              self.reward[0] +
                                                                              self.discount_factor *
                                                                              max(self.qvalues[state][0:2])))
        self.moves = []

    def qvalues_to_json(self):
        print(f"Saving Q Table with {len(self.qvalues.keys())} states ...")
        with open("data\game_history.json", "w") as file:
            json.dump(self.qvalues, file)


