from __future__ import annotations

import dataclasses
import logging
import typing as typ
from collections.abc import Collection, Mapping, Sequence

import sidcon.feature
import sidcon.upgrade
from sidcon.converter import Converter
from sidcon.feature import Feature
from sidcon.upgrade import Upgrade

logging.basicConfig()
logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
@typ.final
class Face(object):
    name: str
    features: Sequence[Feature]  # must have at least one
    upgrades: Mapping[Collection[Upgrade], Face]

    def __post_init__(self):
        if not self.name:
            raise ValueError("Face must have non-empty name")

        if not self.features:
            raise ValueError(f"Face named '{self.name}' must have at least one Feature")

    @property
    def converter(self):
        if len(self.features) != 1 or not isinstance(self.features[0], Converter):
            raise ValueError(f"Face '{self.name}' has no unambiguous single Converter")
        return self.features[0]

    @property
    def input_value(self):
        if len(self.features) > 1:
            raise ValueError(
                f"Face '{self.name}' with multiple features has no unambiguous input value"
            )
        return self.features[0].input_value

    @property
    def output_value(self):
        if len(self.features) > 1:
            raise ValueError(
                f"Face '{self.name}' with multiple features has no unambiguous output value"
            )
        return self.features[0].output_value

    @property
    def min_input_value(self):
        return min(c.min_input_value for c in self.features)

    @property
    def max_input_value(self):
        return max(c.max_input_value for c in self.features)

    @property
    def min_output_value(self):
        return min(c.output_value for c in self.features)

    @property
    def max_output_value(self):
        return max(c.output_value for c in self.features)

    @classmethod
    def from_strings(
        cls,
        name: str,
        feature_strings: Collection[str],
        upgrade_string_map: Mapping[Collection[str], Face],
    ) -> Face:
        features = [sidcon.feature.from_string(s) for s in feature_strings]
        upgrades: Mapping[Collection[Upgrade], Face] = {
            frozenset([sidcon.upgrade.from_string(s) for s in upgrade_strings]): face
            for upgrade_strings, face in upgrade_string_map.items()
        }
        return cls(name=name, features=features, upgrades=upgrades)
