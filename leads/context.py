from copy import copy as _copy
from typing import TypeVar as _TypeVar, Generic as _Generic, Optional as _Optional

from .data import DataContainer, SRWDataContainer, DRWDataContainer


T = _TypeVar("T")


def _check_data_type(data: T, superclass: type = DataContainer):
    if not isinstance(data, superclass):
        raise TypeError(f"New data must inherit from `{superclass}`")


class Context(_Generic[T]):
    def __init__(self, srw_mode: bool = True, initial_data: _Optional[T] = None):
        """
        :param srw_mode: True: single rear wheel mode; False: double rear wheel mode
        :param initial_data: initial data
        """
        self._srw_mode: bool = srw_mode
        superclass = SRWDataContainer if srw_mode else DRWDataContainer
        if initial_data is None:
            initial_data = superclass()
        _check_data_type(initial_data, superclass)
        self.__initial_data_type: type = type(initial_data)
        self._data: T = initial_data

    def data(self) -> T:
        return _copy(self._data)

    def push(self, data: T):
        _check_data_type(data, self.__initial_data_type)
        self._data = data
