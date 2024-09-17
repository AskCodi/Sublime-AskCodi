
import sublime
from sublime import Sheet, View, Region, Settings
import json
import threading
from threading import Thread, Event
from .cache import Cache
from typing import Dict, List, Optional, Any
from .askcodi_network_client import initiate_stream, connect_sse
from .output_panel import OutputPanelListener
from .error_logger import UnknownException, WrongUserInputException, present_error, present_unknown_error
from .askcodi import update_status_bar


class AskCodiWorker(Thread):
    def __init__(self, stop_event: Event, chat_id: str, region: Optional[Region], command: str, context: str, instruction: str, view: View, cache: Cache, listner: OutputPanelListener ):
        self.region = region
        self.chat_id = chat_id
        self.command = command
        self.context = context
        # Text from input panel (as `user`)
        self.instruction = instruction # optional
        self.view = view
        # Text input from input panel
        self.settings: Settings = sublime.load_settings("AskCodi.sublime-settings")

        self.stop_event: Event = stop_event
        self.cache = cache
        self.window = sublime.active_window()
        
        if region:
            scope_region = self.window.active_view().scope_name(region.begin())
            self.language = scope_region.split('.')[-1]
        else:
            self.language = ''
        
        if self.view:
            scope_region = view.scope_name(0)  # Assuming you want the scope at the start of the document
            self.language = scope_region.split(' ')[0].split('.')[-1]
        self.listner = listner

        super(AskCodiWorker, self).__init__()

    # This method appears redundant.
    def update_output_panel(self, text_chunk: str):
        self.listner.update_output_view(
            text=text_chunk,
            window=self.window
        )
        
        
    def handle_data(self, stream):
        data = ''
        response = ''
        try:
            while chunk := stream.read():
                data += chunk.decode()
                while '\n\n' in data:
                    end_of_line_index = data.index('\n\n')
                    complete_message = data[:end_of_line_index]
                    data = data[end_of_line_index + 2:]
                    if jsonData := self.parse_message(complete_message):
                        if 'content' in jsonData:
                            response += jsonData['content']
                            self.update_output_panel(jsonData['content'])
                        elif 'end' in jsonData:
                            update_status_bar('[AskCodi]: generation completed.')
                            self.cache.append_to_cache([{'role': 'assistant', 'content': response}])
                            self.update_output_panel("\n\n___________________________________________\n\n")
        except Exception as error:
            raise UnknownException(str(error))
        except Exception as e:
            raise UnknownException(str(e))
            

    def parse_message(self, sse_data):
        try:
            if sse_data.startswith("data: "):
                try:
                    json_part = sse_data[6:].strip()
                    return json.loads(json_part)
                except json.JSONDecodeError as error:
                    raise UnknownException(str(error))
            return None
        except Exception as error:
            raise UnknownException(str(error))
        


    def handle_chat_stream(self, session_id: str):
        try:
            self.update_output_panel("\n## Answer\n\n")
            self.listner.show_panel(window=self.window)
            self.listner.scroll_to_botton(window=self.window)
            thread = threading.Thread(target=connect_sse, args=(self, session_id))
            thread.start()
        except Exception as error:
            raise UnknownException(str(error))
        

    def prepare_for_stream(self):
        wrapped_selection = self.instruction
        if self.region and self.context.strip() != '' :
            scope_region = self.window.active_view().scope_name(self.region.begin())
            scope_name = scope_region.split('.')[-1] # in case of precise selection take the last scope
            wrapped_selection = f"```{scope_name}\n" + self.context + "\n```"
            wrapped_selection = wrapped_selection + "\n\n" + self.instruction + "\n"
        
        
        messages = [{"role": "user", "content": [{"type": "text", "text": self.instruction}]}]

        self.view.sel().clear()
        try:
            result = initiate_stream(
                        self.chat_id,
                        self.command,
                        self.instruction,
                        self.cache.get_cache(),
                        self.context,
                        self.language,
                        self.settings.get('model'),
                        self.settings.get('api_key')
                    )
            
            if result.get('status'):
                self.update_output_panel("\n\n## Question\n\n" + wrapped_selection + "\n\n")
                self.cache.append_to_cache(messages)
                session_id = result.get('sessionId')
                self.handle_chat_stream(session_id)
            else:
                raise UnknownException(result.get('content'))
        except UnknownException as error:
            present_error(title="[AskCodi] Error", error=error)
            return
        except Exception as error:
            present_unknown_error(title="[AskCodi] error", error=error)
            return
        

    def run(self):
        try:
            api_key = self.settings.get('api_key')
            if not api_key or len(api_key)< 5:
                raise WrongUserInputException("No API key provided, you have to set the AskCodi API key into the settings to make things work.")
            else:
                self.prepare_for_stream()
        except WrongUserInputException as error:
            present_error(title="[AskCodi] Error", error=error)
            return
        except UnknownException as error:
            present_error(title="[AskCodi] Error", error=error)
            return
        except Exception as error:
            present_unknown_error(title="[AskCodi] error", error=error)
            return

        
