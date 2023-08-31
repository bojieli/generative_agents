import random
import re
import openai
import tiktoken


class Mafia:
    num_werewolves = 3
    num_villagers = 3
    num_seers = 1
    num_witches = 1
    num_hunters = 1
    werewolves_win_if_all_others_are_killed = True

    def __init__(self):
        self.initialize_status()
        self.roles = self.generate_roles()
        print(self.roles)

    def shorten_prompt(self, messages):
        max_tokens = 4096 - 500
        encoding = tiktoken.get_encoding("cl100k_base")
        all_contents = '\n'.join([ msg['content'] for msg in messages ])
        num_tokens = len(encoding.encode(all_contents))
        if num_tokens <= max_tokens:
            return messages
        token_overage = num_tokens - max_tokens

        remove_done = False
        new_messages = []
        for msg in messages:
            if remove_done:
                new_messages.append(msg)
            if msg['role'] == 'user':  # remove the first user messages that exceeds token limit
                num_tokens = len(encoding.encode(msg['content']))
                token_overage -= num_tokens
                if token_overage <= 0:
                    remove_done = True
            else:  # do not remove system messages
                new_messages.append(msg)
        return new_messages

    def get_completion(self, messages):
        messages = self.shorten_prompt(messages)
        max_retries = 3
        for i in range(0, max_retries):
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages, request_timeout=30
                )
                return completion["choices"][0]["message"]["content"]
            except Exception as e:
                print(e)
        return ""

    def player_turn(self, player, command):
        game_intro = """
You are an experienced player of Mafia, a social deduction game. The game models a conflict between two groups: an informed minority (the werewolves) and and an uninformed majority (the villagers, seers, witches and hunters). At the start of the game, each player is secretly assigned a role (werewolf, villager, seer, witch or hunter). The game has two alternating phases: first, a night-phase, during which those with night-killing-powers may covertly kill other players, and second, a day-phase, in which all surviving players debate and vote to eliminate a suspect. The game continues until a faction achieves its win-condition; for the villagers, this means eliminating all the werewolves, while for the werewolves, this means eliminating either all the villagers or all the seers, witches and hunters.
    
At night, all players close their eyes. First, all werewolves acknowledge their accomplices, vote to pick a victim, and then close their eyes. Next, the seer open eyes and pick a player to reveal his/her real identity (the moderator only tells the identity to the seer but does not make it public), and then close eyes. Finally, the witches open eyes and know from the moderator which player is killed by the werewolves, and may decide to rescue him/her using the antidote. The witches may also decide to kill a player using the poison. Each witch has only one bottle of antidote and only one bottle of poison throughout the game.
    
At day, all players open their eyes. The moderator first announces which player is dead and the dead player may leave a last word. If the dead player is the hunter, the hunter may choose to kill one player, or choose to not kill anyone. Then, from the next living player of the dead player, every living player has a chance to discuss who are the werewolves. A player may accuse someone of being a werewolf and prompt others to vote to eliminate them. The real werewolves may lie to protect their identities. After the discussion, every living player has one vote to eliminate a player who is suspected to be a werewolf.
"""
        game_intro += (
            "In this instance of Mafia, there are "
            + str(self.num_werewolves)
            + " werewolves, "
            + str(self.num_villagers)
            + " villagers, "
            + str(self.num_seers)
            + " seers, "
            + str(self.num_witches)
            + " witches, and "
            + str(self.num_hunters)
            + " hunters. The players are numbered from 1 to "
            + str(self.num_players)
            + ".\n"
        )
        game_intro += "Below are the past conversions during this game."

        messages = [{"role": "system", "content": game_intro}]
        for record in self.speaker_records:
            if (
                record["visibility"] == self.roles[player]
                or record["visibility"] == "all"
            ):
                speaker = record["speaker"]
                if type(speaker) is int:
                    speaker = "Player " + str(speaker + 1)
                content = (
                    "Day "
                    + str(self.current_day)
                    + ", "
                    + speaker
                    + ": "
                    + record["content"]
                )
                messages.append({"role": "user", "content": content})

        messages.append(
            {
                "role": "system",
                "content": "You are player "
                + str(player + 1)
                + ", your role is "
                + self.roles[player]
                + ". Now it is your turn. "
                + command,
            }
        )

        response = self.get_completion(messages)
        return response

    def parse_int(self, response):
        match = re.search("[0-9]+", response)
        if not match:
            return None
        return int(match.group(0))

    def list_living_players(self):
        return str([i + 1 for i in range(0, self.num_players) if self.alive[i]])

    def generate_roles(self):
        self.roles = list(range(0, self.num_players))
        random.shuffle(self.roles)
        for i in range(0, self.num_players):
            num = self.roles[i]
            if num < self.num_werewolves:
                self.roles[i] = "werewolf"
                continue
            num -= self.num_werewolves

            if num < self.num_villagers:
                self.roles[i] = "villager"
                continue
            num -= self.num_villagers

            if num < self.num_seers:
                self.roles[i] = "seer"
                continue
            num -= self.num_seers

            if num < self.num_witches:
                self.roles[i] = "witch"
                continue
            num -= self.num_witches

            if num < self.num_hunters:
                self.roles[i] = "hunter"
                continue
            raise ValueError("Unknown role exception")
        return self.roles

    def initialize_status(self):
        self.num_players = (
            self.num_werewolves
            + self.num_villagers
            + self.num_seers
            + self.num_witches
            + self.num_hunters
        )
        self.alive = [True for i in range(0, self.num_players)]
        self.witches_poison_used = [False for i in range(0, self.num_players)]
        self.witches_antidote_used = [False for i in range(0, self.num_players)]
        self.current_day = 0
        self.speaker_records = []
        self.dead_players_in_this_round = []

    def print_game_end_message(self, message):
        print(message)
        print(self.roles)

    def game_ended(self):
        if self.werewolves_win_if_all_others_are_killed:  # the hard mode for werewolves
            num_alive_villagers = 0
            for i in range(0, self.num_players):
                if self.roles[i] in ["villager", "seer", "witch", "hunter"] and self.alive[i]:
                    num_alive_villagers += 1
            if num_alive_villagers == 0:
                self.print_game_end_message(
                    "All villagers, seers, witches and hunters are dead. Game ended. The werewolves win."
                )
                return True
        else:  # the easy mode for werewolves
            num_alive_villagers = 0
            for i in range(0, self.num_players):
                if self.roles[i] == "villager" and self.alive[i]:
                    num_alive_villagers += 1
            if num_alive_villagers == 0:
                self.print_game_end_message(
                    "All villagers are dead. Game ended. The werewolves win."
                )
                return True

            num_alive_special_roles = 0
            for i in range(0, self.num_players):
                if self.roles[i] in ["seer", "witch", "hunter"] and self.alive[i]:
                    num_alive_special_roles += 1
            if num_alive_special_roles == 0:
                self.print_game_end_message(
                    "All special roles are dead. Game ended. The werewolves win."
                )
                return True

        num_alive_werewolves = 0
        for i in range(0, self.num_players):
            if self.roles[i] == "werewolf" and self.alive[i]:
                num_alive_werewolves += 1
        if num_alive_werewolves == 0:
            self.print_game_end_message(
                "All werewolves are dead. Game ended. The villagers win."
            )
            return True

        return False

    def speak(self, speaker, visibility, content):
        self.speaker_records.append(
            {
                "day": self.current_day,
                "speaker": speaker,
                "visibility": visibility,
                "content": content,
            }
        )
        if type(speaker) is int:
            speaker_str = "Player " + str(speaker + 1)
        else:
            speaker_str = speaker
        print("Day " + str(self.current_day) + ", " + speaker_str + ": " + content)

    def werewolves_kill(self):
        votes = [0 for i in range(0, self.num_players)]
        alive_werewolves = []
        for i in range(0, self.num_players):
            if self.roles[i] == "werewolf" and self.alive[i]:
                alive_werewolves.append(i)

        list_werewolves = str([i + 1 for i in alive_werewolves])
        for i in alive_werewolves:
            to_kill = self.input_living_player(
                i,
                "The list of living werewolves is "
                + list_werewolves
                + ". Please pick one living player to kill.",
            )
            if type(to_kill) is int:
                votes[to_kill - 1] += 1
                self.speak(
                    i,
                    "werewolf",
                    "Werewolf "
                    + str(i + 1)
                    + " wants to kill Player "
                    + str(to_kill)
                    + " at this night.",
                )

        highest_vote = 0
        for i in range(0, self.num_players):
            if votes[i] > votes[highest_vote]:
                highest_vote = i
        if votes[highest_vote] > 0:
            self.alive[highest_vote] = False
            self.dead_players_in_this_round.append(highest_vote)
            self.speak(
                "Moderator",
                "werewolf",
                "Werewolves kill player " + str(highest_vote + 1) + " at this night.",
            )

    def seers_reveal_identity(self):
        for i in range(0, self.num_players):
            if self.roles[i] == "seer" and self.alive[i]:
                player = self.input_any_player(
                    i, "You are the seer and can reveal the real role of any player."
                )
                if player:
                    self.speak(
                        "Moderator",
                        "seer",
                        "You choose to reveal the role of player "
                        + str(player)
                        + ". The real role of player "
                        + str(player)
                        + " is "
                        + self.roles[player - 1]
                        + ".",
                    )

    def witch_use_poison(self, witch):
        if self.witches_poison_used[witch]:
            return
        # if a witch is killed by the werewolves in this round, the witch still has a chance to use the poison
        if self.alive[witch] or (witch in self.dead_players_in_this_round):
            player = self.input_living_player(
                witch,
                "You are the witch and you have a chance to kill any living player using the poison. You have only one chance to use the poison throughout the game. If you want to use the poison, output the player number to be killed. Otherwise, output None.",
            )
            if type(player) is int:
                self.alive[player - 1] = False
                self.dead_players_in_this_round.append(player - 1)
                self.witches_poison_used[witch] = True

    def witch_use_antidote(self, witch):
        if self.witches_antidote_used[witch]:
            return
        if self.alive[witch]:
            response = self.player_turn(
                witch,
                "Player "
                + str(self.dead_players_in_this_round[0] + 1)
                + " is just killed by the werewolves. You are the witch and have a chance to rescue the player killed by the werewolves. You have only one chance to use the antidote throughout the game. Do you want to rescue the player? Output Yes or No only, do not output any other words.",
            )
            if "yes" in response.lower():
                self.speak(
                    "Moderator",
                    "none",
                    "Witch "
                    + str(witch + 1)
                    + " rescued the dead player "
                    + str(self.dead_players_in_this_round[0] + 1)
                    + ".",
                )
                self.alive[self.dead_players_in_this_round[0]] = True
                self.dead_players_in_this_round.clear()
                self.witches_antidote_used[witch] = True
        # if a witch is killed by the werewolves in this round, the witch has a chance to self-rescue
        elif witch in self.dead_players_in_this_round:
            response = self.player_turn(
                witch,
                "You are just killed by the werewolves. You are the witch and have a chance to rescue yourself. You have only one chance to use the antidote throughout the game. Do you want to rescue yourself? Output Yes or No only, do not output any other words.",
            )
            if "yes" in response.lower():
                self.speak(
                    "Moderator",
                    "none",
                    "Witch " + str(witch + 1) + " rescued him/herself.",
                )
                self.alive[witch] = True
                self.dead_players_in_this_round.clear()
                self.witches_antidote_used[witch] = True

    def witches_use_poison_or_antidote(self):
        # use antidote
        if len(self.dead_players_in_this_round) > 0:
            for i in range(0, self.num_players):
                if self.roles[i] == "witch":
                    self.witch_use_antidote(i)
        # use poison
        for i in range(0, self.num_players):
            if self.roles[i] == "witch":
                self.witch_use_poison(i)

    def hunter_kill_player(self, player):
        player = self.input_living_player(
            player,
            "You are the hunter and you are just killed. You have the chance to kill one living player who is suspected to be werewolf.",
        )
        if type(player) is int:
            self.alive[player - 1] = False
            self.dead_players_in_this_round.append(player - 1)
            self.speak(
                "Moderator",
                "all",
                "Hunter kills player " + str(player) + " at this night.",
            )

    def input_any_player(self, player, command):
        response = self.player_turn(player, command + " Output the player number only, do not output any other words.")
        player = self.parse_int(response)
        if player is None:
            return None
        if player <= 0 or player > self.num_players:
            print("Invalid response: " + response)
            return None
        return player

    def input_living_player(self, player, command):
        response = self.player_turn(
            player,
            command
            + " The list of living players: "
            + self.list_living_players()
            + ". Output the player number only, do not output any other words.",
        )
        player = self.parse_int(response)
        if player is None:
            return None
        if player <= 0 or player > self.num_players:
            print("Invalid response: " + response)
            return None
        if not self.alive[player - 1]:
            print("Invalid response, player is not alive: " + response)
            return None
        return player

    def announce_deaths(self):
        for player in self.dead_players_in_this_round:
            self.speak("Moderator", "all", "Player " + str(player + 1) + " is dead.")
            self.say_last_word(player)
            if self.roles[player] == "hunter":
                self.hunter_kill_player(player)

    def say_last_word(self, player):
        response = self.player_turn(
            player,
            "You are just killed. Please say some last word to all living players.",
        )
        self.speak(player, "all", response)

    def iterate_living_players(self):
        dead_player = 0
        if len(self.dead_players_in_this_round) > 0:
            dead_player = self.dead_players_in_this_round[0]
        living_players = []
        for i in range(dead_player, self.num_players):
            if self.alive[i]:
                living_players.append(i)
        for i in range(0, dead_player):
            if self.alive[i]:
                living_players.append(i)
        return living_players

    def discuss_werewolves(self):
        for player in self.iterate_living_players():
            command = "It is your turn to discuss who are the werewolves according to the past conversions."
            if self.roles[player] == "werewolf":
                command += " Because you are a werewolf, please hide your identity."
            response = self.player_turn(player, command)
            self.speak(player, "all", response)

    def vote_to_kill(self):
        votes = [0 for i in range(0, self.num_players)]
        for player in self.iterate_living_players():
            to_kill = self.input_living_player(
                player, "Based on the discussion, please pick your suspected living werewolf."
            )
            if not to_kill:
                continue
            votes[to_kill - 1] += 1
            self.speak(
                player,
                "all",
                "Player "
                + str(player + 1)
                + " votes "
                + str(to_kill)
                + " as suspected werewolf.",
            )

        highest_vote = 0
        for i in range(0, self.num_players):
            if votes[i] > votes[highest_vote]:
                highest_vote = i
        if votes[highest_vote] > 0:
            self.alive[highest_vote] = False
            self.dead_players_in_this_round.append(highest_vote)
            self.speak(
                "Moderator",
                "all",
                "Player "
                + str(highest_vote + 1)
                + " is eliminated due to receiving the highest vote as suspected werewolf at this day.",
            )

    def initialize_round(self):
        self.dead_players_in_this_round.clear()
        self.current_day += 1

    def run_game(self):
        while True:
            self.initialize_round()

            # at night
            # werewolves choose the player to kill
            self.werewolves_kill()
            # seers select the player to reveal identity
            self.seers_reveal_identity()
            # witches choose to use poison or antidote
            self.witches_use_poison_or_antidote()
            if self.game_ended():
                return

            # at day
            self.announce_deaths()
            # everyone discuss who are the werewolves
            self.discuss_werewolves()
            # vote the player to kill
            self.vote_to_kill()
            if self.game_ended():
                return


game = Mafia()
game.run_game()
