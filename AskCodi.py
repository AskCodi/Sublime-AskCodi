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
import threading
from urllib import request
import urllib
import json
import mdpopups
import textwrap


# globals
EDITOR = "Sublime"
CODI_VERSION = "4.2"
ST_VERSION = int(sublime.version())
SETTINGS_FILE = 'AskCodi.sublime-settings'
SETTINGS = {}
URL = "https://app.askcodi.com/api/askcodi-extension/"

class Constants:
    api_key = '' 
    code = ""

CSS_CLASS_NAME = "askcodi-popup"
CSS = """
    html {{
        --askcodi-accept-foreground: var(--foreground);
        --askcodi-accept-background: var(--background);
        --askcodi-accept-border: var(--purplish);
        --askcodi-reject-foreground: var(--foreground);
        --askcodi-reject-background: var(--background);
        --askcodi-reject-border: var(--yellowish);
        --askcodi-copy-foreground: var(--foreground);
        --askcodi-copy-background: var(--background);
        --askcodi-copy-border: var(--greenish);
    }}

    .{class_name} {{
        margin: 1rem 0.5rem 0 0.5rem;
    }}

    .{class_name} .header {{
        display: block;
        margin-bottom: 1rem;
    }}

    .{class_name} a {{
        border-radius: 3px;
        border-style: solid;
        border-width: 1px;
        display: inline;
        padding: 5;
        text-decoration: none;
    }}

    .{class_name} a.accept {{
        background: var(--askcodi-accept-background);
        border-color: var(--askcodi-accept-border);
        color: var(--askcodi-accept-foreground);
    }}

    .{class_name} a.accept i {{
        color: var(--askcodi-accept-border);
    }}

    .{class_name} a.reject {{
        background: var(--askcodi-reject-background);
        border-color: var(--askcodi-reject-border);
        color: var(--askcodi-reject-foreground);
    }}

    .{class_name} a.reject i {{
        color: var(--askcodi-reject-border);
    }}

    .{class_name} a.copy {{
        background: var(--askcodi-copy-background);
        border-color: var(--askcodi-copy-border);
        color: var(--askcodi-copy-foreground);
    }}

    .{class_name} a.copy i {{
        color: var(--askcodi-copy-border);
    }}
    """.format(
        class_name=CSS_CLASS_NAME
    )

COMPLETION_TEMPLATE = textwrap.dedent(
        """
        <div class="header">{header_items}</div>
        ``````
        {code}
        ``````
        """
    )

header_items = [
                    '<a class="accept" title="Insert Code" href="subl:insert_code"><i>✓</i> Insert</a>',
                    '<a class="reject" title="Reject Code" href="subl:reject_code"><i>×</i> Reject</a>',
                    '<a class="copy" title="Copy Code" href="subl:copy_code"><i>♢</i> Copy</a>',
                    ]

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


Constants.api_key = ApiKey()


def prompt_api_key():
    if Constants.api_key.read():
        return True

    window = sublime.active_window()
    if window:
        def got_key(text):
            # if text:
                Constants.api_key.write(text)
        window.show_input_panel('[AskCodi]: Enter your AskCodi api key:', '', got_key, None, None)
        return True
    else:
        log(ERROR, '[AskCodi]: Could not prompt for api key because no window found.')
        return False


def plugin_loaded():
    global SETTINGS
    settings_exist = False
    SETTINGS = sublime.load_settings(SETTINGS_FILE)
    for file in sublime.find_resources("AskCodi.sublime-settings"):
        if 'Packages/User' in file:
            settings_exist = True
            break

    if not settings_exist:
        SETTINGS.set('api_key', '')
        SETTINGS.set('model', 'Base')
        SETTINGS.set('generate_code', True)
        SETTINGS.set('explain_code', True)
        SETTINGS.set('test_code', True)
        SETTINGS.set('document_code', True)
        SETTINGS.set('complete_code', True)
        SETTINGS.set('context', True)
        sublime.save_settings(SETTINGS_FILE)
    
    SETTINGS = sublime.load_settings(SETTINGS_FILE)

    update_status_bar('[AskCodi]: Initializing AskCodi...')
    if not prompt_api_key():
        set_timeout(after_loaded, 0.5)




def ask_codi_api(app, query, context, self, edit):
    try:
        # if not prompt_api_key():
        #     set_timeout(after_loaded, 0.5)
        update_status_bar("[AskCodi]: Asking Codi...")
        try:
            language = "." + self.view.window().active_view().file_name().split(".")[-1]
        except:
            language = ""
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
            "model": SETTINGS.get("model")
        }
        data = json.dumps(data).encode('utf-8')
        try:
            req = request.Request(URL, data=data, headers=headers)
            response = request.urlopen(req).read().decode('utf-8')
        
            # parse json response
            resp = json.loads(response)

            if (resp["status"]):
                content = COMPLETION_TEMPLATE.format(
                        header_items=" &nbsp;".join(header_items),
                        code=textwrap.dedent(resp["message"]),
                        )

                mdpopups.show_popup(
                    view=self.view,
                    content=content,
                    md=True,
                    css=CSS,
                    layout=sublime.LAYOUT_INLINE,
                    flags=sublime.COOPERATE_WITH_AUTO_COMPLETE,
                    max_width=640,
                    max_height=640,
                    wrapper_class=CSS_CLASS_NAME,
                    )

                Constants.code = textwrap.dedent(resp["message"])
                if len(Constants.code.split("```")) > 1:
                    Constants.code= Constants.code.split("```")[1]
                update_status_bar("[AskCodi]: See suggestion from Codi")
            else:
                update_status_bar("AskCodi: " + resp["message"])
        except urllib.error.HTTPError as e:
            update_status_bar("[AskCodi]: " + json.loads(e.read().decode('utf-8'))["message"])
            if e.code == 401:
                prompt_api_key()

    except Exception as e:
        # print(e)
        # update_status_bar(str(e))
        update_status_bar("AskCodi: Couldn't complete request.")
        pass


class GenerateCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("generate_code"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            context = ""
            if len(selected) > 0:
                if(SETTINGS.get("context")):
                    for region in self.view.sel():
                        region.begin()
                        context = self.view.substr(sublime.Region(region.begin() - 1024, region.begin()))
                gc_thread = threading.Thread(target=ask_codi_api,
                                            args=["Generate", selected, context.strip(), self, edit])
                gc_thread.start()
            else:
                update_status_bar("[AskCodi]: Please select your query.")
        else:
            update_status_bar("[AskCodi]: Please enable generate code from settings...")


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
                update_status_bar("[AskCodi]: Please select your query.")
        else:
            update_status_bar("[AskCodi]: Please check user settings for AskCodi for explain_code setting.")


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
                update_status_bar("[AskCodi]: Please select your query.")
        else:
            update_status_bar("[AskCodi]: Please check user settings for AskCodi for document_code setting.")


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
                update_status_bar("[AskCodi]: Please select your query.")
        else:
            update_status_bar("[AskCodi]: Please check user settings for AskCodi for test_code setting.")



class CompleteCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if SETTINGS.get("complete_code") and SETTINGS.get("context"):
            sel = self.view.sel()[0]
            selected = self.view.substr(sel)
            context = ""
            for region in self.view.sel():
                    region.begin()
                    context = self.view.substr(sublime.Region(region.begin() - 1024, region.begin()))
            tc_thread = threading.Thread(target=ask_codi_api,
                                        args=["Complete", context.strip(), "", self, edit])
            tc_thread.start()
        else:
            update_status_bar("[AskCodi]: Please check user settings for AskCodi for complete_code setting.")


class InsertCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mdpopups.hide_popup(self.view)
        source_line_region = self.view.line(sublime.Region(*self.view.sel()[0].to_tuple()))
        self.view.insert(edit, source_line_region.end(), Constants.code)
        self.view.show(self.view.sel(), show_surrounds=False, animate=True)

        update_status_bar("[AskCodi]: code inserted")


class RejectCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mdpopups.hide_popup(self.view)
        Constants.code = ""
        update_status_bar("[AskCodi]: code rejected.")


class CopyCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mdpopups.hide_popup(self.view)
        sublime.set_clipboard(Constants.code)
        Constants.code = ""
        update_status_bar("[AskCodi]: code copied.")



# plugin_loaded is called manually for sublime text version<3
if ST_VERSION < 3000:
    plugin_loaded()
