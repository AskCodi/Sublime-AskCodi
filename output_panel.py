from sublime import Settings, Window, View, load_settings
from sublime_plugin import EventListener, ViewEventListener
from .cache import Cache
from typing import Optional

class OutputPanelListener(EventListener):
    OUTPUT_PANEL_NAME = "AskCodi Chat"

    def __init__(self, markdown: bool = True, cache: Cache = Cache()) -> None:
        self.markdown: bool = markdown
        self.cache = cache
        self.settings: Settings = load_settings("AskCodi.sublime-settings")

        self.gutter_enabled: bool =  True
        self.line_numbers_enabled: bool = False
        self.scroll_past_end: bool = False
        self.reverse_for_tab: bool = False
        super().__init__()

    def create_new_tab(self, window: Window):
        if self.get_active_tab_(window=window):
            self.refresh_output_panel(window=window)
            self.show_panel(window=window)
            return
        
        # Set up a 70:30 vertical split
        # Layouts are defined as rows and cols, and cells use 0-based indexes to define their positions in the grid
        layout = {
            "cols": [0.0, 0.7, 1.0],  # Split at 70%
            "rows": [0.0, 1.0],
            "cells": [
                [0, 0, 1, 1],  # First pane, from top-left to bottom-middle (70% width)
                [1, 0, 2, 1]   # Second pane, from top-middle to bottom-right (30% width)
            ]
        }

        # Apply the new layout
        window.set_layout(layout)

        new_view = window.new_file()
        new_view.set_scratch(True)
        self.setup_common_presentation_style_(new_view, reversed=self.reverse_for_tab)
        new_view.set_name(self.OUTPUT_PANEL_NAME)

        # Move the new view to the second pane (pane index starts from 0)
        window.set_view_index(new_view, 1, 0)  # '1' indicates the second pane, '0' is the position in the second pane

    def get_output_panel_(self, window: Window) -> View:
        # Ensure the layout is set to a 70:30 split
        layout = {
            "cols": [0.0, 0.7, 1.0],  # Split at 70%
            "rows": [0.0, 1.0],
            "cells": [
                [0, 0, 1, 1],  # First pane, from top-left to bottom-middle (70% width)
                [1, 0, 2, 1]   # Second pane, from top-middle to bottom-right (30% width)
            ]
        }
        # Check and set the layout if it's different from the current layout
        current_layout = window.get_layout()
        if current_layout != layout:
            window.set_layout(layout)

        # Try to find an existing view for the output, otherwise create a new one
        output_view = None
        for view in window.views():
            if view.name() == self.OUTPUT_PANEL_NAME:
                output_view = view
                break

        if not output_view:
            output_view = window.new_file()
            output_view.set_scratch(True)
            output_view.set_name(self.OUTPUT_PANEL_NAME)
            window.set_view_index(output_view, 1, 0)  # Move to the second pane

        # Apply common presentation styles to the view
        self.setup_common_presentation_style_(output_view)

        return output_view

    def setup_common_presentation_style_(self, view: View, reversed: bool = False):
        if self.markdown: view.assign_syntax("Packages/Markdown/MultiMarkdown.sublime-syntax")
        scroll_past_end = not self.scroll_past_end if reversed else self.scroll_past_end
        gutter_enabled = not self.gutter_enabled if reversed else self.gutter_enabled
        line_numbers_enabled = not self.line_numbers_enabled if reversed else self.line_numbers_enabled

        view.settings().set("scroll_past_end", scroll_past_end)
        view.settings().set("gutter", gutter_enabled)
        view.settings().set("line_numbers", line_numbers_enabled)
        view.settings().set("set_unsaved_view_name", False)

    def toggle_overscroll(self, window: Window, enabled: bool):
        view = self.get_output_view_(window=window)
        view.settings().set("scroll_past_end", enabled)

    def update_output_view(self, text: str, window: Window):
        view = self.get_output_view_(window=window)
        view.set_read_only(False)
        view.run_command('append', {'characters': text})
        view.set_read_only(True)
        view.set_name(self.OUTPUT_PANEL_NAME)

    def get_output_view_(self, window: Window, reversed: bool = False) -> View:
        view = self.get_active_tab_(window=window) or self.get_output_panel_(window=window)
        return view
    
    def check_output_view_(self, window: Window, reversed: bool = False) -> View:
        for view in window.views():
            if view.name() == self.OUTPUT_PANEL_NAME:
                return True
        return False

    def refresh_output_panel(self, window: Window):
        output_panel = self.get_output_view_(window=window)
        output_panel.set_read_only(False)
        self.clear_output_panel(window)
        print(self.cache.get_cache())
        for line in self.cache.get_cache():
            ## TODO: Make me enumerated, e.g. Question 1, Question 2 etc.
            ## (it's not that easy, since question and answer are the different lines)
            ## FIXME: This logic conflicts with multifile/multimessage request behaviour
            ## it presents ## Question above each message, while has to do it once for a pack.
            if line['role'] == 'user':
                output_panel.run_command('append', {'characters': f'\n\n## Question\n\n'})
                output_panel.run_command('append', {'characters': line['content'][0]['text']})
            elif line['role'] == 'assistant':
                output_panel.run_command('append', {'characters': '\n\n## Answer\n\n'})
                output_panel.run_command('append', {'characters': line['content']})
                output_panel.run_command('append', {'characters':  '\n\n___________________________________________\n\n'})

        output_panel.set_read_only(True)
        output_panel.set_name(self.OUTPUT_PANEL_NAME)
        self.scroll_to_botton(window=window)

    def clear_output_panel(self, window: Window):
        output_panel = self.get_output_view_(window=window)
        output_panel.run_command("select_all")
        output_panel.run_command("right_delete")

    def scroll_to_botton(self, window: Window):
        output_panel = self.get_output_view_(window=window)
        point = output_panel.text_point(__get_number_of_lines__(view=output_panel), 0)
        output_panel.show_at_center(point)

    def get_active_tab_(self, window) -> Optional[View]:
        for view in window.views():
            if view.name() == self.OUTPUT_PANEL_NAME:
                return view

    def show_panel(self, window: Window):
        # Attempt to activate the view with streaming_view_id if it exists
        view = self.get_active_tab_(window) or None
        if view:
            view.set_name(self.OUTPUT_PANEL_NAME)
            window.focus_view(self.get_active_tab_(window))
            return

        window.run_command("show_panel", {"panel": f"output.{self.OUTPUT_PANEL_NAME}"})


def __get_number_of_lines__(view: View) -> int:
        last_line_num = view.rowcol(view.size())[0]
        return last_line_num
