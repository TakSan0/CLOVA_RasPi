from abc import ABC, abstractmethod
from typing import Union

class BaseConversationProvider(ABC):
    @abstractmethod
    def set_persona(self, prompt, **kwargs) -> None:
        pass

    @abstractmethod
    def get_answer(self, prompt, **kwargs) -> Union[str, None]:
        pass
