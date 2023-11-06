import dataclasses
import enum
import logging
import typing as typ

logging.basicConfig()
logger = logging.getLogger(__name__)


@typ.final
class Column(enum.Enum):
    CARD_NUMBER = "s"
    FACTION_TITLE = "Faction"
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
    faction_title: str
    era: str
    cost: str
    front_name: str
    front_converter: str
    upgrade1: str
    upgrade2: str
    upgrade3: str
    back_name: str
    back_converter: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> "Row":
        upgrade3: str
        try:
            upgrade3 = d[Column.UPGRADE3.value]
        except KeyError:
            upgrade3 = ""
        return cls(
            card_number=d[Column.CARD_NUMBER.value],
            faction_title=d[Column.FACTION_TITLE.value],
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
        # TODO: use `| None` rather than Optional.
        card_number: typ.Optional[str] = None,
        faction_title: typ.Optional[str] = None,
        era: typ.Optional[str] = None,
        cost: typ.Optional[str] = None,
        front_name: typ.Optional[str] = None,
        front_converter: typ.Optional[str] = None,
        upgrade1: typ.Optional[str] = None,
        upgrade2: typ.Optional[str] = None,
        upgrade3: typ.Optional[str] = None,
        back_name: typ.Optional[str] = None,
        back_converter: typ.Optional[str] = None,
    ) -> "Row":
        return Row(
            card_number=card_number if card_number is not None else self.card_number,
            faction_title=faction_title if faction_title is not None else self.faction_title,
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
