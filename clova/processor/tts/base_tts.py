from abc import ABC, abstractmethod
from typing import Union

class BaseTTSProvider(ABC):
    @abstractmethod
    def tts(self, text, **kwargs) -> Union[str, None]: # TODO: make this byte
        pass