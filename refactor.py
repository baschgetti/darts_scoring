#!/usr/bin/env python3

import re


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

    def darts_left(self):
        return self.number_of_scores > 0


def append_to_history(player, valid):
    player.history += player.temp if valid else ["-"] * player.number_of_scores


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

    players = []
    not_finished = []
    wait_queue = []
    for name in names:
        p = Player(name, start_score)
        players.append(p)
        not_finished.append(p)
        wait_queue.append(p)

    print("---Game---")
    return start_score, players, not_finished, wait_queue


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
        case "-", "end":
            return 0
        case _:
            return int(score)


def regular_input_validation(player, input_string):
    input_string = input_string.replace(".", " . ").replace("d", "d ").replace("t", "t ").rstrip().lstrip()
    regex = re.search(r"(^\d[dt]?|^1\d[dt]?|^20[dt]?|^25d?)(\s+(\.|\d[dt]?|1\d[dt]?|20[dt]?|25d?)){0,2}$", input_string)
    return regex is not None and len(player.temp) + len(input_string.split()) <= player.number_of_scores


def regular_input_to_scores(input_string):
    input_string = input_string.replace(".", " . ").replace("d", "d ").replace("t", "t ").rstrip().lstrip()
    return replace_full_stops(input_string.split())


# -----------------------Special Input-----------------------


# -----------------------Game Logic-----------------------


def modify_wait_queue(wait_queue, player):
    if not player.darts_left():
        wait_queue.pop(0)
        if player.remaining_score > 0:
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
        append_to_history(player, append)
        player.reset_temp()
        player.remaining_score = remaining


def game():
    start_score, players, not_finished, wait_queue = setup()

    while len(wait_queue) > 0:
        player = wait_queue[0]
        if player.number_of_scores == 0:
            player.number_of_scores += 3
        input_string = input(f"{player.name} [{player.remaining_score - sum_input(player.temp)}] {player.temp}: ")
        if regular_input_validation(player, input_string):
            play(player, regular_input_to_scores(input_string))
            modify_wait_queue(wait_queue, player)
            print(f"{player.name} has [{player.remaining_score}] remaining")
        else:
            print("Invalid")

    for p in players:
        print(f"{p.name} {p.history}")


game()
