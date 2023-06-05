import inspect
import logging
import sys
import typing as typ
from collections.abc import Mapping

import abstractcp as acp

logging.basicConfig()
logger = logging.getLogger(__name__)


class Good(acp.Abstract):
    name: typ.ClassVar[str] = acp.abstract_class_property(str)
    key: typ.ClassVar[str] = acp.abstract_class_property(str)


GoodT = typ.TypeVar("GoodT", bound=Good)


class ConsumableGood(Good, acp.Abstract):
    """A Good that is destroyed when fed as input to a Converter."""

    ...


class DonationGood(Good, acp.Abstract):
    ...


class ValuableGood(ConsumableGood, acp.Abstract):
    """A Good that has a prescribed fair trade value."""

    value: typ.ClassVar[float] = acp.abstract_class_property(float)


class Small(ValuableGood, acp.Abstract):
    value = 1


class Large(ValuableGood, acp.Abstract):
    value = 1.5


class Colony(ConsumableGood, acp.Abstract):
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


class Ultratech(ValuableGood):
    name = "Ultratech"
    key = "U"
    value = 3


class Ship(ValuableGood):
    name = "Ship"
    key = "*"
    value = 1


class VictoryPoint(ValuableGood):
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
class DonationUltratech(DonationGood, Ultratech):
    name = "Ultratech (donation)"


@typ.final
class DonationShip(DonationGood, Ship):
    name = "Ship (donation)"


@typ.final
class DonationVictoryPoint(DonationGood, VictoryPoint):
    name = "Victory point (donation)"


@typ.final
class DonationYellow(DonationGood, Yellow):
    name = "Yellow cube (donation)"


@typ.final
class DonationBlue(DonationGood, Blue):
    name = "Blue cube (donation)"


@typ.final
class DonationBlack(DonationGood, Black):
    name = "Black cube (donation)"


@typ.final
class DonationWhite(DonationGood, White):
    name = "White cube (donation)"


@typ.final
class DonationBrown(DonationGood, Brown):
    name = "Brown cube (donation)"


@typ.final
class DonationGreen(DonationGood, Green):
    name = "Green cube (donation)"


# Weird stuff


class AnyLarge(Large):
    name = "Any large cube"
    key = "L"


@typ.final
class DonationAnyLarge(DonationGood, AnyLarge):
    name = "Any large cube (donation)"


class AnySmall(Small):
    name = "Any small cube"
    key = "s"


@typ.final
class DonationAnySmall(DonationGood, Small):
    name = "Any small cube (donation)"
    key = "s"


class SmallWild(Small):
    name = "Small wild cube"
    key = "a"


@typ.final
class DonationSmallWild(DonationGood, SmallWild):
    name = "Small wild cube (donation)"


class LargeWild(Large):
    name = "Large wild cube"
    key = "A"


@typ.final
class DonationLargeWild(DonationGood, LargeWild):
    ...


@typ.final
class KtZrKtRtlUltratechCost(Ultratech):
    name = "Kt'Zr'Kt'Rtl Ultratech cost"
    key = "K"


class Envoy(Good):
    name = "Envoy"
    key = "Z"  # "Zeth envoy"


@typ.final
class DonationEnvoy(DonationGood, Envoy):
    name = "Envoy (donation)"


@typ.final
class FleetSupport(Good):
    name = "Fleet support"
    key = "F"


@typ.final
class RelicWorld(Good):
    name = "Relic world"
    key = "R"


@typ.final
class ServiceToken(Good):
    name = "Service token"
    key = "½"


@typ.final
class SmallOrbitalFactory(Good):
    name = "Small orbital factory"
    key = "o"


@typ.final
class LargeOrbitalFactory(Good):
    name = "Large orbital factory"
    key = "O"


@typ.final
class SharingBonus(Good):
    name = "Sharing bonus"
    key = "X"


key_to_non_donation_good: Mapping[str, type[Good]] = {
    c.key: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c)
    and acp.Abstract not in c.__bases__
    and issubclass(c, Good)
    and not issubclass(c, DonationGood)
}

key_to_donation_good: Mapping[str, type[DonationGood]] = {
    c.key: c
    for name, c in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(c)
    and acp.Abstract not in c.__bases__
    and issubclass(c, Good)
    and issubclass(c, DonationGood)
}
