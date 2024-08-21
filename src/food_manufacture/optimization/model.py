import mip  # type: ignore

from ..domain.constraints import AbstractConstraint
from ..domain.task import Task
from .objective import Objective
from .variables import Variables


class Model:
    def __init__(
        self,
        model: mip.Model,
        task: Task,
        var: Variables,
        constraints: list[AbstractConstraint],
    ):
        self.model = model
        self.task = task
        self.var = var
        self.constraints = constraints

    @classmethod
    def build(cls, task: Task) -> "Model":
        model = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
        var = Variables(task=task, model=model)

        return cls(
            model=model,
            task=task,
            var=var,
            constraints=[],
        )

    def add_constraint(self, constraint: AbstractConstraint) -> None:
        self.constraints.append(constraint)
        for c in constraint.constraints(self.task, self.var):
            self.model.add_constr(c)

    def set_objective(self, objective: type[Objective]) -> None:
        self.model.objective = objective.objective(self.task, self.var)
