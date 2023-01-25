"""
/* Copyright (C) Assistiv AI - All Rights Reserved
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
EDITOR = "Sublime"
CODI_VERSION = "3.0"
ST_VERSION = int(sublime.version())
SETTINGS_FILE = 'AskCodi.sublime-settings'
SETTINGS = {}
FAST_TOKEN = ""
CURRENT_POS = 0
KEY = "xkeyaskcodi-aeaf8883-9005-4298-8394-94346f977ed9-37b41a0b-167c-4a12-b639-3aff64e1b88e"
URL = "https://us-central1-askcodi-1a402.cloudfunctions.net"

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
    try:
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
                        'idetype': EDITOR,
                        'authorization': KEY,
                        'source': EDITOR + "-" + CODI_VERSION
                        }
                req = request.Request(URL + "/validateDevice", headers=headers)
                resp = json.load(request.urlopen(req))
                if resp["success"]:
                    FAST_TOKEN = resp["token"]
                    SETTINGS.set('fast_token', FAST_TOKEN)
                    SETTINGS.set('device_id', str(temp_device_id))
                    SETTINGS.set('generate_code', SETTINGS.get("generate_code") if SETTINGS.get("generate_code") else True)
                    SETTINGS.set('explain_code', SETTINGS.get("explain_code") if SETTINGS.get("explain_code") else True)
                    SETTINGS.set('test_code', SETTINGS.get("test_code") if SETTINGS.get("test_code") else True)
                    SETTINGS.set('document_code', SETTINGS.get("document_code") if SETTINGS.get("document_code") else True)
                    SETTINGS.set('complete_code', SETTINGS.get("complete_code") if SETTINGS.get("complete_code") else True)
                    SETTINGS.set('context', SETTINGS.get("context") if SETTINGS.get("context") else True)
                    sublime.save_settings(SETTINGS_FILE)
                    SETTINGS = sublime.load_settings(SETTINGS_FILE)
            except Exception as e:
                pass
        if FAST_TOKEN != "":
            update_status_bar('AskCodi is ready 🤩 ')
    except:
        update_status_bar('Couldn\'t authenticate AskCodi: plugin error')
    return True


def plugin_loaded():
    global SETTINGS
    SETTINGS = sublime.load_settings(SETTINGS_FILE)
    update_status_bar('Initializing AskCodi...')
    check_thread = threading.Thread(target=authenticate)
    check_thread.start()


def ask_codi_api(app, query, context, generated, info, self, edit):
    try:
        update_status_bar("Asking Codi...")
        try:
            language = "." + self.view.window().active_view().file_name().split(".")[-1]
            # self.view.insert(edit, 0, str(language))
        except:
            update_status_bar("Please save the file with a proper language extension first to use AskCodi.")
        headers = {
            'Authorization': KEY,
            'deviceid': SETTINGS.get("device_id"),
            'idetype': EDITOR,
            'token': SETTINGS.get("fast_token"),
            'source': EDITOR + "-" + CODI_VERSION,
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
        req = request.Request(URL + "/askCodiExtension/" + app, data=data, headers=headers)
        resp = json.load(request.urlopen(req))
        if resp["success"]:
            SETTINGS.set('fast_token', resp["token"])
            sublime.save_settings(SETTINGS_FILE)
            if "completion" not in app:
                self.panel = self.view.window().create_output_panel('AskCodi')
                self.panel.run_command('insert', {'characters': resp["message"].strip()})
                self.view.window().run_command('show_panel', {'panel': 'output.AskCodi'})
            else:
                self.view.insert(edit, CURRENT_POS, resp["message"])
            update_status_bar("See suggestion from Codi")
            sublime.status_message('See suggestion from Codi')
        else:
            update_status_bar("AskCodi: " + resp["message"])
    except Exception as e:
        self.view.insert(edit, CURRENT_POS, str(e))
        update_status_bar("Couldn't request AskCodi.")
        pass


class GenerateCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            if SETTINGS.get("generate_code"):
                sel = self.view.sel()[0]
                selected = self.view.substr(sel)
                context = ""
                if len(selected) > 0:
                    for region in self.view.sel():
                        region.begin()
                        context = self.view.substr(sublime.Region(region.begin() - 512, region.begin()))
                    gc_thread = threading.Thread(target=ask_codi_api,
                                                args=["backend", selected, context, "", "", self, edit])
                    gc_thread.start()
                else:
                    update_status_bar("Please select your query.")
            else:
                update_status_bar("Please check user settings for AskCodi for generate_code setting.")
        else:
            update_status_bar("Authenticating device...")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class ExplainCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            if SETTINGS.get("explain_code"):
                sel = self.view.sel()[0]
                selected = self.view.substr(sel)
                if len(selected) > 0:
                    window = sublime.active_window()
                    if window:
                        def send_req(info):
                            ec_thread = threading.Thread(target=ask_codi_api,
                                                        args=["codeexplainer", selected, "", "", info, self,
                                                            edit])
                            ec_thread.start()

                        window.show_input_panel('More information:', "What is the time complexity?", send_req, None, None)
                    else:
                        update_status_bar(
                            "Something went wrong, please restart and try again or, contact AskCodi support.")
                else:
                    update_status_bar("Please select your query.")
            else:
                update_status_bar("Please check user settings for AskCodi for explain_code setting.")
        else:
            update_status_bar("Authenticating device...")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class DocumentCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            if SETTINGS.get("document_code"):
                sel = self.view.sel()[0]
                selected = self.view.substr(sel)
                if len(selected) > 0:
                    dc_thread = threading.Thread(target=ask_codi_api,
                                                args=["documentation", selected, "", "", "", self, edit])
                    dc_thread.start()
                else:
                    update_status_bar("Please select your query.")
            else:
                update_status_bar("Please check user settings for AskCodi for document_code setting.")
        else:
            update_status_bar("Authenticating device...")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class TestCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("device_id"):
            if SETTINGS.get("test_code"):
                sel = self.view.sel()[0]
                selected = self.view.substr(sel)
                if len(selected) > 0:
                    context = ""
                    tc_thread = threading.Thread(target=ask_codi_api,
                                                args=["test", selected, context, "", "", self, edit])
                    tc_thread.start()
                else:
                    update_status_bar("Please select your query.")
            else:
                update_status_bar("Please check user settings for AskCodi for test_code setting.")
        else:
            update_status_bar("Authenticating device...")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


class CompleteCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global CURRENT_POS
        if SETTINGS.get("device_id"):
            if SETTINGS.get("complete_code") and SETTINGS.get("context"):
                context = ""
                for region in self.view.sel():
                    CURRENT_POS = region.begin()
                    context = self.view.substr(sublime.Region(region.begin() - 512, region.begin()))
                if len(context) > 0:
                    ask_codi_api("completion", context, "", "", "", self, edit)
                else:
                    update_status_bar("Please provide some context.")
            else:
                update_status_bar("Please check user settings for AskCodi for complete_code and context settings.")
        else:
            update_status_bar("Authenticating device...")
            download_thread = threading.Thread(target=authenticate)
            download_thread.start()


# plugin_loaded is called manually for sublime text version<3
if ST_VERSION < 3000:
    plugin_loaded()
