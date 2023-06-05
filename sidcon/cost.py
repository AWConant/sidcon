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
    DEEP_UNITY_NOT_TRIPLES = "Dice not triples"
    DEEP_UNITY_SINGLE_ZERO = "Die 0"
    DEEP_UNITY_SINGLE_ONE = "Die 1"
    DEEP_UNITY_SINGLE_TWO = "Die 2"
    DEEP_UNITY_SINGLE_THREE = "Die 3"
    DEEP_UNITY_SINGLE_FOUR = "Die 4"
    DEEP_UNITY_SINGLE_FIVE = "Die 5"
    DEEP_UNITY_SINGLE_SIX = "Die 6"
    DEEP_UNITY_SINGLE_SEVEN = "Die 7"

    # Caylion Collaborative
    CAYLION_COLLABORATIVE_THREE_VOTES = "3 votes"
    CAYLION_COLLABORATIVE_FOUR_VOTES = "4 votes"
    CAYLION_COLLABORATIVE_FIVE_VOTES = "5 votes"
    CAYLION_COLLABORATIVE_SIX_VOTES = "6 votes"

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
