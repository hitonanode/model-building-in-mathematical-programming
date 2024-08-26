from abc import ABCMeta, abstractmethod

from .month import Month
from .oil import Oil


class ManufacturingPlan[T](metaclass=ABCMeta):
    @abstractmethod
    def stock(self, oil: Oil, month: Month) -> T:
        raise NotImplementedError

    @abstractmethod
    def purchase(self, oil: Oil, month: Month) -> T:
        raise NotImplementedError

    @abstractmethod
    def refine(self, oil: Oil, month: Month) -> T:
        raise NotImplementedError

    @abstractmethod
    def is_refined(self, oil: Oil, month: Month) -> T:
        raise NotImplementedError
