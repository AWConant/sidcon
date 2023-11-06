import enum
import logging
import typing as typ
from collections.abc import Mapping

import sidcon.countedunits
import sidcon.units
from sidcon.converter import Converter
from sidcon.countedunits import CountedUnits
from sidcon.row import Row

logging.basicConfig()
logger = logging.getLogger(__name__)


Feature = typ.Union[Converter, CountedUnits, "UniqueFeature"]


@typ.final
@enum.unique
class UniqueFeature(enum.Enum):
    # TODO: Add MAY_NOT_BE_TRADED and UPGRADES_WITH_OTHER_PLAYERS_TECH for alt Kjas.
    PLUS_ONE_COLONY_SUPPRT_THIS_TURN = "+1 Colony Support This Turn"

    CONTEXTUAL_INTEGRATOR_CACHE_VPS = "Variable $"
    CONTEXTUAL_INTEGRATOR_CACHE_ACKNOWLEDGEMENT_UPGRADE = "Ack* upgraded"

    DRAW_TWO_COLONIES_FROM_DECK = "+2 colonies from deck"

    UNDESIRABLE_LIMIT_THREE = "Undesirable Limit: 3"
    UNDESIRABLE_LIMIT_FIVE = "Undesirable Limit: 5"

    NINE_TIEBREAKER = "9 Tie Breaker"

    PLUS_ONE_TO_A_DIE = "+1 to a die"
    MINUS_ONE_TO_A_DIE = "-1 to a die"

    MAY_NOT_USE_GREEN = "may not use g"
    MAY_NOT_USE_BROWN = "may not use b"
    MAY_NOT_USE_WHITE = "may not use w"
    MAY_NOT_USE_YELLOW = "may not use Y"
    MAY_NOT_USE_BLACK = "may not use B"
    MAY_NOT_USE_BLUE = "may not use T"
    MAY_NOT_USE_ULTRATECH = "may not use U"


def front_strings_from_row(r: Row) -> list[str]:
    return _strings_from_string(r.front_converter)


def back_strings_from_row(r: Row) -> list[str]:
    return _strings_from_string(r.back_converter)


def _strings_from_string(s: str) -> list[str]:
    strings = s.split(",")
    return list(filter(lambda s: s != "", strings))


def from_string(s: str) -> Feature:
    unique_feature_error: ValueError
    try:
        return UniqueFeature(s)
    except ValueError as e:
        unique_feature_error = e

    converter_error: ValueError
    try:
        return Converter.from_string_with_unknown_key(s)
    except ValueError as e:
        converter_error = e

    counted_units_error: ValueError
    try:
        return sidcon.countedunits.from_string(s)
    except ValueError as e:
        counted_units_error = e

    raise FeatureParseError(s, unique_feature_error, converter_error, counted_units_error)


def merged(a: Feature, b: Feature) -> Feature:
    if isinstance(a, Converter) and isinstance(b, Converter):
        # TODO: This doesn't ensure that a and b are the same Converter subtype.
        return a.__class__.merged(a, b)
    elif isinstance(a, Mapping) and isinstance(b, Mapping):
        return sidcon.countedunits.add(a, b)
    elif isinstance(a, UniqueFeature) and isinstance(b, UniqueFeature):
        raise ValueError("cannot merge UniqueFeatures")
    else:
        raise ValueError(f"input features have differing or invalid types: {type(a)}, {type(b)}")


@typ.final
class FeatureParseError(Exception):
    s: typ.Final[str]
    unique_feature_error: typ.Final[ValueError]
    converter_error: typ.Final[ValueError]
    counted_units_error: typ.Final[ValueError]

    def __init__(
        self,
        s: str,
        unique_feature_error: ValueError,
        converter_error: ValueError,
        counted_units_error: ValueError,
    ) -> None:
        self.s = s
        self.unique_feature_error = unique_feature_error
        self.converter_error = converter_error
        self.counted_units_error = counted_units_error
        super().__init__(f"couldn't parse Feature from string '{s}'")

    def __str__(self):
        return "\n".join(
            [
                f"{super().__str__()}\n",
                "Unique feature parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.unique_feature_error)}\n",
                "Converter parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.converter_error)}\n",
                "CountedUnits parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.counted_units_error)}",
            ]
        )
