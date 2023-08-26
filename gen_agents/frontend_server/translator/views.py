"""
Author: Joon Sung Park (joonspk@stanford.edu)
File: views.py
"""
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import *

from gen_agents import controller


def landing(request):
    context = {}
    template = "landing/landing.html"
    return render(request, template, context)


def demo(request, sim_code, step, play_speed="2"):
    context = controller.load_demo(sim_code, step, play_speed)
    template = "demo/demo.html"
    return render(request, template, context)


def UIST_Demo(request):
    return demo(
        request, "March20_the_ville_n25_UIST_RUN-step-1-141", 2160, play_speed="3"
    )


def home(request):
    context = controller.load_current_simulation()
    if context is None:
        template = "home/error_start_backend.html"
        return render(request, template, {})

    context["mode"] = "simulate"
    template = "home/home.html"
    return render(request, template, context)


def replay(request, sim_code, step):
    context = controller.load_simulation(sim_code)
    context["step"] = int(step)
    context["mode"] = "replay"

    template = "home/home.html"
    return render(request, template, context)


def replay_persona_state(request, sim_code, step, persona_name):
    step = int(step)

    context = controller.load_persona_state(sim_code, persona_name)
    context["step"] = step
    template = "persona_state/persona_state.html"
    return render(request, template, context)


def path_tester(request):
    context = {}
    template = "path_tester/path_tester.html"
    return render(request, template, context)


def process_environment(request):
    """
    <FRONTEND to BACKEND>
    This sends the frontend visual world information to the backend server.
    It does this by writing the current environment representation to
    "storage/environment.json" file.

    ARGS:
      request: Django request
    RETURNS:
      HttpResponse: string confirmation message.
    """
    data = json.loads(request.body)
    controller.process_environment(data)
    return HttpResponse("received")


def update_environment(request):
    """
    <BACKEND to FRONTEND>
    This sends the backend computation of the persona behavior to the frontend
    visual server.
    It does this by reading the new movement information from
    "storage/movement.json" file.

    ARGS:
      request: Django request
    RETURNS:
      HttpResponse
    """
    # f_curr_sim_code = "temp_storage/curr_sim_code.json"
    # with open(f_curr_sim_code) as json_file:
    #   sim_code = json.load(json_file)["sim_code"]

    data = json.loads(request.body)
    response_data = controller.update_environment(data["sim_code"], int(data["step"]))
    return JsonResponse(response_data)


def path_tester_update(request):
    """
    Processing the path and saving it to path_tester_env.json temp storage for
    conducting the path tester.

    ARGS:
      request: Django request
    RETURNS:
      HttpResponse: string confirmation message.
    """
    data = json.loads(request.body)
    controller.path_tester_update(data)
    return HttpResponse("received")
