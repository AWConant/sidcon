import inspect
import logging
import math
import sys
import typing as typ
from collections.abc import Mapping

import abstractcp as acp

SpeciesT = typ.TypeVar("SpeciesT", bound="Species")

logging.basicConfig()
logger = logging.getLogger(__name__)


# TODO: Split this file into species.py and faction.py


class Species(acp.Abstract):
    # TODO: Rename title to species_name, to disambiguate from faction name.
    name: typ.ClassVar[str] = acp.abstract_class_property(str)

    @classmethod
    def from_string(cls, s: str) -> type["Species"]:
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)]
            )

        for subclass in all_subclasses(cls):
            if (
                acp.Abstract not in subclass.__bases__
                and Faction not in subclass.__bases__
                and subclass.name == s
            ):
                return subclass
        raise ValueError(f"couldn't parse Species from string '{s}'")


class Faction(Species, acp.Abstract):
    # TODO: Rename title to faction_name, to disambiguate from species name. Also update
    # `faction_title_to_faction`.
    title: typ.ClassVar[str] = acp.abstract_class_property(str)
    colony_support: typ.ClassVar[float] = acp.abstract_class_property(float)
    tiebreaker: typ.ClassVar[float] = acp.abstract_class_property(float)
    impact: typ.ClassVar[int] = acp.abstract_class_property(int)


class KtZrKtRtl(Species):
    name = "Kt'Zr'Kt'Rtl"


class Kjasjavikalimm(Species):
    name = "Kjasjavikalimm"


class Caylion(Species):
    name = "Caylion"


class Faderan(Species):
    name = "Faderan"


class Imdril(Species):
    name = "Im'dril"


class EniEt(Species):
    name = "Eni Et"


class Unity(Species):
    name = "Unity"


class Yengii(Species):
    name = "Yengii"


class Zeth(Species):
    name = "Zeth"


@typ.final
class CaylionPlutocracy(Caylion, Faction):
    title = "Caylion Plutocracy"
    colony_support = 3
    tiebreaker = 1
    impact = 0


@typ.final
class CaylionCollaborative(Caylion, Faction):
    title = "Caylion Collaborative"
    colony_support = 3
    tiebreaker = 0
    impact = 3


@typ.final
class EniEtAscendancy(EniEt, Faction):
    title = "Eni Et Ascendancy"
    colony_support = 3
    tiebreaker = 3
    impact = 1


@typ.final
class EniEtEngineers(EniEt, Faction):
    title = "Eni Et Engineers"
    colony_support = 3
    tiebreaker = 1.5
    impact = 0


@typ.final
class FaderanConclave(Faderan, Faction):
    title = "Faderan Conclave"
    colony_support = 4
    tiebreaker = 7
    impact = 0


@typ.final
class SocietyofFallingLight(Faderan, Faction):
    title = "Society of Falling Light"
    colony_support = 8
    tiebreaker = -1
    impact = 2


@typ.final
class ImdrilNomads(Imdril, Faction):
    title = "Im'dril Nomads"
    colony_support = 0
    tiebreaker = 8
    impact = 0


@typ.final
class GrandFleet(Imdril, Faction):
    title = "Grand Fleet"
    colony_support = 0
    tiebreaker = 5.5
    impact = 0


@typ.final
class KjasjavikalimmDirectorate(Kjasjavikalimm, Faction):
    title = "Kjasjavikalimm Directorate"
    colony_support = 6
    tiebreaker = 6
    impact = 0


@typ.final
class KjasjavikalimmIndependentNations(Kjasjavikalimm, Faction):
    title = "Kjasjavikalimm Independent Nations"
    colony_support = 5
    tiebreaker = 7.5
    impact = 0


@typ.final
class KtZrKtRtlAdhocracy(KtZrKtRtl, Faction):
    title = "Kt'Zr'Kt'Rtl Adhocracy"
    colony_support = math.inf
    tiebreaker = math.inf
    impact = 0


@typ.final
class KtZrKtRtlTechnophiles(KtZrKtRtl, Faction):
    title = "Kt'Zr'Kt'Rtl Technophiles"
    colony_support = 3
    tiebreaker = 10
    impact = 1


@typ.final
class ShallowUnity(Unity, Faction):
    title = "Unity"
    colony_support = 1
    tiebreaker = 4
    impact = 0


@typ.final
class DeepUnity(Unity, Faction):
    title = "Deep Unity"
    colony_support = 3
    tiebreaker = math.pi
    impact = 0


@typ.final
class YengiiSociety(Yengii, Faction):
    title = "Yengii Society"
    colony_support = 3
    tiebreaker = 5
    impact = 0


@typ.final
class YengiiJii(Yengii, Faction):
    title = "Yengii Jii"
    colony_support = 3
    tiebreaker = 6.5
    impact = 2


@typ.final
class ZethAnocracy(Zeth, Faction):
    title = "Zeth Anocracy"
    colony_support = 3
    tiebreaker = 2
    impact = 2


@typ.final
class CharitySyndicate(Zeth, Faction):
    title = "Charity Syndicate"
    colony_support = 0
    tiebreaker = 4.5
    impact = 1


faction_to_species: Mapping[type[Faction], type[Species]] = {
    c: next(b for b in c.__bases__ if issubclass(b, Species))
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c) and acp.Abstract not in c.__bases__ and issubclass(c, Faction)
}

faction_title_to_faction: Mapping[str, type[Faction]] = {
    c.title: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c) and acp.Abstract not in c.__bases__ and issubclass(c, Faction)
}
