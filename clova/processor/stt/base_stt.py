from abc import ABC, abstractmethod
from typing import Union

class BaseSTTProvider(ABC):
    @abstractmethod
    # audio: S16_LE? PCM audio
    def stt(self, audio, **kwargs) -> Union[str, None]:
        pass
