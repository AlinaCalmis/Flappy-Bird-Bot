import codecs
import json
from json import JSONDecodeError
import random


class Learning:
    def __init__(self):

        # Initialize the agent
        self.previous_state = "0_0_0"
        self.previous_action = 0
        self.discount_factor = 1
        self.learning_rate = 0.8
        self.gameNR = 0
        self.LOAD_N = 25
        self.reward = {0: 1, 1: -100}
        self.moves = []
        self.scores = []
        self.qvalues = {}
        self.load_qvalues()

    def load_qvalues(self):
        try:
            with open("data\q_values.json", "r") as file:
                self.qvalues = json.load(file)
        except IOError:
            return
        except JSONDecodeError:
            return

        file.close()

    # analizeaza ultima miscare si alege cea mai buna optiune
    def act(self, x, y, vel):
        state = self.get_state(x, y, vel)

        # add the experience to the history
        self.moves.append((self.previous_state, self.previous_action, state))

        # update the previous state
        self.previous_state = state

        # Choose the best action : default is 0 (don't do anything) or 1 (flap)
        self.previous_action = 0 if self.qvalues[state][0] >= self.qvalues[state][1] else 1

        return self.previous_action

    # Update Q values using history
    def update_qvalues(self):

        # Update qvalues via iterating over experiences
        history = list(reversed(self.moves))

        dead = True if int(history[0][2].split("_")[1]) > 120 else False

        t, last_flap = 0, True
        for move in history:
            t += 1
            state, action, new_state = move

            reward = self.reward[0]

            if t <= 2:
                reward = self.reward[1]
                if action:
                    last_flap = False
            elif (last_flap or dead) and action:
                reward = self.reward[1]
                last_flap = False
                dead = False

            self.qvalues[state][action] = ((self.learning_rate) * self.qvalues[state][action] + self.learning_rate
                                           * (reward + self.discount_factor * max(self.qvalues[new_state]) -
                                              self.qvalues[state][action]))

        self.gameNR += 1

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

        state = str(int(x)) + "_" + str(int(y)) + "_" + str(int(vel))

        return state

    def qvalues_to_json(self, force=False):
        if self.gameNR % self.LOAD_N == 0 or force:
            with open("data\q_values.json", "w") as file:
                json.dump(self.qvalues, file, ensure_ascii=False)
            file.close()
            print(f"Saving Q Table with {len(self.qvalues.keys())} states ...")
