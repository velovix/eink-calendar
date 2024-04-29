import datetime
from typing import Any


class Event:
    def __init__(self, calendar_data: dict[str, Any], event_data: dict[str, Any]):
        self.color = self._hex_to_color(calendar_data["backgroundColor"])

        start = event_data["start"]
        self.summary = event_data["summary"]
        if "dateTime" in start:
            self.start_time = datetime.datetime.strptime(
                start["dateTime"], "%Y-%m-%dT%H:%M:%S%z",
            )
            self.all_day = False
        else:
            self.start_time = datetime.datetime.strptime(start["date"], "%Y-%m-%d")
            self.all_day = True

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def _hex_to_color(self, hex_: str) -> tuple[int, int, int]:
        hex_ = hex_.replace("#", "")
        return int(hex_[:2], 16), int(hex_[2:4], 16), int(hex_[4:6], 16)
