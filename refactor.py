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


def contains(element, search_list):
    # return any(list(map(lambda e: e == element, search_list)))
    return search_list.count(element) > 0


def determine_redo_amount(player):
    amount = (len(player.history) + len(player.temp) + 2) % 3 + 1
    return amount


def count_darts_not_thrown(player, n):
    amount_darts_not_thrown = 0
    for i in range(n):
        if player.history[-i] == "x":
            amount_darts_not_thrown += 1
    return amount_darts_not_thrown


def is_edit_start_score_forbidden(player, new_score):
    curr_score = player.start_score - player.remaining_score + sum_input(player.temp)
    if new_score - 1 <= curr_score:
        print("new score too low")
        return True
    return False


# note that this not perform validity checks
def edit_start_score(player, new_score):
    difference = player.start_score - new_score
    player.remaining_score -= difference
    player.start_score = new_score
    print(f"{player.name}'s start score changed to {player.start_score}. New remaining score is {player.remaining_score}")


def print_help():
    help_text = f"""------------------------------------------
How to use: 
Before a game starts, you will be asked to enter the following:
--------------
starting score: in the range of [1,infinity)
--------------
names of all players: all names seperated by spaces. The game will adopt the order in which the names are listed.
--------------
During the game:
To enter scores:
<score> <score>[0-2 times: opt]: Enter at least one and up to three scores seperated by spaces. To enter doubles or trebles, follow the number by 'd' or 't' respectively, e.g. 25d 20t 10. Press Enter to confirm. A '.' is accepted as 2nd or 3rd score and indicates that the score before was scored again. If less than 3 scores are entered, you will be asked to enter the remaining scores in a new line.
--------------
To make adjustments:
--------------
end: removes current player from the game.
--------------
del: deletes one round of scores from the history of scores
--------------
skip: skips the current player.
--------------
redo <player>: changes the current player to the specified player, deletes the scores of the last round and asks you to enter replacement for the deleted scores.
--------------
setwq <list of all names>: changes the order according to the provided list of players' names. List must include each player name currently in the wait queue exactly once. To include a player that is not currently playing, use redo before.
--------------
info <name>: gives you information about given player
--------------
edit <name> <option>: edits properties of one player according to one of the following options:
    sscore <new start score>: changes the start score to <new start score>
    name <new name>: changes the name of the player to <new name>
    reqDouble <False|True>: changes the game mode whether the player is required to finish with a Double
    numScores <new num of scores>: changes the number of scores of the current player to <new num of scores>. <new num of scores> has to be divisible by 3.
--------------
help: print this help text
------------------------------------------"""
    print(help_text)


def redo_blocked(wait_queue):
    return wait_queue.count(wait_queue[0]) > 1


def setwq_blocked(wait_queue):
    return redo_blocked(wait_queue)


# -----------------------Utility-----------------------


class State:
    def __init__(self):
        self.allow_redo = True


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
        if amount > temp_len + hist_len or amount == 0:
            return False
        self.temp = self.temp[:-min(amount, temp_len)]
        count_x_darts = count_darts_not_thrown(self, amount - temp_len)
        if amount > temp_len:
            score_stripped = sum_input(self.history[-(amount - temp_len):])
            self.remaining_score += score_stripped
            self.history = self.history[:-(amount - temp_len)]
        print(f"deleted last {amount - count_x_darts} "
              f"darts from history.")
        # self.number_of_scores += max(0, amount - temp_len)
        self.number_of_scores += 3 if temp_len == 0 else 0
        return True

    def print_info(self):
        print(f"--------------\n"
              f"Player {self.name}\n"
              f"Remaining score: {self.remaining_score - sum_input(self.temp)}\n"
              f"Are you required to score a double to end the game? {self.require_double_finish}\n"
              f"Your score history: {self.history + self.temp}\n"
              f"--------------")
        return


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
    regex = re.search(r"^(del\s*$|end\s*$|skip\s*$|redo\s+.+\s*$|setwq\s+(.*)*)\s*$|help\s*$|info\s+.+\s*$|edit\s+.+\s+(sscore\s+[1-9]\d*|name\s+.+|reqDouble\s+(False|True)|numScores\s+\d+)\s*|editg\s+(sscore\s+[1-9]\d*|reqDouble\s+(False|True))\s*$", input_string)
    return regex is not None


def special_input_action(input_string, player, wait_queue, players):
    if input_string == "":
        return True
    command = input_string.split()[0]
    match command:
        case "end":
            wait_queue.pop(0)
            append_temp_to_history(player, True)
            print(f"{player.name} has chosen to withdraw with a remaining score of "
                  f"{player.start_score - sum_input(player.history)}")
            return True

        case "del":
            # amount = int(input_string.split()[1])
            amount = determine_redo_amount(player)
            if not player.strip_history(amount):
                print("invalid number")
                return False
            return True

        case "skip":
            modify_wait_queue(wait_queue, player, True)
            print(f"skipping {player.name}")
            return True

        case "redo":
            if redo_blocked(wait_queue):
                print("not allowed to use redo until the player that used it before has finished their redo")
                return False
            name = input_string.split()[1]
            p = find_player_with_name(players, name)
            if p is None:
                print("invalid name")
                return False

            amount = determine_redo_amount(p)
            if p == player or not p.strip_history(amount):
                print("player must not be the current player and must already have at least three darts in their score history")
                return False
            wait_queue.insert(0, p)
            # state.allow_redo = False
            return True

        case "setwq":
            if setwq_blocked(wait_queue):
                print("not allowed to use setwq until the player that used redo before has finished their redo")
                return False
            new_wait_queue = []
            names = input_string.split()[1:]

            if len(set(names)) != len(set(wait_queue)):
                print("too few or too many distinct names. setwq arguments must contain all names that are currently "
                      "scheduled. use redo to add a player that has finished to the wait queue.")
                return False

            for name in names:
                p = find_player_with_name(wait_queue, name)
                if p is None:
                    print("invalid name or contains player that has finished")
                    return False
                new_wait_queue.append(p)
            empty_list(wait_queue)
            wait_queue.extend(new_wait_queue)
            return True

        case "editg":
            option = input_string.split()[1]
            match option:
                case "sscore":
                    new_score = int(input_string.split()[2])
                    if any(map(lambda pl: is_edit_start_score_forbidden(pl, new_score), players)):
                        return False
                    for p in players:
                        edit_start_score(p, new_score)
                    return True
                case "reqDouble":
                    req_double = True if input_string.split()[2] == "True" else False
                    for p in wait_queue:
                        p.require_double_finish = req_double
                    print(f"game mode changed to requireDouble = {req_double} for all players.")
                    return True
                case _:
                    return False

        case "edit":
            p = find_player_with_name(players, input_string.split()[1])
            if p is None:
                print("no player with this name found")
                return False
            option = input_string.split()[2]
            match option:
                case "sscore":
                    new_score = int(input_string.split()[3])
                    if is_edit_start_score_forbidden(p, new_score):
                        return False
                    edit_start_score(p, new_score)
                    return True
                case "name":
                    new_name = input_string.split()[3]
                    old_name = p.name
                    p.name = new_name
                    print(f"Player {old_name} has changed their name to {new_name}.")
                    return True
                case "reqDouble":
                    req_double = True if input_string.split()[3] == "True" else False  # regex makes sure only False and True are valid inputs in the first place
                    old_req_double = p.require_double_finish
                    p.require_double_finish = req_double
                    print(f"Player {p.name} has changed their game mode from requireDouble = {old_req_double} to {p.require_double_finish}.")
                    return True
                case "numScores":
                    if p != player:
                        print("Player has to be the current player")
                        return False
                    num_scores = int(input_string.split()[3])
                    old_num_scores = p.number_of_scores
                    if num_scores % 3 != 0:
                        print("numScores must be divisible by 3")
                        return False
                    p.number_of_scores = num_scores
                    print(f"Player {p.name} has changed their remaining scores from {3 if old_num_scores == 0 else old_num_scores} to {p.number_of_scores}.")
                    return True

        case "info":
            p = find_player_with_name(players, input_string.split()[1])
            if p is None:
                print("no player with this name found")
                return False
            p.print_info()
            return True

        case "help":
            print_help()
            return True
        case _:
            return False


# -----------------------Game Logic-----------------------


def update_state(state: State):
    state.allow_redo = True


def modify_wait_queue(wait_queue, player, skip):
    if not player.darts_left() or skip:
        # update_state(state)
        wait_queue.pop(0)
        if player.remaining_score == 0 and contains(player, wait_queue):
            wait_queue.remove(player)
        elif player.remaining_score > 0 and not contains(player, wait_queue):
            wait_queue.append(player)


def valid_move(player, remaining):
    if remaining < 0:
        print("too high")
        return False
    if ((remaining == 1 and player.require_double_finish) or
            (remaining == 0 and player.require_double_finish and player.temp[-1][-1:] != "d")):
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
    # state = State()
    start_score, players, wait_queue = setup()

    while len(wait_queue) > 0:
        # print(list(map(lambda pl: pl.name, wait_queue)))
        player = wait_queue[0]
        input_string = input(f"{player.name} [{player.remaining_score - sum_input(player.temp)}]: ").lstrip().rstrip()
        if special_input_validation(input_string):
            special_input_action(input_string, player, wait_queue, players)
            continue
        if player.number_of_scores <= 0:
            player.number_of_scores += 3
        if regular_input_validation(player, input_string):
            play(player, regular_input_to_scores(input_string))
            modify_wait_queue(wait_queue, player, False)
            if player.is_finished():
                print(f"{player.name} has finished at position "
                      f"{list(map(lambda pl: pl.is_finished(), players)).count(True)} "
                      f"using {len(player.history)} darts.")
        else:
            print("Invalid input.")

    for p in players:
        print(f"{p.name} {p.history}")


game()
