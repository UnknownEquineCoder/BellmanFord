from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HopInfo:
    """
    A class to hold information about a hop.
    """

    next_hop: str
    best_distance: float

    def __repr__(self):
        return f"→ {self.next_hop} (cost: {self.best_distance})"

    @classmethod
    def parse_str(cls, source: str, /) -> HopInfo:
        """
        Parse a string into a HopInfo object.

        :param source: The string to parse.
        :return: A HopInfo object.
        """
        normalised = source[1:-1].strip()
        hop, distance = normalised.split(",")
        return cls(hop, float(distance))
