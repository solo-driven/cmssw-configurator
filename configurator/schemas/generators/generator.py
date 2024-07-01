from abc import ABC, abstractmethod



class Generator(ABC):
    @abstractmethod
    def generator_string(self) -> str:
        pass