from abc import ABC, abstractmethod

class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id): ...
    @abstractmethod
    def list(self): ...
