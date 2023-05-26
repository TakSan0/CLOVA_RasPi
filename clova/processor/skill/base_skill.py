from abc import ABC, abstractmethod
from typing import Union

class BaseSkillProvider(ABC):
    @abstractmethod
    def try_get_answer(self, prompt, **kwargs) -> Union[str, None]:
        pass
