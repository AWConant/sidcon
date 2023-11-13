import argparse
import functools
import itertools
import logging
import typing as typ
from collections import defaultdict
from collections.abc import Sequence
from pprint import pprint  # noqa

import sidcon.parse
from sidcon.alien import (
    Caylion,
    CharitySyndicate,
    EniEt,
    Faction,
    Faderan,
    Imdril,
    Kjasjavikalimm,
    KtZrKtRtl,
    Species,
    Unity,
    Yengii,
    Zeth,
)
from sidcon.card import Card, KtDualCard, Starting, StartingCard, UndesirableCard
from sidcon.converter import Converter
from sidcon.face import Face
from sidcon.technology import Era

logging.basicConfig()
logger = logging.getLogger(__name__)


@typ.runtime_checkable
class StartingCardlike(typ.Protocol):
    front: Face
    era: Era
    species: type[Species]
    faction: type[Faction]


ALL_SPECIES = {
    "Caylion": Caylion,
    "EniEt": EniEt,
    "Faderan": Faderan,
    "Imdril": Imdril,
    "Kjasjavikalimm": Kjasjavikalimm,
    "KtZrKtRtl": KtZrKtRtl,
    "Unity": Unity,
    "Yengii": Yengii,
    "Zeth": Zeth,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("undesirable_limit", type=int)
    # TODO: Add num_fleets param
    parser.add_argument(
        "-s",
        "--species_in_play",
        nargs="+",
        default=ALL_SPECIES.keys(),
    )
    args = parser.parse_args()

    all_cards = sidcon.parse.all_cards()

    cards_by_faction = get_cards_by_faction(all_cards, args)

    overall_converter_by_faction: dict[type[Faction], Converter] = dict()
    for faction, cards in cards_by_faction.items():
        features = list(itertools.chain.from_iterable(c.front.features for c in cards))
        converters = [f for f in features if isinstance(f, Converter)]
        converter = functools.reduce(Converter.merged, converters)
        overall_converter_by_faction[faction] = converter

    for faction, converter in overall_converter_by_faction.items():
        print(
            f"{faction.faction_name}: {overall_converter_by_faction[faction].max_input_value} -> "
            f"{overall_converter_by_faction[faction].output_value}"
        )


def get_cards_by_faction(
    all_cards: Sequence[Card | KtDualCard],
    args: argparse.Namespace,
) -> dict[type[Faction], list[StartingCard | UndesirableCard | KtDualCard]]:
    cards_by_faction: defaultdict[
        type[Faction], list[StartingCard | UndesirableCard | KtDualCard]
    ] = defaultdict(list)

    starting_cards = [c for c in all_cards if isinstance(c, Starting)]
    for c in starting_cards:
        cards_by_faction[c.faction].append(c)

    used_undesirable_cards = get_used_undesirable_cards(all_cards, args)
    cards_by_faction[CharitySyndicate].extend(used_undesirable_cards)

    return cards_by_faction


def get_used_undesirable_cards(
    all_cards: Sequence[Card | KtDualCard],
    args: argparse.Namespace,
) -> list[UndesirableCard]:
    species_in_play = [v for k, v in ALL_SPECIES.items() if k in args.species_in_play]

    undesirable_cards = sorted(
        [c for c in all_cards if isinstance(c, UndesirableCard)],
        key=lambda c: c.front.converter.net_value,
        reverse=True,
    )
    used_undesirable_cards: list[UndesirableCard] = []
    for c in undesirable_cards:
        if len(used_undesirable_cards) >= args.undesirable_limit:
            break
        if c.species in species_in_play:
            used_undesirable_cards.append(c)
    return used_undesirable_cards


if __name__ == "__main__":
    main()
