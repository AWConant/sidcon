import collections
import csv
import logging
import pprint

from sidcon.alien import Kjasjavikalimm
from sidcon.card import (
    Card,
    CreatedCard,
    DualFacedColonyCard,
    KtColonyCard,
    KtDualCard,
    ProjectCard,
    Source,
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
    "Expansive Social",
    "Diffusion",
    "Hand Crafted",
    "Polyutility Components",
    "Anarchic Sacrificial",
    "High-Risk Laboratories",
    "Vast Distance",
    "Bending Engines",
    "Diverse",
    "Interspecies Housing",
    "Alien Cultural",
    "Inspiration",
    #
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


def validate_tech_cards():
    cards = [c for c in all_cards() if isinstance(c, TechnologyCard)]

    fronts = [c.front for c in cards]
    assert all(len(f.features) == 1 for f in fronts)
    assert len(set([f.name for f in fronts])) == 21

    fronts_by_name = collections.defaultdict(list)
    for front in fronts:
        fronts_by_name[front.name].append(front)

    for front_name, like_fronts in fronts_by_name.items():
        assert len(set([f.input_value for f in like_fronts])) == 1
        upgrade_pairs = [
            tuple(sorted(f.upgrades[0][0], key=lambda t: str(t))) for f in like_fronts
        ]
        assert len(set(upgrade_pairs)) == 1

    backs = [c.back for c in cards]
    assert all(len(f.features) == 1 for f in backs)

    back_names = set([f.name for f in backs])
    assert len(back_names) == 22
    # Imdril has Galactic Reunion instead of Galactic Colonization........

    backs_by_name = collections.defaultdict(list)
    for back in backs:
        backs_by_name[back.name].append(back)

    # Some of the unity upgrades produce the same output value as others, but most do not.
    unity_same_back_names = [
        "Multispecies Hybrid Cultures",
        "Full Interspecies Integration",
        "Living Infrastructure",
        "Galactic Domination",
        "Stasis Field",
        "Macroscale Teleportation",
        "Dyson Swarms",
        "Galactic Colonization",
    ]

    for back_name, like_backs in backs_by_name.items():
        # Imdril has Galactic Reunion instead of Galactic Colonization........
        if back_name == "Galactic Reunion":
            back_name = "Galactic Colonization"
        unique_output_values = set([f.output_value for f in like_backs])
        if back_name in unity_same_back_names:
            assert len(unique_output_values) == 1
        else:
            assert len(unique_output_values) == 2
            output1, output2 = unique_output_values
            assert abs(output1 - output2) == 0.5


def pprint_species_cards(species):
    cards = all_cards()
    cards = [card for card in cards if hasattr(card, "species") and card.species == species]

    starting_cards = [c for c in cards if isinstance(c, StartingCard)]
    tech_cards = sorted([c for c in cards if isinstance(c, TechnologyCard)], key=lambda c: c.era.value)
    other_cards = [
        c for c in cards if not isinstance(c, TechnologyCard) and not isinstance(c, StartingCard)
    ]

    print("############## STARTING CARDS ##############")
    pprint.pprint(starting_cards)
    print()
    print()
    # print("############## TECH CARDS ##############")
    # pprint.pprint(tech_cards)
    # print()
    # print()
    print("############## OTHER CARDS ##############")
    pprint.pprint(other_cards)
    print()
    print()


if __name__ == "__main__":
    validate_tech_cards()
    pprint_species_cards(Kjasjavikalimm)
    _ = all_cards()
