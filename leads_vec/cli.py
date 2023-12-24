from datetime import datetime
from time import time

from PySimpleGUI import Button, Text
from keyboard import add_hotkey

from leads import *
from leads.comm import *
from leads_dashboard import *
from leads_vec.__version__ import __version__
from leads_vec.config import Config


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    m3_mode: int = 0


def main(main_controller: Controller, config: Config) -> int:
    context = Leads(srw_mode=config.srw_mode)

    def render(manager: ContextManager):
        def switch_m1_mode():
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 2

        def switch_m3_mode():
            manager.rd().m3_mode = (manager.rd().m3_mode + 1) % 3

        manager["m1"] = Button(font=BODY, key=switch_m1_mode, size=(round(manager.window().width() / 19.393939), 12))
        manager["m2"] = Button(font=H1, size=(round(manager.window().width() / 60), 4))
        manager["m3"] = Button(font=H1, key=switch_m3_mode, size=(round(manager.window().width() / 64), 4))
        manager["dtcs_status"] = Text(text="DTCS READY", text_color="green", font=BODY,
                                      size=(round(manager.window().width() / 32.323232), None))
        manager["abs_status"] = Text(text="ABS READY", text_color="green", font=BODY,
                                     size=(round(manager.window().width() / 32.323232), None))
        manager["ebi_status"] = Text(text="EBI READY", text_color="green", font=BODY,
                                     size=(round(manager.window().width() / 32.323232), None))
        manager["atbs_status"] = Text(text="ATBS READY", text_color="green", font=BODY,
                                      size=(round(manager.window().width() / 32.323232), None))
        manager["comm_status"] = Text(text="COMM ONLINE", text_color="white", font=BODY,
                                      size=(round(manager.window().width() / 32.323232), None))

        def switch_dtcs():
            context.set_dtcs(not (dtcs_enabled := context.is_dtcs_enabled()))
            manager["dtcs"].update(f"DTCS {'OFF' if dtcs_enabled else 'ON'}")

        add_hotkey("1", switch_dtcs)

        def switch_abs():
            context.set_abs(not (abs_enabled := context.is_abs_enabled()))
            manager["abs"].update(f"ABS {'OFF' if abs_enabled else 'ON'}")

        add_hotkey("2", switch_abs)

        def switch_ebi():
            context.set_ebi(not (ebi_enabled := context.is_ebi_enabled()))
            manager["ebi"].update(f"EBI {'OFF' if ebi_enabled else 'ON'}")

        add_hotkey("3", switch_ebi)

        def switch_atbs():
            context.set_atbs(not (atbs_enabled := context.is_atbs_enabled()))
            manager["atbs"].update(f"ATBS {'OFF' if atbs_enabled else 'ON'}")

        add_hotkey("4", switch_atbs)

        manager["dtcs"] = Button(button_text="DTCS ON", key=switch_dtcs, font=BODY,
                                 size=(round(manager.window().width() / 25.858585), None))
        manager["abs"] = Button(button_text="ABS ON", key=switch_abs, font=BODY,
                                size=(round(manager.window().width() / 25.858585), None))
        manager["ebi"] = Button(button_text="EBI ON", key=switch_ebi, font=BODY,
                                size=(round(manager.window().width() / 25.858585), None))
        manager["atbs"] = Button(button_text="ATBS ON", key=switch_atbs, font=BODY,
                                 size=(round(manager.window().width() / 25.858585), None))

    uim = initialize(Window(1080, 720,
                            config.refresh_rate,
                            CustomRuntimeData()), render, context, main_controller)

    class CustomCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            uim.rd().comm = None
            uim["comm_status"].update("COMM OFFLINE", text_color="gray")

        def on_receive(self, service: Service, msg: bytes) -> None:
            print(msg)

    uim.rd().comm = start_client(config.comm_addr, create_client(config.comm_port, CustomCallback()), True)

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent) -> None:
            try:
                uim.rd().comm_notify(e.data)
            except IOError:
                uim.rd().comm_kill()
                uim.rd().comm = None
                uim["comm_status"].update("COMM OFFLINE", text_color="gray")

        def on_update(self, e: UpdateEvent) -> None:
            duration = int(time()) - uim.rd().start_time
            if uim.rd().m1_mode == 0:
                uim["m1"].update("LAP TIME\n\nLAP1 9s\nLAP2 11s\nLAP3 10s")
            elif uim.rd().m1_mode == 1:
                uim["m1"].update(f"VeC {__version__.upper()}\n\n"
                                 f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                 f"{duration // 60} MIN {duration % 60} SEC\n\n"
                                 f"{'SRW MODE' if config.srw_mode else 'DRW MODE'}\n"
                                 f"REFRESH RATE: {config.refresh_rate} FPS")
            uim["m2"].update(f"{int(context.data().front_wheel_speed)}")
            if uim.rd().m3_mode == 0:
                uim["m3"].update("0.0V")
            elif uim.rd().m3_mode == 1:
                uim["m3"].update("G Force")
            else:
                uim["m3"].update("Speed Trend")

        def on_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].update(e.system + " INTERVENED", text_color="purple")

        def post_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].update(e.system + " READY", text_color="green")

        def on_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].update(e.system + " SUSPENDED", text_color="red")

        def post_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].update(e.system + " READY", text_color="green")

    context.set_event_listener(CustomListener())
    uim.layout([
        ["m1", "m2", "m3"],
        ["dtcs_status", "abs_status", "ebi_status", "atbs_status", "comm_status"],
        ["dtcs", "abs", "ebi", "atbs"]
    ])
    add_hotkey("ctrl+e", uim.kill)
    uim.show()
    uim.rd().comm_kill()
    return 0
