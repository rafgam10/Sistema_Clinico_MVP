from abc import ABC, abstractmethod

class IUsuario(ABC):
    
    @abstractmethod
    def get_usuario() -> None: pass