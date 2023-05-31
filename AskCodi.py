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
import urllib
import json
import platform


# globals
EDITOR = "Sublime"
CODI_VERSION = "4.0"
ST_VERSION = int(sublime.version())
SETTINGS_FILE = 'AskCodi.sublime-settings'
SETTINGS = {}
API_KEY = ""
URL = "http://127.0.0.1:3000/api/askcodi-extension/"

def update_status_bar(message):
    try:
        if message:
            active_window = sublime.active_window()
            if active_window:
                for view in active_window.views():
                    view.set_status('AskCodi', message)
    except:
        pass


class ApiKey(object):
    _key = None

    def read(self):
        if self._key:
            return self._key

        key = SETTINGS.get('api_key')
        if key:
            self._key = key
            return self._key

        return self._key

    def write(self, key):
        global SETTINGS
        self._key = key
        SETTINGS.set('api_key', str(key))
        sublime.save_settings(SETTINGS_FILE)


APIKEY = ApiKey()


def prompt_api_key():
    # if APIKEY.read():
    #     return True

    window = sublime.active_window()
    if window:
        def got_key(text):
            if text:
                APIKEY.write(text)
        window.show_input_panel('[AskCodi] Enter your AskCodi api key:', '', got_key, None, None)
        return True
    else:
        log(ERROR, 'Could not prompt for api key because no window found.')
        return False


def plugin_loaded():
    global SETTINGS
    settings_exist = False;
    SETTINGS = sublime.load_settings(SETTINGS_FILE)
    for file in sublime.find_resources("AskCodi.sublime-settings"):
        if 'Packages/User' in file:
            settings_exist = True
            break

    if not settings_exist:
        SETTINGS.set('api_key', '')
        SETTINGS.set('generate_code', True)
        SETTINGS.set('explain_code', True)
        SETTINGS.set('test_code', True)
        SETTINGS.set('document_code', True)
        SETTINGS.set('context', True)
        sublime.save_settings(SETTINGS_FILE)
    
    SETTINGS = sublime.load_settings(SETTINGS_FILE)

    update_status_bar('Initializing AskCodi...')
    if not prompt_api_key():
        set_timeout(after_loaded, 0.5)




def ask_codi_api(app, query, context, self, edit):
    try:
        # if not prompt_api_key():
        #     set_timeout(after_loaded, 0.5)
        update_status_bar("Asking Codi...")
        try:
            language = "." + self.view.window().active_view().file_name().split(".")[-1]
        except:
            update_status_bar("Please save the file with a proper language extension first to use AskCodi.")
        headers = {
            'apikey': SETTINGS.get("api_key"),
            'source': EDITOR,
            'version': CODI_VERSION,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        if context!="":
            messages = [{'role': 'user', 'content': context}, {'role': 'user', 'content': query}]
        else:
            messages = [{'role': 'user', 'content': query}]
        
        data = {
            "messages": messages,
            "language": language,
            "app": app,
        }
        data = json.dumps(data).encode('utf-8')
        try:
            req = request.Request(URL, data=data, headers=headers)
            response = request.urlopen(req).read().decode('utf-8')
            print(response)
        
            # parse json response
            resp = json.loads(response)
            print(resp)
            self.panel = self.view.window().create_output_panel('AskCodi')
            self.panel.run_command('insert', {'characters': str(response)})
            self.view.window().run_command('show_panel', {'panel': 'output.AskCodi'})
            update_status_bar("See suggestion from Codi")
            sublime.status_message('See suggestion from Codi')

            if (resp["status"]):
                self.panel = self.view.window().create_output_panel('AskCodi')
                self.panel.run_command('insert', {'characters': resp["message"]})
                self.view.window().run_command('show_panel', {'panel': 'output.AskCodi'})
                update_status_bar("See suggestion from Codi")
                sublime.status_message('See suggestion from Codi')
            else:
                update_status_bar("AskCodi: " + resp["message"])
        except urllib.error.HTTPError as e:
            update_status_bar("AskCodi: " + json.loads(e.read().decode('utf-8'))["message"])
            if e.code == 401:
                prompt_api_key()

    except Exception as e:
        print(e)
        update_status_bar("AskCodi: Couldn't complete request.")
        pass


class GenerateCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("generate_code"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            context = ""
            if len(selected) > 0:
                for region in self.view.sel():
                    region.begin()
                    context = self.view.substr(sublime.Region(region.begin() - 512, region.begin()))
                # MakeRequest(self.view, "Generate", query, context).start()
                gc_thread = threading.Thread(target=ask_codi_api,
                                            args=["Generate", selected, context.strip(), self, edit])
                gc_thread.start()
            else:
                update_status_bar("Please select your query.")
        else:
            update_status_bar("Please enable generate code from settings...")


class ExplainCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("explain_code"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                ec_thread = threading.Thread(target=ask_codi_api,
                                                    args=["Explain", selected, "", self, edit])
                ec_thread.start()
            else:
                update_status_bar("Please select your query.")
        else:
            update_status_bar("Please check user settings for AskCodi for explain_code setting.")


class DocumentCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("document_code"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                dc_thread = threading.Thread(target=ask_codi_api,
                                            args=["Document", selected, "", self, edit])
                dc_thread.start()
            else:
                update_status_bar("Please select your query.")
        else:
            update_status_bar("Please check user settings for AskCodi for document_code setting.")


class TestCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("test_code"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            if len(selected) > 0:
                context = ""
                tc_thread = threading.Thread(target=ask_codi_api,
                                            args=["Test", selected, context, self, edit])
                tc_thread.start()
            else:
                update_status_bar("Please select your query.")
        else:
            update_status_bar("Please check user settings for AskCodi for test_code setting.")


# plugin_loaded is called manually for sublime text version<3
if ST_VERSION < 3000:
    plugin_loaded()
