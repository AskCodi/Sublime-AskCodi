"""
/* Copyright (C) Assistiv AI - All Rights Reserved
 * This extension project is developed as a part of AskCodi's Sublime extension 
 * AskCodi is a product from Assistiv AI and is a separate financial entity
 * Unauthorized copying or modifying of this project, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Sachin Sharma <sharma@assistiv.ai>, October 2022
 */
"""

import os
import uuid
from threading import Event
from typing import Any, Dict, List, Optional

import sublime
from sublime import Edit, Region, Settings, Sheet, View
from sublime_plugin import EventListener, TextCommand

import threading
from .cache import Cache
from .askcodi_worker import AskCodiWorker
from .output_panel import OutputPanelListener
from .askcodi_network_client import get_models
from .error_logger import WrongUserInputException, UnknownException, present_error


# globals
ST_VERSION = int(sublime.version())
settings: Optional[Settings] = None
cache = Cache()
listner = OutputPanelListener(markdown=True, cache=cache)
chat_id = str(uuid.uuid4())


class Chat(TextCommand):
    stop_event: Event = Event()
    worker_thread: Optional[AskCodiWorker] = None
    # cache = None

    def on_input(self, region: Optional[Region], context: str, view: View, instruction: str):
        from .askcodi_worker import AskCodiWorker

        Chat.stop_worker()  # Stop any existing worker before starting a new one
        Chat.stop_event.clear()
        update_status_bar('[AskCodi]: Chat initiated with Codi!!')
        Chat.worker_thread = AskCodiWorker(stop_event=self.stop_event, chat_id=chat_id, region=region, command='code-generator', context=context, view=view, instruction=instruction, cache=cache, listner=listner)
        Chat.worker_thread.start()

    def run(self, edit):
        if not settings:
            return  # Abort if settings are not loaded yet

        # get selected text
        region: Optional[Region] = None
        context: Optional[str] = ""
        for region in self.view.sel():
            if not region.empty():
                context += self.view.substr(region) + "\n"

        _ = sublime.active_window().show_input_panel(
                    "Question: ",
                    "",
                    lambda user_input: self.on_input(
                        region=region if region else None,
                        context=context,
                        view=self.view,
                        instruction=user_input,
                        # listner=listner
                    ),
                    None,
                    None,
                )

    @classmethod
    def stop_worker(cls):
        if cls.worker_thread and cls.worker_thread.is_alive():
            cls.stop_event.set()  # Signal the thread to stop
            cls.worker_thread = None


class GenerateCode(TextCommand):
    stop_event: Event = Event()
    worker_thread: Optional[AskCodiWorker] = None

    def on_input(self, region: Optional[Region], context: str, view: View, instruction: str):
        from .askcodi_worker import AskCodiWorker

        Chat.stop_worker()  # Stop any existing worker before starting a new one
        Chat.stop_event.clear()

        Chat.worker_thread = AskCodiWorker(stop_event=self.stop_event, chat_id=chat_id, region=region, command='code-generator', context=context, view=view, instruction=instruction, cache=cache, listner=listner)
        Chat.worker_thread.start()
        update_status_bar('[AskCodi]: Generate code initiated with Codi!!')

    def run(self, edit):
        if not settings:
            return  # Abort if settings are not loaded yet
        
        try:
            region: Optional[Region] = None
            context: Optional[str] = ""
            instruction: Optional[str] = ""
            
            for region in self.view.sel():
                context += self.view.substr(sublime.Region(region.begin() - 1024, region.begin()))  + "\n"
                if not region.empty():
                    instruction += self.view.substr(region) + "\n"

            if len(instruction) > 0:
                self.on_input(region=region if region else None,
                                context=context,
                                view=self.view,
                                instruction=instruction
                            )
            else:
                raise WrongUserInputException("Please select your query on the editor to use Generate Code app. The query can be a comment or a statement")
        except WrongUserInputException as error:
            present_error(title="[AskCodi] Info", error=error)
            return

    @classmethod
    def stop_worker(cls):
        if cls.worker_thread and cls.worker_thread.is_alive():
            cls.stop_event.set()  # Signal the thread to stop
            cls.worker_thread = None
    
class ExplainCode(TextCommand):
    stop_event: Event = Event()
    worker_thread: Optional[AskCodiWorker] = None

    def on_input(self, region: Optional[Region], context: str, view: View, instruction: str):
        from .askcodi_worker import AskCodiWorker

        Chat.stop_worker()  # Stop any existing worker before starting a new one
        Chat.stop_event.clear()

        Chat.worker_thread = AskCodiWorker(stop_event=self.stop_event, chat_id=chat_id, region=region, command='code-explainer', context=context, view=view, instruction=instruction, cache=cache, listner=listner)
        Chat.worker_thread.start()
        update_status_bar('[AskCodi]: Explain code initiated with Codi!!')

    def run(self, edit):
        if not settings:
            return  # Abort if settings are not loaded yet
        
        try:
            region: Optional[Region] = None
            instruction: Optional[str] = ""
            for region in self.view.sel():
                if not region.empty():
                    instruction += self.view.substr(region) + "\n"

            if len(instruction) > 0:
                self.on_input(region=region if region else None,
                                context='',
                                view=self.view,
                                instruction=instruction
                            )
            else:
                raise WrongUserInputException("Please select your query on the editor to use Explain Code app.")
        except WrongUserInputException as error:
            present_error(title="[AskCodi] Info", error=error)
            return

    @classmethod
    def stop_worker(cls):
        if cls.worker_thread and cls.worker_thread.is_alive():
            cls.stop_event.set()  # Signal the thread to stop
            cls.worker_thread = None


class DocumentCode(TextCommand):
    stop_event: Event = Event()
    worker_thread: Optional[AskCodiWorker] = None

    def on_input(self, region: Optional[Region], context: str, view: View, instruction: str):
        from .askcodi_worker import AskCodiWorker

        Chat.stop_worker()  # Stop any existing worker before starting a new one
        Chat.stop_event.clear()

        Chat.worker_thread = AskCodiWorker(stop_event=self.stop_event, chat_id=chat_id, region=region, command='code-documentation', context=context, view=view, instruction=instruction, cache=cache, listner=listner)
        Chat.worker_thread.start()
        update_status_bar('[AskCodi]: Document code initiated with Codi!!')

    def run(self, edit):
        if not settings:
            return  # Abort if settings are not loaded yet
        
        try:
            region: Optional[Region] = None
            instruction: Optional[str] = ""
            for region in self.view.sel():
                if not region.empty():
                    instruction += self.view.substr(region) + "\n"

            if len(instruction) > 0:
                self.on_input(region=region if region else None,
                                context='',
                                view=self.view,
                                instruction=instruction
                            )
            else:
                raise WrongUserInputException("Please select your query on the editor to use Document Code app.")
        except WrongUserInputException as error:
            present_error(title="[AskCodi] Info", error=error)
            return

    @classmethod
    def stop_worker(cls):
        if cls.worker_thread and cls.worker_thread.is_alive():
            cls.stop_event.set()  # Signal the thread to stop
            cls.worker_thread = None
            

class UnitTests(TextCommand):
    stop_event: Event = Event()
    worker_thread: Optional[AskCodiWorker] = None

    def on_input(self, region: Optional[Region], context: str, view: View, instruction: str):
        from .askcodi_worker import AskCodiWorker

        Chat.stop_worker()  # Stop any existing worker before starting a new one
        Chat.stop_event.clear()

        Chat.worker_thread = AskCodiWorker(stop_event=self.stop_event, chat_id=chat_id, region=region, command='unit-tests-writer', context=context, view=view, instruction=instruction, cache=cache, listner=listner)
        Chat.worker_thread.start()
        update_status_bar('[AskCodi]: Unit tests initiated with Codi!!')

    def run(self, edit):
        if not settings:
            return  # Abort if settings are not loaded yet
        
        try:
            region: Optional[Region] = None
            instruction: Optional[str] = ""
            for region in self.view.sel():
                if not region.empty():
                    instruction += self.view.substr(region) + "\n"

            if len(instruction) > 0:
                self.on_input(region=region if region else None,
                                context='',
                                view=self.view,
                                instruction=instruction
                            )
            else:
                raise WrongUserInputException("Please select your query on the editor to use Unit Tests app.")
        except WrongUserInputException as error:
            present_error(title="[AskCodi] Info", error=error)
            return

    @classmethod
    def stop_worker(cls):
        if cls.worker_thread and cls.worker_thread.is_alive():
            cls.stop_event.set()  # Signal the thread to stop
            cls.worker_thread = None
                      

class OpenChat(TextCommand):
    def run(self, edit):
        # listner.create_new_tab(window=sublime.active_window())
        exists = listner.check_output_view_(window=sublime.active_window())
        if not exists:
            listner.create_new_tab(window=sublime.active_window())
        listner.refresh_output_panel(window=sublime.active_window())
        listner.show_panel(window=sublime.active_window())
        
        
class ResetChatHistory(TextCommand):
    def run(self, edit):
        global chat_id
        chat_id = str(uuid.uuid4())
        cache.clear_cache()
        listner.refresh_output_panel(sublime.active_window())
     

class SetApiKey(TextCommand):
    def run(self, edit):
        prompt_api_key()
            
            
class SelectModel(TextCommand):
    def run(self, edit):
        try:
            self.items = get_models(settings.get('api_key'))
            # self.items = ["Option 1", "Option 2", "Option 3", "Option 4"]
            window = sublime.active_window()
            # Show the quick panel (dropdown)
            window.show_quick_panel(self.items, self.on_done)
        except UnknownException as error:
            present_error(title="[AskCodi] Error", error=error)
            return
        

    def on_done(self, index):
        # This method is called when a user selects an item
        if index == -1:
            present_error(title="[AskCodi] Info", error="No model option selected. Using previously set default model.")
        else:
            handle_settings = HandleSettings()
            handle_settings.write('model', self.items[index])
    
    
def plugin_loaded():
    global settings
    update_status_bar('[AskCodi]: Initializing AskCodi...')
    handle_settings = HandleSettings()
    handle_settings.read()
    


def prompt_api_key():
    window = sublime.active_window()
    if window:
        def add_key(text):
            handle_settings = HandleSettings()
            handle_settings.write('api_key', text)
        window.show_input_panel('[AskCodi]: API key:', '', add_key, None, None)
    else:
        present_error(title="[AskCodi] Error", error="Could not prompt for API key, you have to set the API key into the settings to make things work.")
        return
    
    
def update_status_bar(message):
    try:
        if message:
            active_window = sublime.active_window()
            if active_window:
                for view in active_window.views():
                    view.set_status('AskCodi', message)
    except:
        pass

        
class HandleSettings(object):
    _key = None

    def read(self):
        global settings
        settings = sublime.load_settings('AskCodi.sublime-settings')
        for file in sublime.find_resources("AskCodi.sublime-settings"):
            if 'Packages/User' in file:
                settings_exist = True
                break

        if not settings_exist:
            settings.set('api_key', '')
            settings.set('model', 'Base')
            sublime.save_settings('AskCodi.sublime-settings')
            prompt_api_key()
        else:
            api_key = self.settings.get('api_key')
            model = self.settings.get('model')
            change = False
            if (not api_key or len(api_key)< 5):
                settings.set('api_key', '')
                change = True
                prompt_api_key()
            if (not model):
                settings.set('model', 'Base')
                change = True
            if change:
                sublime.save_settings('AskCodi.sublime-settings')
                
        settings = sublime.load_settings('AskCodi.sublime-settings')
        api_key = settings.get('api_key')
        if not api_key or len(api_key)< 5:
            prompt_api_key()
        else:
            update_status_bar('[AskCodi]: Ask Codi!!')

    def write(self, key, value):
        global settings
        settings = sublime.load_settings('AskCodi.sublime-settings')
        settings.set(key, str(value))
        sublime.save_settings('AskCodi.sublime-settings')
        

# plugin_loaded is called manually for sublime text version<3
if ST_VERSION < 3000:
    plugin_loaded()
