import enum
import logging
import typing as typ

import abstractcp as acp

logging.basicConfig()
logger = logging.getLogger(__name__)


# TODO: make this an IntEnum, to support comparison natively.
@typ.final
@enum.unique
class Era(enum.Enum):
    I = 1  # noqa: E741
    II = 2
    III = 3
    IV = 4


class Technology(acp.Abstract):
    name: typ.ClassVar[str] = acp.abstract_class_property(str)

    @classmethod
    def from_string(cls, s: str) -> type["Technology"]:
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union(
                [s for c in cls.__subclasses__() for s in all_subclasses(c)]
            )

        for subclass in all_subclasses(cls):
            if acp.Abstract not in subclass.__bases__ and subclass.name == s:
                return subclass
        raise ValueError(f"couldn't parse Technology from string '{s}'")

    @classmethod
    def multiple_from_string(cls, string_with_commas: str) -> list[type["Technology"]]:
        ss = string_with_commas.split(",")
        return [cls.from_string(s) for s in ss]


class DonationTechnology(Technology, acp.Abstract):
    ...


class Era1Technology(Technology, acp.Abstract):
    ...


class Era2Technology(Technology, acp.Abstract):
    ...


class Era3Technology(Technology, acp.Abstract):
    ...


class Nanotechnology(Era1Technology):
    name = "Nanotechnology"


@typ.final
class DonationNanotechnology(DonationTechnology, Era1Technology):
    name = "+Nanotechnology"


class GeneticEngineering(Era1Technology):
    name = "Genetic Engineering"


@typ.final
class DonationGeneticEngineering(DonationTechnology, Era1Technology):
    name = "+Genetic Engineering"


class AtomicTransmutation(Era1Technology):
    name = "Atomic Transmutation"


@typ.final
class DonationAtomicTransmutation(DonationTechnology, Era1Technology):
    name = "+Atomic Transmutation"


class ClinicalImmortality(Era1Technology):
    name = "Clinical Immortality"


@typ.final
class DonationClinicalImmortality(DonationTechnology, Era1Technology):
    name = "+Clinical Immortality"


class UbiquitousCulturalRepository(Era1Technology):
    name = "Ubiquitous Cultural Repository"


@typ.final
class DonationUbiquitousCulturalRepository(DonationTechnology, Era1Technology):
    name = "+Ubiquitous Cultural Repository"


class QuantumComputers(Era1Technology):
    name = "Quantum Computers"


@typ.final
class DonationQuantumComputers(DonationTechnology, Era1Technology):
    name = "+Quantum Computers"


class UniversalTranslator(Era1Technology):
    name = "Universal Translator"


@typ.final
class DonationUniversalTranslator(DonationTechnology, Era1Technology):
    name = "+Universal Translator"


class HyperspaceMining(Era2Technology):
    name = "Hyperspace Mining"


@typ.final
class DonationHyperspaceMining(DonationTechnology, Era2Technology):
    name = "+Hyperspace Mining"


class SingularityControl(Era2Technology):
    name = "Singularity Control"


@typ.final
class DonationSingularityControl(DonationTechnology, Era2Technology):
    name = "+Singularity Control"


class AntimatterPower(Era2Technology):
    name = "Antimatter Power"


@typ.final
class DonationAntimatterPower(DonationTechnology, Era2Technology):
    name = "+Antimatter Power"


class AchronalAnalysis(Era2Technology):
    name = "Achronal Analysis"


@typ.final
class DonationAchronalAnalysis(DonationTechnology, Era2Technology):
    name = "+Achronal Analysis"


class OrganicConstruction(Era2Technology):
    name = "Organic Construction"


@typ.final
class DonationOrganicConstruction(DonationTechnology, Era2Technology):
    name = "+Organic Construction"


class CrossSpeciesEthicalEquality(Era2Technology):
    name = "Cross Species Ethical Equality"


@typ.final
class DonationCrossSpeciesEthicalEquality(DonationTechnology, Era2Technology):
    name = "+Cross Species Ethical Equality"


class InterspeciesMedicalExchange(Era2Technology):
    name = "Interspecies Medical Exchange"


@typ.final
class DonationInterspeciesMedicalExchange(DonationTechnology, Era2Technology):
    name = "+Interspecies Medical Exchange"


@typ.final
class SocialExodus(Era3Technology):
    name = "Social Exodus"


@typ.final
class GalacticTelecommControl(Era3Technology):
    name = "Galactic Telecomm Control"


@typ.final
class XenoCulturalExchange(Era3Technology):
    name = "Xeno Cultural Exchange"


@typ.final
class PolySpeciesCorporations(Era3Technology):
    name = "Poly Species Corporations"


@typ.final
class Megastructures(Era3Technology):
    name = "Megastructures"


@typ.final
class MatterGeneration(Era3Technology):
    name = "Matter Generation"


@typ.final
class TemporalDilation(Era3Technology):
    name = "Temporal Dilation"
