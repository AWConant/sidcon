from __future__ import annotations

import dataclasses
import enum
import logging
import typing as typ
from collections.abc import Collection, Mapping, Sequence, Set

from frozendict import frozendict

import sidcon.converter
import sidcon.cost
import sidcon.exception
import sidcon.faction
import sidcon.feature
import sidcon.upgrade
from sidcon.cost import Cost
from sidcon.face import Face
from sidcon.faction import Faction, KtZrKtRtl, Species
from sidcon.feature import Feature
from sidcon.row import Row
from sidcon.technology import Era, Technology
from sidcon.unit import Colony
from sidcon.upgrade import Upgrade

logging.basicConfig()
logger = logging.getLogger(__name__)


# TODO: All of these name lists should be unexported, and instead the constructors should raise an
# exception when the name doesn't match.
starting_race_card_front_name: str = "Starting Race Card"

interest_converter_card_front_names: Set[str] = frozenset(
    [
        "Cultural Charity",
        "Volunteer Medical Movement",
        "Mutual Understanding",
        "Elder's Wisdom",
        "Intercultural Archive",
        "Xenotech Pool",
    ]
)

kt_colony_card_front_names: Set[str] = frozenset(
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

undesirable_card_front_names: Set[str] = frozenset(
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

project_card_front_names: typ.Final[Set[str]] = frozenset(
    [
        "Hyperspace Consortium",
        "Low Caylius Orbital Factories",
        "Oceanic Settlement",
        "Gamified Research",
    ]
)

relic_world_card_front_names: Set[str] = frozenset(
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

# TODO: use mypy literals for card names.

kt_left_card_names: Set[str] = frozenset(
    {
        "Expansive Social",
        "Hand Crafted",
        "Anarchic Sacrificial",
        "Vast Distance",
        "Diverse",
        "Alien Cultural",
    }
)

kt_right_card_names: Set[str] = frozenset(
    {
        "Diffusion",
        "Polyutility Components",
        "High-Risk Laboratories",
        "Bending Engines",
        "Interspecies Housing",
        "Inspiration",
    }
)

# bidirectional
kt_card_name_mapping: Mapping[str, str] = frozendict(
    {
        "Expansive Social": "Diffusion",
        "Diffusion": "Expansive Social",
        "Hand Crafted": "Polyutility Components",
        "Polyutility Components": "Hand Crafted",
        "Anarchic Sacrificial": "High-Risk Laboratories",
        "High-Risk Laboratories": "Anarchic Sacrificial",
        "Vast Distance": "Bending Engines",
        "Bending Engines": "Vast Distance",
        "Diverse": "Interspecies Housing",
        "Interspecies Housing": "Diverse",
        "Alien Cultural": "Inspiration",
        "Inspiration": "Alien Cultural",
    }
)


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

    @property
    def name(self) -> str:
        return self.front.name

    @property
    def era(self) -> Era | None:
        return self.front.era

    @classmethod
    def from_row(cls, r: Row) -> Card:
        back: Face | None = None
        if r.back_name:
            back = Face.from_strings(r.back_name, r.back_feature_strings)

        upgrade_string_map: Mapping[Collection[str], Face] = dict()
        if back is not None and len(r.upgrade_strings) > 0:
            # Assumption: no card upgrades for free.
            upgrade_string_map = {frozenset(r.upgrade_strings): back}

        front = Face.from_strings(
            r.front_name,
            r.front_feature_strings,
            era_string=r.era,
            upgrade_string_map=upgrade_string_map,
        )

        return Card(front=front)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesCard(Card):
    species: type[Species]

    @classmethod
    def from_row(cls, r: Row) -> SpeciesCard:
        c = super().from_row(r)
        faction_name = r.faction_name
        try:
            species = Species.from_string(faction_name)
        except ValueError:
            faction = sidcon.faction.name_to_faction[faction_name]
            species = sidcon.faction.to_species[faction]
        return SpeciesCard(front=c.front, species=species)


@dataclasses.dataclass(frozen=True, kw_only=True)
class FactionCard(SpeciesCard):
    faction: type[Faction]

    @classmethod
    def from_row(cls, r: Row) -> FactionCard:
        c = super().from_row(r)
        faction_name = r.faction_name
        faction = sidcon.faction.name_to_faction[faction_name]

        return FactionCard(front=c.front, species=c.species, faction=faction)


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
        return TechnologyCard(front=c.front, species=c.species, technology=technology)


class Starting(object):
    ...


# TODO: Maybe add Star/Moon to this?
@dataclasses.dataclass(frozen=True, kw_only=True)
class StartingCard(FactionCard, Starting):
    @classmethod
    def from_row(cls, r: Row) -> StartingCard:
        c = super().from_row(r)
        return StartingCard(front=c.front, species=c.species, faction=c.faction)


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class SetupCard(FactionCard, Starting):
    colonies: Collection["Colony"]
    research_teams: Collection["ResearchTeam"]

    @classmethod
    def from_row(cls, r: Row) -> SetupCard:
        copied_row = r.copy(upgrade1="", upgrade2="")
        # TODO: Parse upgrade1 and upgrade2 as colonies/research teams here. When you do, consider
        # updating the type hint from Collection to Set, or list, or something.
        c = super().from_row(copied_row)
        return SetupCard(
            front=c.front,
            species=c.species,
            faction=c.faction,
            colonies=[],
            research_teams=[],
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class InterestConverterCard(StartingCard):
    @classmethod
    def from_row(cls, r: Row) -> InterestConverterCard:
        c = super().from_row(r)
        return InterestConverterCard(
            front=c.front,
            faction=c.faction,
            species=c.species,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ColonyCard(Card):
    @classmethod
    def from_row(cls, r: Row) -> ColonyCard:
        c = super().from_row(r)
        return ColonyCard(front=c.front)


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
            species=c.species,
            faction=c.faction,
            cost=cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class KtColonyCard(CreatedCard, FrontedColonyCard):
    @classmethod
    def from_row(cls, r: Row) -> KtColonyCard:
        created_card = CreatedCard.from_row(r)
        fronted_colony_card = FrontedColonyCard.from_row(r)
        return KtColonyCard(
            front=created_card.front,
            species=created_card.species,
            faction=created_card.faction,
            front_type=fronted_colony_card.front_type,
            cost=created_card.cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class KtDualCard(StartingCard):
    @classmethod
    def from_rows(cls, left_row: Row, right_row: Row) -> KtDualCard:
        left_card = super().from_row(left_row)
        right_card = super().from_row(right_row)
        return KtDualCard(
            front=cls._merged_face(
                left_card.front,
                right_card.front,
            ),
            species=KtZrKtRtl,
            faction=left_card.faction,
        )

    @staticmethod
    def _merged_face(left_face: Face, right_face: Face) -> Face:
        return Face(
            name=f"{left_face.name} {right_face.name}",
            features=KtDualCard._merged_features(left_face.features, right_face.features),
            upgrades=KtDualCard._merged_upgrades(
                left_face, right_face, left_face.upgrades, right_face.upgrades
            ),
        )

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
            mf = sidcon.feature.merged(lf, rf)
            merged.append(mf)
        return merged

    @staticmethod
    def _merged_upgrades(
        left_face: Face,
        right_face: Face,
        left_upgrades: Sequence[tuple[Era | None, Collection[Upgrade], Face]],
        right_upgrades: Sequence[tuple[Era | None, Collection[Upgrade], Face]],
    ) -> list[tuple[Era | None, Collection[Upgrade], Face]]:
        merged_upgrades = []
        for (left_era, left_upgrade, left_upgraded_face) in left_upgrades:
            merged_upgrades.append(
                (left_era, left_upgrade, KtDualCard._merged_face(left_upgraded_face, right_face))
            )
        for (right_era, right_upgrade, right_upgraded_face) in right_upgrades:
            merged_upgrades.append(
                (right_era, right_upgrade, KtDualCard._merged_face(left_face, right_upgraded_face))
            )
        return merged_upgrades


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class UndesirableCard(SpeciesCard):
    @classmethod
    def from_row(cls, r: Row) -> UndesirableCard:
        c = super().from_row(r)
        return UndesirableCard(front=c.front, species=c.species)


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class ProjectCard(CreatedCard):
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
            species=c.species,
            faction=c.faction,
            cost=c.cost,
            back_cost=back_cost,
        )


@typ.final
@dataclasses.dataclass(frozen=True, kw_only=True)
class RelicWorldCard(CreatedCard):
    @classmethod
    def from_row(cls, r: Row) -> RelicWorldCard:
        c = super().from_row(r)
        return RelicWorldCard(
            front=c.front,
            species=c.species,
            faction=c.faction,
            cost=c.cost,
        )
