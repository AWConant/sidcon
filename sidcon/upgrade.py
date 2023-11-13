import enum
import logging
import typing as typ

import sidcon.exception
from sidcon.converter import NoMatchingArrow, PurpleConverter
from sidcon.technology import Technology

logging.basicConfig()
logger = logging.getLogger(__name__)


Upgrade = typ.Union[PurpleConverter, type[Technology], "FactionSpecificUpgradeCondition"]


@typ.final
@enum.unique
class FactionSpecificUpgradeCondition(enum.Enum):
    # Deep Unity
    TRIPLES = "Dice triples"
    DOUBLE_ZEROES = "Die double 0s"
    DOUBLE_ONES = "Die double 1s"
    DOUBLE_TWOS = "Die double 2s"
    DOUBLE_THREES = "Die double 3s"
    DOUBLE_FOURS = "Die double 4s"
    DOUBLE_FIVES = "Die double 5s"
    DOUBLE_SIXES = "Die double 6s"
    DOUBLE_SEVENS = "Die double 7s"

    # Charity Syndicate
    CROSS_COLONIZATION = "Cross-Colonization"

    # Kt Technophiles
    KT_RESEARCH = "Tech invention"


def merged(a: Upgrade, b: Upgrade) -> Upgrade:
    if isinstance(a, PurpleConverter) and isinstance(b, PurpleConverter):
        # WARNING: This doesn't ensure that a and b are the same Converter subtype. Here, this
        # doesn't matter unless PurpleConverter has descendents in the future.
        # TODO: Figure out how to ensure that a and b are both exactly PurpleConverters, rather
        # than simply within the type.
        return a.__class__.merged(a, b)
    else:
        raise ValueError(f"input upgrades have differing or unhandled types: {type(a)}, {type(b)}")


def from_string(s: str) -> Upgrade:
    technology_error: ValueError
    try:
        return Technology.from_string(s)
    except ValueError as e:
        technology_error = e

    converter_error: NoMatchingArrow
    try:
        return PurpleConverter.from_string(s)
    except NoMatchingArrow as e:
        converter_error = e

    faction_specific_error: ValueError
    try:
        return FactionSpecificUpgradeCondition(s)
    except ValueError as e:
        faction_specific_error = e

    raise UpgradeParseError(s, technology_error, converter_error, faction_specific_error)


@typ.final
class UpgradeParseError(Exception):
    s: typ.Final[str]
    technology_error: typ.Final[ValueError]
    converter_error: typ.Final[NoMatchingArrow]
    faction_specific_upgrade_condition_error: typ.Final[ValueError]

    def __init__(
        self,
        s: str,
        technology_error: ValueError,
        converter_error: NoMatchingArrow,
        faction_specific_upgrade_condition_error: ValueError,
    ) -> None:
        self.s = s
        self.technology_error = technology_error
        self.converter_error = converter_error
        self.faction_specific_upgrade_condition_error = faction_specific_upgrade_condition_error
        super().__init__(f"couldn't parse Upgrade from string '{s}'")

    def __str__(self):
        return "\n".join(
            [
                f"{super().__str__()}\n",
                "Technology parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.technology_error)}\n",
                "Converter parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.converter_error)}",
                "Faction-specific upgrade condition parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.faction_specific_upgrade_condition_error)}",
            ]
        )
