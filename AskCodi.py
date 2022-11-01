"""
/* Copyright (C) Assistiv AI LTDA - All Rights Reserved
 * This extension project is developed as a part of AskCodi's Sublime extension 
 * AskCodi is a product from Assistiv AI and is a separate financial entity
 * Unauthorized copying or modifying of this project, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Sachin Sharma <sharma@assistiv.ai>, October 2022
 */
"""

import sublime
import sublime_plugin
import webbrowser
import uuid
import time
import threading
from urllib import request
import json
import platform

# globals
ST_VERSION = int(sublime.version())
SETTINGS_FILE = 'AskCodi.sublime-settings'
SETTINGS = {}
FAST_TOKEN = ""
CURRENT_POS = 0


def update_status_bar(message):
    try:
        if message:
            active_window = sublime.active_window()
            if active_window:
                for view in active_window.views():
                    view.set_status('AskCodi', message)
    except:
        pass


def authenticate():
    global SETTINGS, FAST_TOKEN
    if SETTINGS.get("device_id"):
        update_status_bar('Codi is chilling while you code 😴 ')
        return True
    temp_device_id = str(uuid.uuid4())
    webbrowser.open(
        'https://app.askcodi.com/login?ideType=Sublime&deviceId=' + temp_device_id + "&os=" + platform.system() + "-" + platform.machine(),
        new=2)
    start = time.time()
    while FAST_TOKEN == "" and time.time() - start <= 120.0:
        time.sleep(3)
        try:
            # make request and wait
            headers = {'Content-Type': 'application/json',
                       'token': FAST_TOKEN,
                       'deviceid': temp_device_id,
                       'idetype': SETTINGS.get("editor"),
                       'authorization': SETTINGS.get("api_key"),
                       'source': SETTINGS.get("editor") + "-" + SETTINGS.get("version")
                       }
            req = request.Request(SETTINGS.get("url") + "/validateDevice", headers=headers)
            resp = json.load(request.urlopen(req))
            if resp["success"]:
                FAST_TOKEN = resp["token"]
                SETTINGS.set('fast_token', FAST_TOKEN)
                SETTINGS.set('device_id', str(temp_device_id))
                sublime.save_settings(SETTINGS_FILE)
        except:
            pass
    if FAST_TOKEN != "":
        update_status_bar('AskCodi is ready 🤩 ')
    return True


def plugin_loaded():
    global SETTINGS
    SETTINGS = sublime.load_settings(SETTINGS_FILE)
    update_status_bar('Initializing AskCodi... 🥶 ')
    check_thread = threading.Thread(target=authenticate)
    check_thread.start()


def ask_codi_api(app, query, language, context, generated, info, self, edit):
    try:
        headers = {
            'Authorization': SETTINGS.get("api_key"),
            'deviceid': SETTINGS.get("device_id"),
            'idetype': SETTINGS.get("editor"),
            'token': SETTINGS.get("fast_token"),
            'source': SETTINGS.get("editor") + "-" + SETTINGS.get("version"),
            'Content-Type': 'application/json'
        }
        data = {
            "query": query,
            "generated": generated,
            "context": context,
            "fromLanguage1": language,
            "fromLanguage2": "",
            "toLanguage": "",
            "info": info,
            "position": 0
        }
        data = str(json.dumps(data)).encode('utf-8')
        req = request.Request(SETTINGS.get("url") + "/askCodiExtension/" + app, data=data, headers=headers)
        resp = json.load(request.urlopen(req))
        if resp["success"]:
            SETTINGS.set('fast_token', resp["token"])
            if "completion" not in app:
                self.panel = self.view.window().create_output_panel('AskCodi')
                self.panel.run_command('insert', {'characters': resp["message"].strip()})
                self.view.window().run_command('show_panel', {'panel': 'output.AskCodi'})
            else:
                self.view.insert(edit, CURRENT_POS, resp["message"])
            update_status_bar("See suggestion from Codi 🤖 ")
            sublime.status_message('See suggestion from Codi 🤖 ')
        else:
            update_status_bar("AskCodi: " + resp["message"] + " 👻 ")
    except:
        update_status_bar("Couldn't request AskCodi :/ 🤯 ")
        pass


class GenerateCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            context = ""
            if len(selected) > 0:
                for region in self.view.sel():
                    region.begin()
                    context = self.view.substr(sublime.Region(region.begin() - 512, region.begin()))
                language = "." + self.view.window().active_view().file_name().split(".")[-1]
                gc_thread = threading.Thread(target=ask_codi_api,
                                             args=["backend", selected, language, context, "", "", self, edit])
                gc_thread.start()
            else:
                update_status_bar("Please select your query 👾 ")
        else:
            update_status_bar("Authenticating device... 🥶 ")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class ExplainCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                language = "." + self.view.window().active_view().file_name().split(".")[-1]

                window = sublime.active_window()
                if window:
                    def send_req(info):
                        ec_thread = threading.Thread(target=ask_codi_api,
                                                     args=["codeexplainer", selected, language, "", "", info, self,
                                                           edit])
                        ec_thread.start()

                    window.show_input_panel('More information:', "What is the time complexity?", send_req, None, None)
                else:
                    update_status_bar(
                        "Something went wrong, please restart and try again or, contact AskCodi support 😵‍💫 ")
            else:
                update_status_bar("Please select your query 👾 ")
        else:
            update_status_bar("Authenticating device... 🥶 ")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class DocumentCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                language = "." + self.view.window().active_view().file_name().split(".")[-1]
                dc_thread = threading.Thread(target=ask_codi_api,
                                             args=["documentation", selected, language, "", "", "", self, edit])
                dc_thread.start()
            else:
                update_status_bar("Please select your query 👾 ")
        else:
            update_status_bar("Authenticating device... 🥶 ")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class TestCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                language = "." + self.view.window().active_view().file_name().split(".")[-1]
                context = ""
                tc_thread = threading.Thread(target=ask_codi_api,
                                             args=["test", selected, language, context, "", "", self, edit])
                tc_thread.start()
            else:
                update_status_bar("Please select your query 👾 ")
        else:
            update_status_bar("Authenticating device... 🥶 ")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class CompleteCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global CURRENT_POS
        if SETTINGS.get("device_id"):
            context = ""
            for region in self.view.sel():
                CURRENT_POS = region.begin()
                context = self.view.substr(sublime.Region(region.begin() - 512, region.begin()))
            language = "." + self.view.window().active_view().file_name().split(".")[-1]
            ask_codi_api("completion", context, language, "", "", "", self, edit)
        else:
            update_status_bar("Authenticating device... 🥶 ")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


# plugin_loaded is called manually for sublime text version<3
if ST_VERSION < 3000:
    plugin_loaded()
