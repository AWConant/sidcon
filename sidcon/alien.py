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
    species_name: typ.ClassVar[str] = acp.abstract_class_property(str)

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
                and subclass.species_name == s
            ):
                return subclass
        raise ValueError(f"couldn't parse Species from string '{s}'")


class Faction(Species, acp.Abstract):
    faction_name: typ.ClassVar[str] = acp.abstract_class_property(str)
    colony_support: typ.ClassVar[float] = acp.abstract_class_property(float)
    tiebreaker: typ.ClassVar[float] = acp.abstract_class_property(float)
    impact: typ.ClassVar[int] = acp.abstract_class_property(int)


class KtZrKtRtl(Species):
    species_name = "Kt'Zr'Kt'Rtl"


class Kjasjavikalimm(Species):
    species_name = "Kjasjavikalimm"


class Caylion(Species):
    species_name = "Caylion"


class Faderan(Species):
    species_name = "Faderan"


class Imdril(Species):
    species_name = "Im'dril"


class EniEt(Species):
    species_name = "Eni Et"


class Unity(Species):
    species_name = "Unity"


class Yengii(Species):
    species_name = "Yengii"


class Zeth(Species):
    species_name = "Zeth"


@typ.final
class CaylionPlutocracy(Caylion, Faction):
    faction_name = "Caylion Plutocracy"
    colony_support = 3
    tiebreaker = 1
    impact = 0


@typ.final
class CaylionCollaborative(Caylion, Faction):
    faction_name = "Caylion Collaborative"
    colony_support = 3
    tiebreaker = 0
    impact = 3


@typ.final
class EniEtAscendancy(EniEt, Faction):
    faction_name = "Eni Et Ascendancy"
    colony_support = 3
    tiebreaker = 3
    impact = 1


@typ.final
class EniEtEngineers(EniEt, Faction):
    faction_name = "Eni Et Engineers"
    colony_support = 3
    tiebreaker = 1.5
    impact = 0


@typ.final
class FaderanConclave(Faderan, Faction):
    faction_name = "Faderan Conclave"
    colony_support = 4
    tiebreaker = 7
    impact = 0


@typ.final
class SocietyofFallingLight(Faderan, Faction):
    faction_name = "Society of Falling Light"
    colony_support = 8
    tiebreaker = -1
    impact = 2


@typ.final
class ImdrilNomads(Imdril, Faction):
    faction_name = "Im'dril Nomads"
    colony_support = 0
    tiebreaker = 8
    impact = 0


@typ.final
class GrandFleet(Imdril, Faction):
    faction_name = "Grand Fleet"
    colony_support = 0
    tiebreaker = 5.5
    impact = 0


@typ.final
class KjasjavikalimmDirectorate(Kjasjavikalimm, Faction):
    faction_name = "Kjasjavikalimm Directorate"
    colony_support = 6
    tiebreaker = 6
    impact = 0


@typ.final
class KjasjavikalimmIndependentNations(Kjasjavikalimm, Faction):
    faction_name = "Kjasjavikalimm Independent Nations"
    colony_support = 5
    tiebreaker = 7.5
    impact = 0


@typ.final
class KtZrKtRtlAdhocracy(KtZrKtRtl, Faction):
    faction_name = "Kt'Zr'Kt'Rtl Adhocracy"
    colony_support = math.inf
    tiebreaker = math.inf
    impact = 0


@typ.final
class KtZrKtRtlTechnophiles(KtZrKtRtl, Faction):
    faction_name = "Kt'Zr'Kt'Rtl Technophiles"
    colony_support = 3
    tiebreaker = 10
    impact = 1


@typ.final
class ShallowUnity(Unity, Faction):
    faction_name = "Unity"
    colony_support = 1
    tiebreaker = 4
    impact = 0


@typ.final
class DeepUnity(Unity, Faction):
    faction_name = "Deep Unity"
    colony_support = 3
    tiebreaker = math.pi
    impact = 0


@typ.final
class YengiiSociety(Yengii, Faction):
    faction_name = "Yengii Society"
    colony_support = 3
    tiebreaker = 5
    impact = 0


@typ.final
class YengiiJii(Yengii, Faction):
    faction_name = "Yengii Jii"
    colony_support = 3
    tiebreaker = 6.5
    impact = 2


@typ.final
class ZethAnocracy(Zeth, Faction):
    faction_name = "Zeth Anocracy"
    colony_support = 3
    tiebreaker = 2
    impact = 2


@typ.final
class CharitySyndicate(Zeth, Faction):
    faction_name = "Charity Syndicate"
    colony_support = 0
    tiebreaker = 4.5
    impact = 1


faction_to_species: Mapping[type[Faction], type[Species]] = {
    c: next(b for b in c.__bases__ if issubclass(b, Species))
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c) and acp.Abstract not in c.__bases__ and issubclass(c, Faction)
}

faction_name_to_faction: Mapping[str, type[Faction]] = {
    c.faction_name: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c) and acp.Abstract not in c.__bases__ and issubclass(c, Faction)
}
