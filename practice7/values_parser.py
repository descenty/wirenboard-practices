from dataclasses import dataclass
from json import load


@dataclass
class BoardValues:
    id: int
    time: str
    temperature: float
    motion: float
    sound: float
    illuminance: float


data: list[BoardValues] = [
    BoardValues(**values) for values in load(open("data.json", "r"))
]

for values in data:
    for key, value in values.__dict__.items():
        print(f"{' '.join(key.split('_'))}: {value}")
    print()
