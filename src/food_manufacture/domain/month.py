from pydantic import BaseModel, Field


class Month(BaseModel):
    year: int
    month: int = Field(..., ge=1, le=12)

    def __le__(self, other: "Month") -> bool:
        return (self.year, self.month) <= (other.year, other.month)

    def __lt__(self, other: "Month") -> bool:
        return (self.year, self.month) < (other.year, other.month)

    def __str__(self) -> str:
        return f"{self.year}/{self.month:02d}"

    def __hash__(self) -> int:
        return hash(self.year * 12 + self.month)

    @classmethod
    def from_str(cls, s: str) -> "Month":
        year, month = map(int, s.split("/"))
        return cls(year=year, month=month)

    def next(self) -> "Month":
        if self.month == 12:
            return Month(year=self.year + 1, month=1)
        return Month(year=self.year, month=self.month + 1)

    def previous(self) -> "Month":
        if self.month == 1:
            return Month(year=self.year - 1, month=12)
        return Month(year=self.year, month=self.month - 1)
