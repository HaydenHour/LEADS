from importlib.util import find_spec as _find_spec

if not _find_spec("dearpygui"):
    raise ImportError("Please install `dearpygui` to run this module\n>>> pip install dearpygui")

from typing import Callable as _Callable, TypeVar as _TypeVar

from leads import Leads as _Leads, Controller as _Controller
from leads.comm import Server as _Server, create_server as _create_server
from leads_dashboard.prototype import *
from leads_dashboard.runtime import *

T = _TypeVar("T")

H1 = ("Arial", 24)
H2 = ("Arial", 22)
H3 = ("Arial", 20)
H4 = ("Arial", 18)
H5 = ("Arial", 16)
BODY = ("Arial", 12)


def initialize(window: Window,
               render: _Callable[[ContextManager], None],
               leads: _Leads[T],
               main_controller: _Controller[T]) -> ContextManager:
    ctx = ContextManager(window)
    render(ctx)
    window.runtime_data().frame_counter = 0

    def on_refresh(_):
        leads.push(main_controller.collect_all())
        leads.update()

    window.set_on_refresh(on_refresh)
    return ctx


def initialize_comm_server(window: Window,
                           render: _Callable[[ContextManager], None],
                           server: _Server = _create_server()) -> None:
    ctx = ContextManager(window)
    render(ctx)
    server.start(True)

    def on_close(_):
        server.kill()

    window.set_on_close(on_close)
