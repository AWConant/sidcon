from __future__ import annotations

import dataclasses
import enum
import logging
import typing as typ
from collections.abc import Collection, Mapping, Sequence, Set

from frozendict import frozendict

import sidcon.alien
import sidcon.converter
import sidcon.cost
import sidcon.exception
import sidcon.feature
import sidcon.upgrade
from sidcon.alien import Faction, KtZrKtRtl, KtZrKtRtlAdhocracy, KtZrKtRtlTechnophiles, Species
from sidcon.converter import Converter
from sidcon.cost import Cost
from sidcon.face import Face
from sidcon.feature import Feature
from sidcon.row import Row
from sidcon.technology import Era, Technology
from sidcon.unit import Colony
from sidcon.upgrade import Upgrade

logging.basicConfig()
logger = logging.getLogger(__name__)


@typ.final
@enum.unique
class Source(enum.Enum):
    STARTING = "Starting"
    RESEARCH = "Researched"
    UNDESIRABLE = "Undesirable"
    BID = "Bid"
    CREATED = enum.auto()

    @classmethod
    def from_string(cls, s: str) -> Source:
        try:
            return cls(s)
        except ValueError:
            return cls.CREATED


@dataclasses.dataclass(frozen=True, kw_only=True)
class Card(object):
    # TODO: Card number
    front: Face
    back: Face | None

    @property
    def name(self):
        return self.front.name

    @classmethod
    def from_row(cls, r: Row) -> Card:
        back: Face | None = None
        if r.back_name:
            feature_strings = sidcon.feature.back_strings_from_row(r)
            back = Face.from_strings(r.back_name, feature_strings, dict())

        feature_strings = sidcon.feature.front_strings_from_row(r)

        upgrade_string_map: dict[Set[str], Face] = dict()
        if back is not None and len(r.upgrade_strings) > 0:
            # Assumption: no card upgrades for free.
            upgrade_string_map[frozenset(r.upgrade_strings)] = back

        front = Face.from_strings(r.front_name, feature_strings, upgrade_string_map)

        return Card(front=front, back=back)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesCard(Card):
    era: Era | None
    species: type[Species]

    @classmethod
    def from_row(cls, r: Row) -> SpeciesCard:
        c = super().from_row(r)
        faction_title = r.faction_title
        try:
            species = Species.from_string(faction_title)
        except ValueError:
            faction = sidcon.alien.faction_title_to_faction[faction_title]
            species = sidcon.alien.faction_to_species[faction]

        era_string = r.era
        try:
            era = Era(int(era_string))
        except (TypeError, ValueError):
            era = None

        return SpeciesCard(front=c.front, back=c.back, species=species, era=era)


@dataclasses.dataclass(frozen=True, kw_only=True)
class FactionCard(SpeciesCard):
    faction: type[Faction]

    @classmethod
    def from_row(cls, r: Row) -> FactionCard:
        c = super().from_row(r)
        faction_title = r.faction_title
        faction = sidcon.alien.faction_title_to_faction[faction_title]

        return FactionCard(
            front=c.front, back=c.back, species=c.species, era=c.era, faction=faction
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class TechnologyCard(SpeciesCard):
    technology: type[Technology]

    @classmethod
    def from_row(cls, r: Row) -> TechnologyCard:
        c = super().from_row(r)
        technology = Technology.from_string(r.front_name)
        if technology is None:
            raise ValueError(
                "couldn't identify a technology for card with front name '{r.front_name}'"
            )
        return TechnologyCard(
            front=c.front, back=c.back, species=c.species, era=c.era, technology=technology
        )


class Starting(object):
    ...


# TODO: Maybe add Star/Moon to this?
@dataclasses.dataclass(frozen=True, kw_only=True)
class StartingCard(FactionCard, Starting):
    @classmethod
    def from_row(cls, r: Row) -> StartingCard:
        c = super().from_row(r)
        return StartingCard(
            front=c.front, back=c.back, species=c.species, era=c.era, faction=c.faction
        )


# TODO: Rename this to something that doesn't sound like it inherits from StartingCard.
@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class StartingRaceCard(FactionCard, Starting):
    front_name: typ.Final[str] = "Starting Race Card"

    colonies: Collection["Colony"]
    research_teams: Collection["ResearchTeam"]

    @classmethod
    def from_row(cls, r: Row) -> StartingRaceCard:
        copied_row = r.copy(upgrade1="", upgrade2="")
        # TODO: Parse upgrade1 and upgrade2 as colonies/research teams here. When you do, consider
        # updating the type hint from Collection to Set, or list, or something.
        c = super().from_row(copied_row)
        return StartingRaceCard(
            front=c.front,
            back=c.back,
            species=c.species,
            era=c.era,
            faction=c.faction,
            colonies=[],
            research_teams=[],
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class InterestConverterCard(StartingCard):
    _all_front_names: typ.Final[Set[str]] = frozenset(
        [
            "Cultural Charity",
            "Volunteer Medical Movement",
            "Mutual Understanding",
            "Elder's Wisdom",
            "Intercultural Archive",
            "Xenotech Pool",
        ]
    )

    @classmethod
    def from_row(cls, r: Row) -> InterestConverterCard:
        c = super().from_row(r)
        return InterestConverterCard(
            front=c.front,
            back=c.back,
            faction=c.faction,
            species=c.species,
            era=c.era,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ColonyCard(Card):
    @classmethod
    def from_row(cls, r: Row) -> ColonyCard:
        c = super().from_row(r)
        return ColonyCard(front=c.front, back=c.back)


@dataclasses.dataclass(frozen=True, kw_only=True)
class FrontedColonyCard(ColonyCard):
    front_type: type[Colony]

    @classmethod
    def from_row(cls, r: Row) -> FrontedColonyCard:
        front_colony_key, front_converter = r.front_converter.split(",", 1)
        # TODO: Why do we need to copy this?
        copied_row = r.copy(
            front_converter=front_converter,
        )
        c = super().from_row(copied_row)
        return FrontedColonyCard(
            front=c.front,
            back=c.back,
            front_type=Colony.from_key(front_colony_key),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DualFacedColonyCard(FrontedColonyCard):
    back_type: type[Colony]

    @classmethod
    def from_row(cls, r: Row) -> DualFacedColonyCard:
        back_colony_key, back_converter = r.back_converter.split(",", 1)
        # TODO: Why do we need to copy this?
        copied_row = r.copy(
            back_converter=back_converter,
        )
        c = super().from_row(copied_row)
        return DualFacedColonyCard(
            front=c.front,
            back=c.back,
            front_type=c.front_type,
            back_type=Colony.from_key(back_colony_key),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ResearchTeam(Card):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CreatedCard(FactionCard):
    cost: Cost
    # TODO: Should cost move to Face...? It's a failure of abstraction, but I have no idea how to
    # deal with Kt.

    @classmethod
    def from_row(cls, r: Row) -> CreatedCard:
        c = super().from_row(r)
        cost = sidcon.cost.from_string(r.cost)
        return CreatedCard(
            front=c.front,
            back=c.back,
            species=c.species,
            era=c.era,
            faction=c.faction,
            cost=cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class KtColonyCard(CreatedCard, FrontedColonyCard):
    _all_front_names: typ.Final[Set[str]] = frozenset(
        [
            "Zd'Nx",
            "Kz'Tlr",
            "Kln'Qn",
            "Nz'Cht'Qt'Rz",
            "Tn'Rg'Tx'Tc",
            "Gz'Zd",
            "!IN'ZR'KZ",
            "Tk'T!'Zk",
            "Kr'Xn'Xx",
            "Kt'Dq'Rn'Nr",
            "Nx'Xt'!In",
            "Nx'Dr",
            "Nz'Tt",
        ]
    )

    # TODO: Is the FactionCard data model actually right? The spreadsheet has these as era 1 cards,
    # but I don't see any indication that they are era 1 on the actual card. If they aren't, then
    # faction cards don't necessarily have an era, or these aren't faction cards.
    @classmethod
    def from_row(cls, r: Row) -> KtColonyCard:
        created_card = CreatedCard.from_row(r)
        fronted_colony_card = FrontedColonyCard.from_row(r)
        return KtColonyCard(
            front=created_card.front,
            back=None,
            species=created_card.species,
            era=created_card.era,
            faction=created_card.faction,
            front_type=fronted_colony_card.front_type,
            cost=created_card.cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class KtDualCard(Starting):
    left_name_to_right_name: typ.Final[Mapping[str, str]] = frozendict(
        {
            # Base game
            "Expansive Social": "Diffusion",
            "Hand Crafted": "Polyutility Components",
            "Anarchic Sacrificial": "High-Risk Laboratories",
            # Bifurcation
            "Vast Distance": "Bending Engines",
            "Diverse": "Interspecies Housing",
            "Alien Cultural": "Inspiration",
        }
    )

    left: FactionCard
    right: FactionCard
    species = KtZrKtRtl

    @property
    def name(self) -> str:
        return f"{self.left.name} {self.right.name}"

    @property
    def faction(self) -> type[Faction]:
        return self.left.faction

    @property
    def front(self) -> Face:
        return self._merged_face(self.left.front, self.right.front)

    @property
    def back(self) -> Face | None:
        if self.left.back is None or self.right.back is None:
            return None
        return self._merged_face(self.left.back, self.right.back)

    @property
    def frontback(self) -> Face | None:
        if self.right.back is None:
            return None
        return self._merged_face(self.left.front, self.right.back)

    @property
    def backfront(self) -> Face | None:
        if self.left.back is None:
            return None
        return self._merged_face(self.left.back, self.right.front)

    def __post_init__(self):
        both_cards = [self.left, self.right]
        if not all(c.species is KtZrKtRtl for c in both_cards):
            raise ValueError(
                "KtDualCard must consist of KtZrKtRtl cards, "
                f"not {[c.species for c in both_cards]}"
            )
        if self.left.faction != self.right.faction:
            raise ValueError(
                "KtDualCard.left and right must have same faction; "
                f"got '{self.left.faction}' and '{self.right.faction}'"
            )
        if (
            self.left.faction is not KtZrKtRtlAdhocracy
            and self.right.faction is not KtZrKtRtlTechnophiles
        ):
            raise ValueError(f"faction must be a Kt'Zr'Kt'Rtl faction; not {self.faction}")
        for left_name, right_name in self.left_name_to_right_name.items():
            if self.left.name == left_name:
                if self.right.name != right_name:
                    raise ValueError(
                        f"KtDualCard has valid left name '{self.left.name}' with "
                        f"non-matching right name '{self.right.name}'"
                    )
                break
        else:
            raise ValueError(f"KtDualCard has invalid left name '{self.left.name}'")

    @classmethod
    def coalesced_cards(cls, cs: Sequence[Card]) -> list["Card | KtDualCard"]:
        left_name_to_index: dict[str, int] = dict()
        right_name_to_index: dict[str, int] = dict()
        for i, c in enumerate(cs):
            for left_name, right_name in cls.left_name_to_right_name.items():
                if c.name == left_name:
                    left_name_to_index[left_name] = i
                elif c.name == right_name:
                    right_name_to_index[right_name] = i

        coalesced: list["Card | KtDualCard"] = []

        for name, index in left_name_to_index.items():
            left_card = cs[index]
            right_card = cs[right_name_to_index[cls.left_name_to_right_name[name]]]
            assert isinstance(left_card, FactionCard)
            assert isinstance(right_card, FactionCard)
            card = KtDualCard(left=left_card, right=right_card)
            coalesced.append(card)

        indices_to_exclude = set().union(left_name_to_index.values(), right_name_to_index.values())
        for i, c in enumerate(cs):
            if i not in indices_to_exclude:
                coalesced.append(c)

        return coalesced

    @staticmethod
    def _merged_face(left_face: Face, right_face: Face) -> Face:
        name = f"{left_face.name} {right_face.name}"
        features = KtDualCard._merged_features(left_face.features, right_face.features)
        # TODO: Figure out how to express upgrades.
        # upgrade = KtDualCard._merged_upgrades(left_face.upgrades, right_face.upgrades)
        return Face(name=name, features=features, upgrades=dict())

    @staticmethod
    def _merged_features(
        left_features: Sequence[Feature], right_features: Sequence[Feature]
    ) -> list[Feature]:
        if len(left_features) != len(right_features):
            raise ValueError(
                "len of input sequences must be identical; "
                f"{len(left_features)} != {len(right_features)}"
            )
        merged: list[Feature] = []
        for lf, rf in zip(left_features, right_features):
            if isinstance(lf, Converter) and isinstance(rf, Mapping):
                # Right halves of Kt converters do not include the arrow, so they need to be mapped
                # to "free" converters before being merged.
                rf = lf.__class__.from_counted_units(rf)
            mf = sidcon.feature.merged(lf, rf)
            merged.append(mf)
        return merged

    @staticmethod
    def _merged_upgrades(
        left_upgrades: Sequence[Upgrade], right_upgrades: Sequence[Upgrade]
    ) -> list[Upgrade]:
        if len(left_upgrades) != len(right_upgrades):
            raise ValueError(
                "len of input sequences must be identical; "
                f"{len(left_upgrades)} != {len(right_upgrades)}"
            )
        return [sidcon.upgrade.merged(lf, rf) for lf, rf in zip(left_upgrades, right_upgrades)]


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class UndesirableCard(SpeciesCard):
    _all_front_names: typ.Final[Set[str]] = frozenset(
        [
            "The Uprooted",  # Caylion
            "Hadopelagic Exiles",  # Eni Et
            "Zealots",  # Faderan
            "Disaffected Artists",  # Im'dril
            "Anosmia",  # Kjasjavikalimm
            "Loafers",  # Kt'Zr'Kt'Rtl
            "Free Slices",  # Unity
            "Iconoclasts",  # Yengii
        ]
    )

    @classmethod
    def from_row(cls, r: Row) -> UndesirableCard:
        c = super().from_row(r)
        return UndesirableCard(
            front=c.front,
            back=c.back,
            species=c.species,
            era=c.era,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class ProjectCard(CreatedCard):
    _all_front_names: typ.Final[Set[str]] = frozenset(
        [
            "Hyperspace Consortium",
            "Low Caylius Orbital Factories",
            "Oceanic Settlement",
            "Gamified Research",
        ]
    )
    back_cost: Cost

    @classmethod
    def from_row(cls, r: Row) -> ProjectCard:
        copied_row = r.copy(
            front_name=f"{r.front_name} ({r.front_converter})",
            upgrade3="",
        )
        c = super().from_row(copied_row)

        back_cost = sidcon.cost.from_string(r.upgrade3)
        return ProjectCard(
            front=c.front,
            back=c.back,
            species=c.species,
            era=c.era,
            faction=c.faction,
            cost=c.cost,
            back_cost=back_cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class RelicWorldCard(CreatedCard):
    _all_front_names: typ.Final[Set[str]] = frozenset(
        [
            # TODO: Gift of the Duruntai is technically not a Faderan card, since it can be traded
            # permanently... There isn't really a good way to express this, since RelicWorldCards
            # are CreatedCards, which are FactionCards, which cannot be traded permanently.
            "Gift of the Duruntai",
            "Contextual Integrator Cache",
            "Automated Transport Network",
            "Relic Detector",
            "Library of Entelechy",
            "Transmutive Decomposer",
            "Nalgorian Grindstone",
            "Star's Ruin",
            "Paradise Converter",
            "Barian Trade Armada",
            "Thil's Demiring",
            "The Grand Armilla",
        ]
    )

    @classmethod
    def from_row(cls, r: Row) -> RelicWorldCard:
        c = super().from_row(r)
        return RelicWorldCard(
            front=c.front,
            back=c.back,
            species=c.species,
            era=c.era,
            faction=c.faction,
            cost=c.cost,
        )
