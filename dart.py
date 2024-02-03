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

    def is_finished(self):
        return self.remaining_score == 0 or (len(self.history) > 0 and self.history[-1] == "end")

    def strip_history(self, number):
        if len(self.history) >= number:
            stripped = self.history[-number:]
            self.history = self.history[:-number]
            return stripped
        return []


def append_to_history(player, scores, valid):
    player.history += scores if valid else ["-", "-", "-"]


# -----------------------Input Managing-----------------------


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


def replace_full_stops(scores):
    for i in range(1, len(scores)):
        if scores[i] == ".":
            scores[i] = scores[i - 1]  # safe because input validation does not accept leading .
    return scores


def get_scores_string_list(input_string):
    return replace_full_stops(input_string.split())


def input_validation(input_string, temp_len, input_size):
    regex = re.search(r"(^\d[dt]?|^1\d[dt]?|^20[dt]?|^25d?)(\s+(\.|\d[dt]?|1\d[dt]?|20[dt]?|25d?)){0,2}$", input_string)
    return regex is not None and temp_len + len(input_string.split()) <= input_size


def input_to_sum(player, temp, remaining, input_size):
    input_string = input(f"{player.name} [{str(remaining)}]: ").rstrip().lstrip()
    if detect_special_input(input_string, player, temp):
        print("detected")
        return False
    input_string = input_string.replace(".", " . ").replace("d", "d ").replace("t", "t ").rstrip().lstrip()
    if input_validation(input_string, len(temp), input_size):
        temp += get_scores_string_list(input_string)
    else:
        print("Invalid")
        return False
    return True


# -----------------------Special Input-----------------------


def validate_special_input():
    regex = re.search(r"^\s*(end|del\s*[1-9]\d*|edit\s+)\s*$")


def detect_special_input(input_string, player, temp):
    if input_string == "":
        return True
    if input_string.startswith("end"):
        player.append_to_history(["end"], True)
        return True
    elif input_string.startswith("del"):
        number = int(input_string.split()[1])
        delete_history(player, temp, number)
        return True
    elif input_string.startswith("edit"):
        return True
    return False


def delete_history(player, temp, number):
    if number > len(temp) + len(player.history):
        print("Invalid del")
        return False
    temp_len = len(temp)
    for i in range(min(number, temp_len)):
        temp.pop()
    stripped = player.strip_history(number - temp_len)
    player.remaining_score += sum_input(stripped)
    play(player, number - temp_len)
    return True


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
    for name in names:
        p = Player(name, start_score)
        players.append(p)
        not_finished.append(p)

    print("---Game---")
    return start_score, players, not_finished


# -----------------------Game Logic-----------------------


def valid_move(player, temp, remaining):
    if remaining > 0:
        return True
    if remaining < 0:
        print("too high")
        return False
    if player.require_double_finish and temp[-1][-1:] != "d":
        print("double finish required")
        return False
    return True


def play(player, input_size):
    temp = []
    append = True

    while len(temp) < input_size:
        remaining = player.remaining_score - sum_input(temp)
        if not input_to_sum(player, temp, remaining, input_size):
            continue
        remaining = player.remaining_score - sum_input(temp)
        if not valid_move(player, temp, remaining):
            append = False
            remaining = player.remaining_score
            break
        if remaining == 0:
            break

    player.remaining_score = remaining
    append_to_history(player, temp, append)


def game():
    start_score, players, not_finished = setup()

    while len(not_finished) > 0:
        for player in not_finished:
            play(player, 3)
            print(f"{player.name} has [{player.remaining_score}] remaining")
            if player.is_finished():
                not_finished.remove(player)
                print(f"{player.name} has finished at position {len(players) - len(not_finished)} using {len(player.history)} darts.")

    for p in players:
        print(f"{p.name} {p.history}")


game()
