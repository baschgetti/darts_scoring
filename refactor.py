#!/usr/bin/env python3

import re


# -----------------------Utility-----------------------


def find_player_with_name(players, name):
    for player in players:
        if name == player.name:
            return player
    return None


def empty_list(list_empty):
    for i in range(len(list_empty)):
        list_empty.pop()


# -----------------------Player-----------------------


class Player:
    def __init__(self, name, start_score):
        self.history = []
        self.name = name
        self.start_score = start_score
        self.remaining_score = start_score
        self.require_double_finish = False
        self.temp = []
        self.number_of_scores = 0

    def reset_temp(self):
        self.temp = []
        self.number_of_scores = 0

    def is_finished(self):
        return self.remaining_score == 0

    def darts_left(self):
        return self.number_of_scores > 0

    def strip_history(self, amount):
        temp_len, hist_len = len(self.temp), len(self.history)
        if amount > temp_len + hist_len:
            return False
        self.temp = self.temp[:-min(amount, temp_len)]
        if amount > temp_len:
            score_stripped = sum_input(self.history[-(amount - temp_len):])
            self.remaining_score += score_stripped
            self.history = self.history[:-(amount - temp_len)]
        print(f"deleted last {amount} darts from history.")
        self.number_of_scores += max(0, amount - temp_len)
        return True


def append_temp_to_history(player, valid):
    if not valid:
        player.temp = list(map(lambda s: s + "x", player.temp)) + ["x"] * (player.number_of_scores - len(player.temp))
    player.history += player.temp


# -----------------------Setup-----------------------


def setup():
    print("---Setup---")
    input_string = ""
    while not input_string.isdigit() or int(input_string) <= 0:
        input_string = input("please enter your starting score: ")
    start_score = int(input_string)
    names = []
    while len(names) < 1:
        names = input("please enter the names of all players: ").split()
        if len(names) != len(set(names)):
            print("use distinct names pls :)")
            names = []

    players = []
    wait_queue = []
    for name in names:
        p = Player(name, start_score)
        players.append(p)
        wait_queue.append(p)

    print("---Game---")
    return start_score, players, wait_queue


# -----------------------Input Managing-----------------------


def replace_full_stops(scores):
    for i in range(1, len(scores)):
        if scores[i] == ".":
            scores[i] = scores[i - 1]  # safe because input validation does not accept leading .
    return scores


def sum_input(scores):
    return sum(map(lambda score: convert_score(score), scores))


def convert_score(score):
    match score[-1:]:
        case "d":
            return int(score[:-1]) * 2
        case "t":
            return int(score[:-1]) * 3
        case "x":
            return 0
        case _:
            return int(score) if score.isnumeric() else 0


def regular_input_validation(player, input_string):
    input_string = input_string.replace(".", " . ").replace("d", "d ").replace("t", "t ").rstrip().lstrip()
    regex = re.search(r"(^\d[dt]?|^1\d[dt]?|^20[dt]?|^25d?)(\s+(\.|\d[dt]?|1\d[dt]?|20[dt]?|25d?)){0,2}$", input_string)
    return regex is not None and len(player.temp) + len(input_string.split()) <= player.number_of_scores


def regular_input_to_scores(input_string):
    input_string = input_string.replace(".", " . ").replace("d", "d ").replace("t", "t ").rstrip().lstrip()
    return replace_full_stops(input_string.split())


# -----------------------Special Input-----------------------


def special_input_validation(input_string):
    regex = re.search(r"^(del\s+[1-9]\d*|end|skip|next\s+.*|setwq\s+(.*)*)\s*$", input_string)
    return regex is not None


def special_input_action(input_string, player, wait_queue, players):
    if input_string == "":
        return True
    if input_string.startswith("end"):
        wait_queue.pop(0)
        append_temp_to_history(player, True)
        print(f"{player.name} has chosen to withdraw with a remaining score of {player.start_score - sum_input(player.history)}")
        return True
    elif input_string.startswith("del"):
        amount = int(input_string.split()[1])
        if not player.strip_history(amount):
            print("invalid number")
            return False
        return True
    elif input_string.startswith("edit"):
        # TODO
        return True
    elif input_string.startswith("skip"):
        wait_queue.append(wait_queue.pop(0))
        print(f"skipping {player.name}")
        return True
    elif input_string.startswith("next"):
        name = input_string.split()[1]
        player = find_player_with_name(players, name)
        if player is None:
            print("invalid name")
            return False
        wait_queue.insert(0, player)
        if player.number_of_scores <= 0:
            player.number_of_scores -= 3
            # necessary to avoid finished players to change and del 1 or 2 and get 3 inputs (see: how is
            # number_of_scores increased)
        return True
    elif input_string.startswith("setwq"):
        new_wait_queue = []
        names = input_string.split()[1:]
        for name in names:
            p = find_player_with_name(wait_queue, name)
            if len(set(names)) != len(set(wait_queue)):
                print("too few or too many distinct names. setwq arguments must contain all names that are currently "
                      "scheduled. use change to add a player that has finished to the wait queue.")
                return False
            if p is None:
                print("invalid name or contains player that has finished")
                return False
            new_wait_queue.append(p)
        empty_list(wait_queue)
        wait_queue.extend(new_wait_queue)
        return True
    return False


# -----------------------Game Logic-----------------------


def modify_wait_queue(wait_queue, player):
    if not player.darts_left():
        wait_queue.pop(0)
        if player.remaining_score > 0 and find_player_with_name(wait_queue, player.name) is None:
            wait_queue.append(player)


def valid_move(player, remaining):
    if remaining < 0:
        print("too high")
        return False
    if (remaining == 1 and player.require_double_finish) or (remaining == 0 and player.require_double_finish and player.temp[-1][-1:] != "d"):
        print("double finish required")
        return False
    return True


def play(player, scores):
    append = True
    player.temp += scores
    remaining = player.remaining_score - sum_input(player.temp)
    if not valid_move(player, remaining):
        append = False
        remaining = player.remaining_score

    if len(player.temp) == player.number_of_scores or remaining == 0 or not append:
        append_temp_to_history(player, append)
        player.reset_temp()
        player.remaining_score = remaining
        print(f"{player.name} has [{player.remaining_score}] remaining")


def game():
    start_score, players, wait_queue = setup()

    while len(wait_queue) > 0:
        print(list(map(lambda pl: pl.name, wait_queue)))
        player = wait_queue[0]
        if player.number_of_scores <= 0:
            player.number_of_scores += 3
        input_string = input(f"{player.name} [{player.remaining_score - sum_input(player.temp)}]: ").lstrip().rstrip()
        if special_input_validation(input_string):
            special_input_action(input_string, player, wait_queue, players)
        elif regular_input_validation(player, input_string):
            play(player, regular_input_to_scores(input_string))
            modify_wait_queue(wait_queue, player)
            if player.is_finished():
                print(f"{player.name} has finished at position {list(map(lambda pl: pl.is_finished(), players)).count(True)} using {len(player.history)} darts.")
        else:
            print("Invalid")

    for p in players:
        print(f"{p.name} {p.history}")


game()
