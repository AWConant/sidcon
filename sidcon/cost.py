import enum
import logging
import typing as typ
from collections.abc import Collection

from sidcon.converter import NoMatchingArrow, PurpleConverter
from sidcon.technology import Technology

logging.basicConfig()
logger = logging.getLogger(__name__)


Cost = typ.Union[PurpleConverter, Collection[type[Technology]], "FactionSpecificCost"]


@typ.final
@enum.unique
class FactionSpecificCost(enum.Enum):
    # Deep Unity
    NOT_TRIPLES = "Dice not triples"
    SINGLE_ZERO = "Die 0"
    SINGLE_ONE = "Die 1"
    SINGLE_TWO = "Die 2"
    SINGLE_THREE = "Die 3"
    SINGLE_FOUR = "Die 4"
    SINGLE_FIVE = "Die 5"
    SINGLE_SIX = "Die 6"
    SINGLE_SEVEN = "Die 7"

    # Caylion Collaborative
    THREE_VOTES = "3 votes"
    FOUR_VOTES = "4 votes"
    FIVE_VOTES = "5 votes"
    SIX_VOTES = "6 votes"

    # Yengii Jii
    JII_CONSTRAINT = "Jii Constraint"


def from_string(s: str) -> Cost:
    try:
        return FactionSpecificCost(s)
    except ValueError:
        pass

    try:
        return PurpleConverter.from_string(s)
    except NoMatchingArrow:
        pass

    try:
        return Technology.multiple_from_string(s)
    except ValueError:
        pass

    raise ValueError(f"couldn't parse Cost from string '{s}'")
