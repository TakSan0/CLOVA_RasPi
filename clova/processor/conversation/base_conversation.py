from abc import ABC, abstractmethod

class BaseConversationProvider(ABC):
    @abstractmethod
    def set_persona(self, prompt, **kwargs) -> None:
        pass

    @abstractmethod
    def get_answer(self, prompt, **kwargs) -> str | None:
        pass
