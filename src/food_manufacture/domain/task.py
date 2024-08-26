from pydantic import BaseModel

from .month import Month
from .oil import Oil, OilName, OilType


class Task(BaseModel):
    target_months: list[Month]

    oils: list[Oil]

    market_price: dict[tuple[Month, OilName], float]

    sell_price_per_ton: float = 150  # 販売価格

    max_refine_tons_per_month: dict[OilType, float] = {
        OilType.VEGETABLE: 200,
        OilType.NON_VEGETABLE: 250,
    }

    max_stock_tons_per_raw_oil: float = 1000

    storage_cost_per_ton_per_month: float = 5

    final_hardness_lb: float = 3
    final_hardness_ub: float = 6

    init_stock_tons_per_raw_oil: float = 500
    final_min_stock_tons_per_raw_oil: float = 500

    min_refine_tons_per_month_per_oil_if_used: float = 20
    max_types_of_oils_to_refine_per_month: int = 3

    big_m: float = 250

    dependency_rules: list[tuple[list[OilName], OilName]] = [
        ([OilName("VEG 1")], OilName("OIL 3")),
        ([OilName("VEG 2")], OilName("OIL 3")),
    ]

    def oil(self, name: OilName) -> Oil:
        return next(oil for oil in self.oils if oil.name == name)

    @property
    def first_month(self) -> Month:
        return self.target_months[0]

    @property
    def last_month(self) -> Month:
        return self.target_months[-1]

    @classmethod
    def build(
        cls,
        first_month: Month,
        last_month: Month,
        oils: list[Oil],
        market_price: dict[tuple[Month, OilName], float],
    ) -> "Task":
        assert first_month <= last_month

        assert len(set(oil.name for oil in oils)) == len(oils)

        months = [first_month]
        while months[-1] < last_month:
            months.append(months[-1].next())

        return cls(
            target_months=months,
            oils=oils,
            market_price=market_price,
        )
