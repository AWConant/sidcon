from __future__ import annotations

import dataclasses
import logging
import typing as typ
from collections.abc import Collection, Mapping, Sequence

import sidcon.feature
import sidcon.upgrade
from sidcon.converter import Converter
from sidcon.feature import Feature
from sidcon.technology import Era
from sidcon.upgrade import Upgrade

logging.basicConfig()
logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
@typ.final
class Face(object):
    name: str
    features: Sequence[Feature]  # must have at least one
    # TODO: allow this to be a single tuple, since every card except Kt has one Face it upgrades
    # to. Probably requires a name change too. Alternatively, define an `upgrade` @property that
    # fetches either `None` or exactly the single upgrade. (ValueError on len(upgrades)>1)
    upgrades: Sequence[tuple[Era | None, Collection[Upgrade], Face]]

    def __post_init__(self):
        if not self.name:
            raise ValueError("Face must have non-empty name")

        if not self.features:
            raise ValueError(f"Face named '{self.name}' must have at least one Feature")

    @property
    def era(self) -> Era | None:
        if len(self.upgrades) != 1:
            raise ValueError(f"Face '{self.name}' has no unambiguous single Upgrade")
        return self.upgrades[0][0]

    @property
    def converter(self) -> Converter:
        if len(self.features) != 1 or not isinstance(self.features[0], Converter):
            raise ValueError(f"Face '{self.name}' has no unambiguous single Converter")
        return self.features[0]

    @property
    def input_value(self) -> float:
        return self.converter.input_value

    @property
    def output_value(self) -> float:
        return self.converter.output_value

    @property
    def min_input_value(self) -> float:
        return min(c.min_input_value for c in self.features if isinstance(c, Converter))

    @property
    def max_input_value(self) -> float:
        return max(c.max_input_value for c in self.features if isinstance(c, Converter))

    @property
    def min_output_value(self) -> float:
        return min(c.output_value for c in self.features if isinstance(c, Converter))

    @property
    def max_output_value(self) -> float:
        return max(c.output_value for c in self.features if isinstance(c, Converter))

    @classmethod
    def from_strings(
        cls,
        name: str,
        feature_strings: Collection[str],
        era_string: str = "",
        upgrade_string_map: Mapping[Collection[str], Face] = dict(),
    ) -> Face:
        era = Era.from_string(era_string)
        features = [sidcon.feature.from_string(s) for s in feature_strings]
        upgrades = [
            (era, [sidcon.upgrade.from_string(s) for s in upgrade_strings], face)
            for upgrade_strings, face in upgrade_string_map.items()
        ]
        return cls(name=name, features=features, upgrades=upgrades)
