from abc import ABC, abstractmethod


class Switch:
    @abstractmethod
    def set(self, state: bool) -> None:
        pass
