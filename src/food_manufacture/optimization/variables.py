import mip  # type: ignore

from ..domain.manufacturing_plan import ManufacturingPlan
from ..domain.month import Month
from ..domain.oil import Oil
from ..domain.task import Task


class Variables(ManufacturingPlan[mip.Var]):
    def __init__(
        self,
        task: Task,
        model: mip.Model,
    ) -> None:
        self.stock_vals = {
            (month, oil.name): model.add_var(name=f"stock_{month}_{oil.name}", lb=0)
            for month in task.target_months
            for oil in task.oils
        }

        self.purchase_vals = {
            (month, oil.name): model.add_var(name=f"purchase_{month}_{oil.name}", lb=0)
            for month in task.target_months
            for oil in task.oils
        }

        self.refine_vals = {
            (month, oil.name): model.add_var(name=f"refine_{month}_{oil.name}", lb=0)
            for month in task.target_months
            for oil in task.oils
        }

        self.is_refined_vals = {
            (month, oil.name): model.add_var(
                name=f"is_refined_{month}_{oil.name}", var_type=mip.BINARY
            )
            for month in task.target_months
            for oil in task.oils
        }

        for month in task.target_months:
            for oil in task.oils:
                model.add_constr(
                    self.is_refined_vals[(month, oil.name)] * task.big_m
                    >= self.refine_vals[(month, oil.name)]
                )

    def stock(self, oil: Oil, month: Month) -> mip.Var:
        return self.stock_vals[(month, oil.name)]

    def purchase(self, oil: Oil, month: Month) -> mip.Var:
        return self.purchase_vals[(month, oil.name)]

    def refine(self, oil: Oil, month: Month) -> mip.Var:
        return self.refine_vals[(month, oil.name)]

    def is_refined(self, oil: Oil, month: Month) -> mip.Var:
        return self.is_refined_vals[(month, oil.name)]
