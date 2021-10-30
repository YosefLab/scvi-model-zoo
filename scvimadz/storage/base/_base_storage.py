from abc import ABC, abstractmethod
from typing import List


class BaseStorage(ABC):
    @abstractmethod
    def list_model_keys(self) -> List[str]:
        """ Returns the id's of all models stored """
        pass

    @abstractmethod
    def list_dataset_keys(self) -> List[str]:
        """ Returns the id's of all datasets stored """
        pass

    def list_all_keys(self) -> List[str]:
        """ Returns the id's of all models and datasets stored """
        return self.list_model_keys() + self.list_dataset_keys()

    @abstractmethod
    def load_model(self, key: str) -> str:
        """
        Loads the model with the given id if it exists, else raises an error.

        Parameters
        ----------
        model_id
            id of the model to load
        """
        pass
