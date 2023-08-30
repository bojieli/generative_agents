import os
import openai
import random
import re

num_werewolves = 3
num_villagers = 3
num_seers = 1
num_witches = 1
num_hunters = 1

num_players = num_werewolves + num_villagers + num_seers + num_witches + num_hunters
roles = []
alive = []
witches_poison_used = []
witches_antidote_used = []
current_day = 0
speaker_records = []
dead_players_in_this_round = []

def get_completion(system_prompt, previous_rounds):
    messages = [
      { "role": "system", "content": system_prompt }
    ]
    for content in previous_rounds:
        messages.append({ "role": "user", "content": content })

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages=messages
    )

    return completion['choices'][0]['message']['content']

def player_turn(player, command):
    game_intro = """
You are an experienced player of Mafia, a social deduction game. The game models a conflict between two groups: an informed minority (the werewolves) and and an uninformed majority (the villagers, seers, witches and hunters). At the start of the game, each player is secretly assigned a role (werewolf, villager, seer, witch or hunter). The game has two alternating phases: first, a night-phase, during which those with night-killing-powers may covertly kill other players, and second, a day-phase, in which all surviving players debate and vote to eliminate a suspect. The game continues until a faction achieves its win-condition; for the villagers, this means eliminating all the werewolves, while for the werewolves, this means eliminating either all the villagers or all the seers, witches and hunters.

At night, all players close their eyes. First, all werewolves acknowledge their accomplices, vote to pick a victim, and then close their eyes. Next, the seer open eyes and pick a player to reveal his/her real identity (the moderator only tells the identity to the seer but does not make it public), and then close eyes. Finally, the witches open eyes and know from the moderator which player is killed by the werewolves, and may decide to rescue him/her using the antidote. The witches may also decide to kill a player using the poison. Each witch has only one bottle of antidote and only one bottle of poison throughout the game.

At day, all players open their eyes. The moderator first announces which player is dead and the dead player may leave a last word. If the dead player is the hunter, the hunter may choose to kill one player, or choose to not kill anyone. Then, from the next living player of the dead player, every living player has a chance to discuss who are the werewolves. A player may accuse someone of being a werewolf and prompt others to vote to eliminate them. The real werewolves may lie to protect their identities. After the discussion, every living player has one vote to eliminate a player who is suspected to be a werewolf.
    """
    game_intro += "In this instance of Mafia, there are " + str(num_werewolves) + " werewolves, " + str(num_villagers) + " villagers, " + str(num_seers) + " seers, " + str(num_witches) + " witches, and " + str(num_hunters) + " hunters. The players are numbered from 1 to " + str(num_players).

    previous_rounds = []
    for record in speaker_records:
        if record['speaker']
    previous_rounds.append({ "role": "system", "content": "You are player " + str(player + 1) + ", your role is " + roles[player] + ". Now it is your turn. " + command })
    response = get_completion(game_intro, previous_rounds)
    return response

def parse_int(response):
    match = re.search('[0-9]+', response)
    if not match:
        return None
    return int(match.group(0))

def list_living_players():
    return str([ i+1 for i in range(0, num_players) if alive[i] ])

def generate_roles():
    roles = [i for i in range(0, num_players)]
    random.shuffle(roles)
    for i in range(0, num_players):
        num = roles[i]
        if num < num_werewolves:
            roles[i] = 'werewolf'
            continue
        else:
            num -= num_werewolves
        if num < num_villagers:
            roles[i] = 'villager'
            continue
        else:
            num -= num_villagers
        if num < num_seers:
            roles[i] = 'seer'
            continue
        else:
            num -= num_seers
        if num < num_witches:
            roles[i] = 'witch'
            continue
        else:
            num -= num_witches
        if num < num_hunters:
            roles[i] = 'hunter'
            continue
        else:
            raise 'Unknown role exception'
    return roles

def initialize_status():
    alive = [True for i in range(0, num_players)]
    witches_poison_used = [False for i in range(0, num_witches)]
    witches_antidote_used = [False for i in range(0, num_witches)]

def game_ended():
    num_alive_villagers = 0
    for i in range(0, num_players):
        if roles[i] == 'villager' and alive[i]:
            num_alive_villagers += 1
    if num_alive_villagers == 0:
        print('All villagers are dead. Game ended. The werewolves win.')
        return True

    num_alive_special_roles = 0
    for i in range(0, num_players):
        if roles[i] in ['seer', 'witch', 'hunter'] and alive[i]:
            num_alive_special_roles += 1
    if num_alive_special_roles == 0:
        print('All special roles are dead. Game ended. The werewolves win.')

    num_alive_werewolves = 0
    for i in range(0, num_players):
        if roles[i] == '':
    return False

def speak(speaker, visibility, content):
    print(speaker + ': ' + content)
    speaker_records.append({ 'speaker': speaker, 'visibility': visibility, 'content': content })

def werewolves_kill():
    votes = [0 for i in range(0, num_players)]
    for i in range(0, num_players):
        if roles[i] == 'werewolf' and alive[i]:
            player = input_living_player(player, 'Please pick on e living player to kill.')
            if player is int:
                votes[player - 1] += 1
                speak(i, 'werewolves', 'Werewolf wants to kill ' + str(player) + ' at this night')

    highest_vote = 0
    for i in range(0, num_players):
        if votes[i] > votes[highest_vote]
            highest_vote = i
    if votes[highest_vote] > 0:
        alive[highest_vote] = False
        dead_players_in_this_round.append(highest_vote)
        speak('Moderator', 'werewolves', 'Werewolves kill player ' + str(highest_vote + 1) + ' at this night.')

def seers_reveal_identity():
    pass

def witches_use_poison_or_antidote():
    pass

def hunter_kill_player(player):
    response = input_living_player("You are the hunter and you are just killed. You have the chance to kill one living player who is suspected to be werewolf.")

def input_living_player(player):
    response = player_turn(player, command + " The list of living players: " + list_living_players() + ". Output the player number only.")
    player = parse_int(response)
    if player == None:
        print('Invalid response: ' + response)
        return None
    if player <= 0 or player >= num_players:
        print('Invalid response: ' + response)
        return None
    if not alive[player - 1]:
        print('Invalid response, player is not alive: ' + response)
        return None
    return player

def announce_deaths():
    for player in dead_players_in_this_round:
        if roles[player] == 'hunter':
            hunter_kill_player(player)
        speak('Moderator', 'all', 'Player ' + str(player + 1) + ' is dead.')
        say_last_word(player)
    dead_players_in_this_round = []

def say_last_word(player):
    response = player_turn(player, "You are just killed. Please say some last word to all living players.")
    speak(player, 'all', response)

def discuss_werewolves():
    pass

def vote_to_kill():
    pass

def run_game():
    while True:
        # at night
        # werewolves choose the player to kill
        werewolves_kill()
        # seers select the player to reveal identity
        seers_reveal_identity()
        # witches choose to use poison or antidote
        witches_use_poison_or_antidote()
        if game_ended():
            return

        # at day
        announce_deaths()
        # dead player say last word
        say_last_word()
        # everyone discuss who are the werewolves
        discuss_werewolves()
        # vote the player to kill
        vote_to_kill()
        announce_deaths()
        if game_ended():
            return

roles = generate_roles()
print(roles)
initialize_status()
run_game()
