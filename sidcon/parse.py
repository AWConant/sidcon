import csv
import logging
import pprint

from sidcon.card import (
    Card,
    CreatedCard,
    DualFacedColonyCard,
    KtColonyCard,
    KtDualCard,
    ProjectCard,
    Source,
    Starting,
    StartingCard,
    StartingRaceCard,
    TechnologyCard,
    UndesirableCard,
)
from sidcon.row import Row

logging.basicConfig()
logger = logging.getLogger(__name__)


skipped_card_factions = [
    "Donation",
    "Confluence",  # TODO
    "Research",  # TODO
]

skipped_front_names = [
    "Incoming Donations",
    "Starting Race Card",
    "Phases",
    "Yengii License Idea Spindles",
    "Yengii License Hybrid FTL",
    "Kt' Technology Reference",
    "Undesirables Reference",
    "Grand Fleet 3",
    "Grand Fleet 1",
    "Starting Fleet Support, 2",
    # Buildable fleet support TODO
    "Fleet Support, 3",
    "Fleet Support, 1",
    "Fleet Support, 2",
    # Kt Research TODO
    "Retrocontinuity",
    "Stellar Harvesting",
    "Metauniversal Adapter",
    "Biohacking",
    "Planetary Rotogyro",
    "Ecology Inversion",
    "Coordinated Anarchy",
    "Leadership Timeshare",
    "Idea Spindles",
    "Hybrid FTL",
]


filenames = ["data/cards.csv", "data/bifurcation-cards.csv"]


def cards_from_filepath(filepath: str) -> list["Card | KtDualCard"]:
    cards = []
    with open(filepath) as csvfile:
        pp = pprint.PrettyPrinter(sort_dicts=False)
        dr = csv.DictReader(csvfile)
        for d in dr:
            r = Row.from_dict(d)
            if r.faction_title in skipped_card_factions:
                continue
            if r.front_name in skipped_front_names:
                continue
            try:
                source = Source.from_string(r.cost)
                card: Card
                if source == Source.CREATED:
                    if r.front_name in ProjectCard._all_front_names:
                        card = ProjectCard.from_row(r)
                    elif r.front_name in KtColonyCard._all_front_names:
                        card = KtColonyCard.from_row(r)
                    else:
                        card = CreatedCard.from_row(r)
                elif source == Source.RESEARCH:
                    card = TechnologyCard.from_row(r)
                elif source == Source.STARTING:
                    if r.front_name == StartingRaceCard.front_name:
                        card = StartingRaceCard.from_row(r)
                    else:
                        card = StartingCard.from_row(r)
                elif source == Source.UNDESIRABLE:
                    card = UndesirableCard.from_row(r)
                elif source == Source.BID:
                    # TODO: Implement research teams and colonies.
                    if r.faction_title == "Colonies":
                        card = DualFacedColonyCard.from_row(r)
                else:
                    pass
                cards.append(card)
                logger.info(f"Parsed card number {r.card_number}.\n")
            except Exception as e:
                logger.fatal(f"couldn't parse row dict:\n{pp.pformat(r)}\n")
                raise e
    return KtDualCard.coalesced_cards(cards)


def all_cards() -> list["Card | KtDualCard"]:
    cards = []
    for fname in filenames:
        cards.extend(cards_from_filepath(fname))
    return cards


if __name__ == "__main__":
    cards = all_cards()
    #starting_cards = list(filter(lambda c: isinstance(c, Starting), cards))
    #pprint.pprint(starting_cards)
    #print(len(starting_cards))
    pprint.pprint(cards)
    print(len(cards))
