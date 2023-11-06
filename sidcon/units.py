import inspect
import logging
import sys
import typing as typ
from collections.abc import Mapping

import abstractcp as acp

logging.basicConfig()
logger = logging.getLogger(__name__)


class Unit(acp.Abstract):
    name: typ.ClassVar[str] = acp.abstract_class_property(str)
    key: typ.ClassVar[str] = acp.abstract_class_property(str)


UnitT = typ.TypeVar("UnitT", bound=Unit)


class ConsumableUnit(Unit, acp.Abstract):
    """A Unit that is destroyed when fed as input to a Converter."""

    ...


class DonationUnit(Unit, acp.Abstract):
    ...


class ValuableUnit(ConsumableUnit, acp.Abstract):
    """A Unit that has a prescribed fair trade value."""

    value: typ.ClassVar[float] = acp.abstract_class_property(float)


class Small(ValuableUnit, acp.Abstract):
    value = 1


class Large(ValuableUnit, acp.Abstract):
    value = 1.5


class Colony(ConsumableUnit, acp.Abstract):
    @classmethod
    def from_key(cls, key: str) -> type["Colony"]:
        for subclass in cls.__subclasses__():
            if subclass.key == key:
                return subclass
        raise ValueError(f"key '{key}' is not a valid Colony key")


@typ.final
class AnyColony(Colony):
    name = "Any colony"
    key = "N"


@typ.final
class DesertColony(Colony):
    name = "Desert colony"
    key = "D"


@typ.final
class IceColony(Colony):
    name = "Ice colony"
    key = "I"


@typ.final
class JungleColony(Colony):
    name = "Jungle colony"
    key = "J"


@typ.final
class OceanColony(Colony):
    name = "Ocean colony"
    key = "W"


class Ultratech(ValuableUnit):
    name = "Ultratech"
    key = "U"
    value = 3


class Ship(ValuableUnit):
    name = "Ship"
    key = "*"
    value = 1


class VictoryPoint(ValuableUnit):
    name = "Victory point"
    key = "$"
    value = 3


class Yellow(Large):
    name = "Yellow cube"
    key = "Y"


class Blue(Large):
    name = "Blue cube"
    key = "T"


class Black(Large):
    name = "Black cube"
    key = "B"


class White(Small):
    name = "White cube"
    key = "w"


class Brown(Small):
    name = "Brown cube"
    key = "b"


class Green(Small):
    name = "Green cube"
    key = "g"


@typ.final
class DonationUltratech(DonationUnit, Ultratech):
    name = "Ultratech (donation)"


@typ.final
class DonationShip(DonationUnit, Ship):
    name = "Ship (donation)"


@typ.final
class DonationVictoryPoint(DonationUnit, VictoryPoint):
    name = "Victory point (donation)"


@typ.final
class DonationYellow(DonationUnit, Yellow):
    name = "Yellow cube (donation)"


@typ.final
class DonationBlue(DonationUnit, Blue):
    name = "Blue cube (donation)"


@typ.final
class DonationBlack(DonationUnit, Black):
    name = "Black cube (donation)"


@typ.final
class DonationWhite(DonationUnit, White):
    name = "White cube (donation)"


@typ.final
class DonationBrown(DonationUnit, Brown):
    name = "Brown cube (donation)"


@typ.final
class DonationGreen(DonationUnit, Green):
    name = "Green cube (donation)"


# Weird stuff


class AnyLarge(Large):
    name = "Any large cube"
    key = "L"


@typ.final
class DonationAnyLarge(DonationUnit, AnyLarge):
    name = "Any large cube (donation)"


class AnySmall(Small):
    name = "Any small cube"
    key = "s"


@typ.final
class DonationAnySmall(DonationUnit, Small):
    name = "Any small cube (donation)"
    key = "s"


class SmallWild(Small):
    name = "Small wild cube"
    key = "a"


@typ.final
class DonationSmallWild(DonationUnit, SmallWild):
    name = "Small wild cube (donation)"


class LargeWild(Large):
    name = "Large wild cube"
    key = "A"


@typ.final
class DonationLargeWild(DonationUnit, LargeWild):
    ...


@typ.final
class KtZrKtRtlUltratechCost(Ultratech):
    name = "Kt'Zr'Kt'Rtl Ultratech cost"
    key = "K"


class Envoy(Unit):
    name = "Envoy"
    key = "Z"  # "Zeth envoy"


@typ.final
class DonationEnvoy(DonationUnit, Envoy):
    name = "Envoy (donation)"


@typ.final
class FleetSupport(Unit):
    name = "Fleet support"
    key = "F"


@typ.final
class RelicWorld(Unit):
    name = "Relic world"
    key = "R"


@typ.final
class ServiceToken(Unit):
    name = "Service token"
    key = "½"


@typ.final
class SmallOrbitalFactory(Unit):
    name = "Small orbital factory"
    key = "o"


@typ.final
class LargeOrbitalFactory(Unit):
    name = "Large orbital factory"
    key = "O"


@typ.final
class SharingBonus(Unit):
    name = "Sharing bonus"
    key = "X"


key_to_non_donation_unit: Mapping[str, type[Unit]] = {
    c.key: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c)
    and acp.Abstract not in c.__bases__
    and issubclass(c, Unit)
    and not issubclass(c, DonationUnit)
}

key_to_donation_unit: Mapping[str, type[DonationUnit]] = {
    c.key: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c)
    and acp.Abstract not in c.__bases__
    and issubclass(c, Unit)
    and issubclass(c, DonationUnit)
}
