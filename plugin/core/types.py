try:
    from typing_extensions import Protocol
    from typing import Optional, List, Callable, Dict, Any
    assert Optional and List and Callable and Dict and Any
except ImportError:
    pass
    Protocol = object  # type: ignore


class Settings(object):

    def __init__(self):
        self.show_status_messages = True
        self.show_view_status = True
        self.auto_show_diagnostics_panel = True
        self.show_diagnostics_phantoms = False
        self.show_diagnostics_count_in_view_status = False
        self.show_diagnostics_in_view_status = True
        self.show_diagnostics_severity_level = 3
        self.only_show_lsp_completions = False
        self.diagnostics_highlight_style = "underline"
        self.highlight_active_signature_parameter = True
        self.document_highlight_style = "stippled"
        self.document_highlight_scopes = {
            "unknown": "text",
            "text": "text",
            "read": "markup.inserted",
            "write": "markup.changed"
        }
        self.diagnostics_gutter_marker = "dot"
        self.complete_all_chars = False
        self.completion_hint_type = "auto"
        self.resolve_completion_for_snippets = False
        self.log_debug = True
        self.log_server = True
        self.log_stderr = False
        self.log_payloads = False


class ClientStates(object):
    STARTING = 0
    READY = 1
    STOPPING = 2


class ConfigState(object):

    def __init__(self, project_path, state=ClientStates.STARTING, client=None, capabilities=None):
        self.project_path = project_path
        self.state = state
        self.client = client
        self.capabilities = capabilities


class LanguageConfig(object):
    def __init__(self, language_id: str, scopes: 'List[str]', syntaxes: 'List[str]') -> None:
        self.id = language_id
        self.scopes = scopes
        self.syntaxes = syntaxes


class ClientConfig(object):
    def __init__(self, name, binary_args, tcp_port, scopes=[], syntaxes=[], languageId=None,
                 languages: 'List[LanguageConfig]'=[], enabled=True, init_options=dict(),
                 settings=dict(), env=dict()) -> None:
        self.name = name
        self.binary_args = binary_args
        self.tcp_port = tcp_port
        if not languages and languageId:
            languages.append(LanguageConfig(languageId, scopes, syntaxes))
        self.languages = languages
        self.enabled = enabled
        self.init_options = init_options
        self.settings = settings
        self.env = env


class SettingsLike(object):
    def __init__(self, values):
        ...

    def get(self, key: str) -> 'Any':
        ...

    def set(self, key: str, value: 'Any'):
        ...


class ViewLike(Protocol):
    def __init__(self):
        pass

    def file_name(self) -> 'Optional[str]':
        ...

    def window(self) -> 'Optional[Any]':  # WindowLike
        ...

    def buffer_id(self) -> int:
        ...

    def substr(self, region: 'Any') -> str:
        ...

    def settings(self) -> 'Any':  # SettingsLike
        ...

    def size(self) -> int:
        ...

    def set_status(self, key: str, status: str) -> None:
        ...

    def sel(self):
        ...

    def score_selector(self, region, scope: str) -> int:
        ...


class WindowLike(Protocol):
    def id(self) -> int:
        ...

    def folders(self) -> 'List[str]':
        ...

    def num_groups(self) -> int:
        ...

    def active_group(self) -> int:
        ...

    def active_view_in_group(self, group: int) -> ViewLike:
        ...

    def project_data(self) -> 'Optional[dict]':
        ...

    def active_view(self) -> 'Optional[ViewLike]':
        ...

    def status_message(self, msg: str) -> None:
        ...

    def views(self) -> 'List[ViewLike]':
        ...

# protocols can be modules once mypy implements this.
# class SublimeGlobal(Protocol):
#     DIALOG_CANCEL = 0  # type: int
#     DIALOG_YES = 1  # type: int
#     DIALOG_NO = 2  # type: int

#     def message_dialog(self, msg: str) -> None:
#         ...

#     def ok_cancel_dialog(self, msg: str, ok_title: str) -> bool:
#         ...

#     def yes_no_cancel_dialog(self, msg, yes_title: str, no_title: str) -> int:
#         ...
