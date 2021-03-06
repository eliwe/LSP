import mdpopups
import sublime
import sublime_plugin
import webbrowser

from .core.settings import ClientConfig, client_configs
from .core.configurations import (
    create_window_configs,
    get_global_client_config
)
from .core.registry import config_for_scope, windows
from .core.events import global_events
from .core.workspace import enable_in_project, disable_in_project


def detect_supportable_view(view: sublime.View):
    config = config_for_scope(view)
    if not config:
        available_config = get_global_client_config(view)
        if available_config:
            show_enable_config(view, available_config)


global_events.subscribe("view.on_load_async", detect_supportable_view)
global_events.subscribe("view.on_activated_async", detect_supportable_view)


def extract_syntax_name(syntax_file: str) -> str:
    return syntax_file.split('/')[-1].split('.')[0]


def show_enable_config(view: sublime.View, config: ClientConfig):
    syntax = str(view.settings().get("syntax", ""))
    message = "LSP has found a language server for {}. Run \"Setup Language Server\" to start using it".format(
        extract_syntax_name(syntax)
    )
    window = view.window()
    if window:
        window.status_message(message)


class LspEnableLanguageServerGloballyCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        available_config = get_global_client_config(view)
        if available_config:
            client_configs.enable(available_config.name)
            wm = windows.lookup(self.window)
            wm.update_configs(create_window_configs(self.window))
            sublime.set_timeout_async(lambda: wm.activate_view(view), 500)
            self.window.status_message("{} enabled, starting server...".format(available_config.name))
            return

        self.window.status_message("No config available to enable")


class LspEnableLanguageServerInProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        wm = windows.lookup(self.window)
        config = wm._configs.scope_config(view)
        if config:
            enable_in_project(self.window, config.name)
            wm.update_configs(create_window_configs(self.window))
            sublime.set_timeout_async(lambda: wm.activate_view(view), 500)
            self.window.status_message("{} enabled, starting server...".format(config.name))
        else:
            self.window.status_message("No config available to enable")


class LspDisableLanguageServerGloballyCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        global_config = get_global_client_config(view)
        if global_config:
            client_configs.disable(global_config.name)
            wm = windows.lookup(self.window)
            wm.update_configs(create_window_configs(self.window))
            sublime.set_timeout_async(lambda: wm.end_sessions(), 500)
            self.window.status_message("{} disabled, shutting down server...".format(global_config.name))
            return

        self.window.status_message("No config available to disable")


class LspDisableLanguageServerInProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        wm = windows.lookup(self.window)
        config = wm._configs.scope_config(view)
        if config:
            disable_in_project(self.window, config.name)
            wm.update_configs(create_window_configs(self.window))
            wm.end_sessions()
        else:
            self.window.status_message("No config available to disable")


supported_syntax_template = '''
Installation steps:

* Open the [LSP documentation](https://lsp.readthedocs.io)
* Read the instructions for {}
* Install the language server on your system
* Choose an option below to start the server

Enable: [Globally](#enable_globally) | [This Project Only](#enable_project)
'''

unsupported_syntax_template = """
*LSP has no built-in configuration for a {} language server*

Visit [langserver.org](https://langserver.org) to find out if a language server exists for this language."""


class LspSetupLanguageServerCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        syntax = view.settings().get("syntax")
        available_config = get_global_client_config(view)

        syntax_name = extract_syntax_name(syntax)
        title = "# Language Server for {}\n".format(syntax_name)

        if available_config:
            content = supported_syntax_template.format(syntax_name)
        else:
            title = "# No Language Server support"
            content = unsupported_syntax_template.format(syntax_name)

        mdpopups.show_popup(
            view,
            "\n".join([title, content]),
            css='''
                .lsp_documentation {
                    margin: 1rem 1rem 0.5rem 1rem;
                    font-family: system;
                }
                .lsp_documentation h1,
                .lsp_documentation p {
                    margin: 0 0 0.5rem 0;
                }
            ''',
            md=True,
            wrapper_class="lsp_documentation",
            max_width=800,
            max_height=600,
            on_navigate=self.on_hover_navigate
        )

    def on_hover_navigate(self, href):
        if href == "#enable_globally":
            self.window.run_command("lsp_enable_language_server_globally")
        elif href == "#enable_project":
            self.window.run_command("lsp_enable_language_server_in_project")
        else:
            webbrowser.open_new_tab(href)
