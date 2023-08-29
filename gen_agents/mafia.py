import os
import openai
import random

num_werewolves = 3
num_villagers = 3
num_seers = 1
num_witches = 1
num_hunters = 1

num_players = num_werewolves + num_villagers + num_seers + num_witches + num_hunters
roles = []

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

roles = generate_roles()
print(roles)
