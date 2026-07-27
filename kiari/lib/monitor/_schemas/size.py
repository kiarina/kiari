from dataclasses import dataclass


@dataclass
class Size:
    width: int

    height: int

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height
