from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from json import dumps as _dumps
from threading import Lock as _Lock
from typing import Self as _Self, Any as _Any


class DataContainer(object, metaclass=_ABCMeta):
    def __init__(self):
        self._lock: _Lock = _Lock()

    @_abstractmethod
    def __sub__(self, other: _Self) -> _Self:
        raise NotImplementedError

    def __setattr__(self, key: str, value: _Any):
        if key == "_lock":
            super().__setattr__(key, value)
            return
        self._lock.acquire()
        try:
            super().__setattr__(key, value)
        finally:
            self._lock.release()

    def __str__(self) -> str:
        return _dumps(self.to_dict())

    def to_dict(self) -> dict:
        attributes = dir(self)
        r = {}
        for n in attributes:
            if n.startswith("_"):
                continue
            v = self.__getattribute__(n)
            if type(v) in (int, float, str):
                r[n] = v
        return r

    def encode(self) -> bytes:
        return str(self).encode()


class DefaultDataContainer(DataContainer):
    def __init__(self, wheel_speed: int | float = 0):
        super().__init__()
        self.wheel_speed: int | float = wheel_speed

    def __sub__(self, other: _Self) -> _Self:
        return DefaultDataContainer(self.wheel_speed - other.wheel_speed)


class SRWDataContainer(DataContainer):
    """
    Single Rear Wheel
    """

    def __init__(self,
                 front_wheel_speed: int | float = 0,
                 rear_wheel_speed: int | float = 0,
                 ):
        super().__init__()
        self.front_wheel_speed: int | float = front_wheel_speed
        self.rear_wheel_speed: int | float = rear_wheel_speed

    def __sub__(self, other: _Self) -> _Self:
        return SRWDataContainer(
            self.front_wheel_speed - other.front_wheel_speed,
            self.rear_wheel_speed - other.rear_wheel_speed
        )


class DRWDataContainer(DataContainer):
    """
    Dual Rear Wheel
    """

    def __init__(self,
                 front_wheel_speed: int | float = 0,
                 left_rear_wheel_speed: int | float = 0,
                 right_rear_wheel_speed: int | float = 0,
                 ):
        super().__init__()
        self.front_wheel_speed: int | float = front_wheel_speed
        self.left_rear_wheel_speed: int | float = left_rear_wheel_speed
        self.right_rear_wheel_speed: int | float = right_rear_wheel_speed

    def __sub__(self, other: _Self) -> _Self:
        return DRWDataContainer(
            self.front_wheel_speed - other.front_wheel_speed,
            self.left_rear_wheel_speed - other.left_rear_wheel_speed,
            self.right_rear_wheel_speed - other.right_rear_wheel_speed
        )
