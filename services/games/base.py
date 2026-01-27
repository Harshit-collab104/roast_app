from abc import ABC, abstractmethod

class GameInterface(ABC):
    @abstractmethod
    def get_player_data(self,player_identifier:str):
        pass
    @abstractmethod
    def format_data(self,raw_data):
        pass