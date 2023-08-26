"""The controller which reacts and drives the simulation."""
from typing import Any, Dict, Union

import os
import json
import os

import datetime

from gen_agents.global_methods import find_filenames, check_if_file_exists
from gen_agents.utils import fs_storage, fs_temp_storage, fs_storage_compressed


def load_demo(sim_code, step, play_speed="2") -> Dict[str, Any]:
    move_file = f"{fs_storage_compressed}/{sim_code}/master_movement.json"
    meta_file = f"{fs_storage_compressed}/{sim_code}/meta.json"
    step = int(step)
    play_speed_opt = {"1": 1, "2": 2, "3": 4, "4": 8, "5": 16, "6": 32}
    if play_speed not in play_speed_opt:
        play_speed = 2
    else:
        play_speed = play_speed_opt[play_speed]

    # Loading the basic meta information about the simulation.
    with open(meta_file) as json_file:
        meta = json.load(json_file)

    sec_per_step = meta["sec_per_step"]
    start_datetime = datetime.datetime.strptime(
        meta["start_date"] + " 00:00:00", "%B %d, %Y %H:%M:%S"
    )
    for i in range(step):
        start_datetime += datetime.timedelta(seconds=sec_per_step)
    start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Loading the movement file
    with open(move_file) as json_file:
        raw_all_movement = json.load(json_file)

    # Loading all names of the personas
    persona_names = dict()
    persona_names = []
    persona_names_set = set()
    for p in list(raw_all_movement["0"].keys()):
        persona_names += [
            {
                "original": p,
                "underscore": p.replace(" ", "_"),
                "initial": p[0] + p.split(" ")[-1][0],
            }
        ]
        persona_names_set.add(p)

    # <all_movement> is the main movement variable that we are passing to the
    # frontend. Whereas we use ajax scheme to communicate steps to the frontend
    # during the simulation stage, for this demo, we send all movement
    # information in one step.
    all_movement = dict()

    # Preparing the initial step.
    # <init_prep> sets the locations and descriptions of all agents at the
    # beginning of the demo determined by <step>.
    init_prep = dict()
    for int_key in range(step + 1):
        key = str(int_key)
        val = raw_all_movement[key]
        for p in persona_names_set:
            if p in val:
                init_prep[p] = val[p]
    persona_init_pos = dict()
    for p in persona_names_set:
        persona_init_pos[p.replace(" ", "_")] = init_prep[p]["movement"]
    all_movement[step] = init_prep

    # Finish loading <all_movement>
    for int_key in range(step + 1, len(raw_all_movement.keys())):
        all_movement[int_key] = raw_all_movement[str(int_key)]

    return {
        "sim_code": sim_code,
        "step": step,
        "persona_names": persona_names,
        "persona_init_pos": json.dumps(persona_init_pos),
        "all_movement": json.dumps(all_movement),
        "start_datetime": start_datetime,
        "sec_per_step": sec_per_step,
        "play_speed": play_speed,
        "mode": "demo",
    }


def load_simulation(sim_code: str) -> Dict[str, Any]:
    persona_names = []
    persona_names_set = set()
    for i in find_filenames(f"{fs_storage}/{sim_code}/personas", ""):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)

    persona_init_pos = []
    file_count = []
    for i in find_filenames(f"{fs_storage}/{sim_code}/environment", ".json"):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            file_count += [int(x.split(".")[0])]
    curr_json = f"{fs_storage}/{sim_code}/environment/{str(max(file_count))}.json"
    with open(curr_json) as json_file:
        persona_init_pos_dict = json.load(json_file)
        for key, val in persona_init_pos_dict.items():
            if key in persona_names_set:
                persona_init_pos += [[key, val["x"], val["y"]]]

    return {
        "sim_code": sim_code,
        "persona_names": persona_names,
        "persona_init_pos": persona_init_pos,
        "mode": "simulate",
    }


def load_current_simulation() -> Union[Dict[str, Any], None]:
    f_curr_sim_code = f"{fs_temp_storage}/curr_sim_code.json"
    f_curr_step = f"{fs_temp_storage}/curr_step.json"

    if not check_if_file_exists(f_curr_step):
        return None

    with open(f_curr_sim_code) as json_file:
        sim_code = json.load(json_file)["sim_code"]

    with open(f_curr_step) as json_file:
        step = json.load(json_file)["step"]

    context = load_simulation(sim_code)
    context["step"] = step
    return context


def load_persona_state(sim_code: str, persona_name: str) -> Dict[str, Any]:
    persona_name_underscore = persona_name
    persona_name = " ".join(persona_name.split("_"))
    memory = f"{fs_storage}/{sim_code}/personas/{persona_name}/bootstrap_memory"
    if not os.path.exists(memory):
        memory = f"{fs_storage_compressed}/{sim_code}/personas/{persona_name}/bootstrap_memory"

    with open(memory + "/scratch.json") as json_file:
        scratch = json.load(json_file)

    with open(memory + "/spatial_memory.json") as json_file:
        spatial = json.load(json_file)

    with open(memory + "/associative_memory/nodes.json") as json_file:
        associative = json.load(json_file)

    a_mem_event = []
    a_mem_chat = []
    a_mem_thought = []

    for count in range(len(associative.keys()), 0, -1):
        node_id = f"node_{str(count)}"
        node_details = associative[node_id]

        if node_details["type"] == "event":
            a_mem_event += [node_details]

        elif node_details["type"] == "chat":
            a_mem_chat += [node_details]

        elif node_details["type"] == "thought":
            a_mem_thought += [node_details]

    return {
        "sim_code": sim_code,
        "persona_name": persona_name,
        "persona_name_underscore": persona_name_underscore,
        "scratch": scratch,
        "spatial": spatial,
        "a_mem_event": a_mem_event,
        "a_mem_chat": a_mem_chat,
        "a_mem_thought": a_mem_thought,
    }


def process_environment(env_update: Dict[str, Any]) -> None:
    """
    <FRONTEND to BACKEND>
    This sends the frontend visual world information to the backend server.
    It does this by writing the current environment representation to
    "storage/environment.json" file.
    """
    step = env_update["step"]
    sim_code = env_update["sim_code"]
    environment = env_update["environment"]

    with open(f"{fs_storage}/{sim_code}/environment/{step}.json", "w") as outfile:
        json.dump(environment, outfile, indent=2)


def update_environment(sim_code: str, step: int) -> None:
    """
    <BACKEND to FRONTEND>
    This sends the backend computation of the persona behavior to the frontend
    visual server.
    It does this by reading the new movement information from
    "storage/movement.json" file.
    """
    # f_curr_sim_code = "temp_storage/curr_sim_code.json"
    # with open(f_curr_sim_code) as json_file:
    #   sim_code = json.load(json_file)["sim_code"]

    response_data = {"<step>": -1}
    if check_if_file_exists(f"{fs_storage}/{sim_code}/movement/{step}.json"):
        with open(f"{fs_storage}/{sim_code}/movement/{step}.json") as json_file:
            response_data = json.load(json_file)
        response_data["<step>"] = step
    return response_data


def path_tester_update(camera: Dict[str, Any]) -> None:
    """
    Processing the path and saving it to path_tester_env.json temp storage for
    conducting the path tester.
    """
    camera = camera["camera"]

    with open(f"{fs_temp_storage}/path_tester_env.json", "w") as outfile:
        json.dump(camera, outfile, indent=2)
