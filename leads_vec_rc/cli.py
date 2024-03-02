from json import loads
from os import mkdir
from os.path import abspath, exists
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from leads import *
from leads.comm import *
from leads.data_persistence import *
from leads_gui import *

config = get_config(Config)
if not exists(config.data_dir):
    mkdir(config.data_dir)
    L.info(f"Data dir \"{abspath(config.data_dir)}\" created")

data_record = DataPersistence(max_size=1, compressor=lambda o, s: o[-s:])
time_stamp_record = DataPersistence(config.data_dir + "/time_stamp.csv",
                                    persistence=config.enable_data_persistence,
                                    max_size=2000)
speed_record = DataPersistence(config.data_dir + "/speed.csv",
                               persistence=config.enable_data_persistence,
                               max_size=2000)


class CommCallback(Callback):
    def on_connect(self, service: Service, connection: Connection) -> None:
        L.debug("Connected")

    def on_fail(self, service: Service, error: Exception) -> None:
        L.error("Comm client error: " + str(error))

    def on_receive(self, service: Service, msg: bytes) -> None:
        d = loads(msg.decode())
        data_record.append(d)
        time_stamp_record.append(d["t"])
        speed_record.append(d["front_wheel_speed"])

    def on_disconnect(self, service: Service, connection: Connection) -> None:
        time_stamp_record.close()
        speed_record.close()


client = start_client(config.comm_addr, create_client(config.comm_port, CommCallback()), True)

app = FastAPI(title="LEADS VeC Remote Controller")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def index() -> str:
    return "LEADS VeC Remote Controller"


@app.get("/current")
async def current() -> dict[str, Any]:
    return data_record[-1]


@app.get("/time_stamp")
async def time_stamp() -> list[int]:
    return time_stamp_record.to_list()


@app.get("/speed")
async def speed() -> list[float]:
    return speed_record.to_list()


@app.get("/time_lap")
async def time_lap() -> str:
    client.send(b"time_lap")
    return "done"
