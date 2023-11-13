import dataclasses
import enum
import logging
import typing as typ

logging.basicConfig()
logger = logging.getLogger(__name__)


@typ.final
class Column(enum.Enum):
    CARD_NUMBER = "s"
    FACTION_NAME = "Faction"
    FRONT_NAME = "Front Name"
    ERA = "Era"
    COST = "Cost"
    FRONT_CONVERTER = "Front Factory"
    UPGRADE1 = "Upgrade1"
    UPGRADE2 = "Upgrade2"
    UPGRADE3 = "Upgrade3"  # bifurcation only
    BACK_NAME = "Back Name"
    BACK_CONVERTER = "Back Factory"
    INPUT_VALUE = "Input"  # unused
    FRONT_OUTPUT_VALUE = "Front Output"  # unused
    FRONT_EFFICIENCY = "Front Efficiency"  # unused
    BACK_OUTPUT_VALUE = "Back Output"  # unused
    BACK_EFFICIENCY = "Back Efficiency"  # unused
    UPGRADES = "Upgrades"  # unused


@dataclasses.dataclass(frozen=True, kw_only=True)
class Row(object):
    card_number: str
    faction_name: str
    era: str
    cost: str
    front_name: str
    front_converter: str
    upgrade1: str
    upgrade2: str
    upgrade3: str
    back_name: str
    back_converter: str

    # TODO: rename this to from_csv_row_dict, to disambiguate from the ods parsing logic, when that
    # exists.
    @classmethod
    def from_dict(cls, d: dict[str, str]) -> "Row":
        upgrade3: str
        try:
            upgrade3 = d[Column.UPGRADE3.value]
        except KeyError:
            upgrade3 = ""
        return cls(
            card_number=d[Column.CARD_NUMBER.value],
            faction_name=d[Column.FACTION_NAME.value],
            era=d[Column.ERA.value],
            cost=d[Column.COST.value],
            front_name=d[Column.FRONT_NAME.value],
            front_converter=d[Column.FRONT_CONVERTER.value],
            upgrade1=d[Column.UPGRADE1.value],
            upgrade2=d[Column.UPGRADE2.value],
            upgrade3=upgrade3,
            back_name=d[Column.BACK_NAME.value],
            back_converter=d[Column.BACK_CONVERTER.value],
        )

    def copy(
        self,
        *,
        card_number: str | None = None,
        faction_name: str | None = None,
        era: str | None = None,
        cost: str | None = None,
        front_name: str | None = None,
        front_converter: str | None = None,
        upgrade1: str | None = None,
        upgrade2: str | None = None,
        upgrade3: str | None = None,
        back_name: str | None = None,
        back_converter: str | None = None,
    ) -> "Row":
        return Row(
            card_number=card_number if card_number is not None else self.card_number,
            faction_name=faction_name if faction_name is not None else self.faction_name,
            era=era if era is not None else self.era,
            cost=cost if cost is not None else self.cost,
            front_name=front_name if front_name is not None else self.front_name,
            front_converter=front_converter
            if front_converter is not None
            else self.front_converter,
            upgrade1=upgrade1 if upgrade1 is not None else self.upgrade1,
            upgrade2=upgrade2 if upgrade2 is not None else self.upgrade2,
            upgrade3=upgrade3 if upgrade3 is not None else self.upgrade3,
            back_name=back_name if back_name is not None else self.back_name,
            back_converter=back_converter if back_converter is not None else self.back_converter,
        )

    @property
    def upgrade_strings(self) -> list[str]:
        return list(filter(lambda s: s != "", [self.upgrade1, self.upgrade2, self.upgrade3]))

    @property
    def front_feature_strings(self) -> list[str]:
        return self._strings_from_string(self.front_converter)

    @property
    def back_feature_strings(self) -> list[str]:
        return self._strings_from_string(self.back_converter)

    @staticmethod
    def _strings_from_string(s: str) -> list[str]:
        strings = s.split(",")
        return list(filter(lambda s: s != "", strings))
