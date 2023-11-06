from collections.abc import Mapping, MutableMapping

import sidcon.units
from sidcon.units import Unit, ValuableUnit

# All units after _DONATION_KEY in a string are donation units.
_DONATION_KEY = "+"
_STRIPPED_SUBSTRINGS = [" §"]


CountedUnits = Mapping[type[Unit], int]

# TODO: Unexport this if possible.
MutableCountedUnits = MutableMapping[type[Unit], int]


def value(units: CountedUnits) -> float:
    total = 0.0
    for unit_type, count in units.items():
        if issubclass(unit_type, ValuableUnit):
            total += count * unit_type.value
    return total


def from_string(s: str) -> CountedUnits:
    for ss in _STRIPPED_SUBSTRINGS:
        s = s.replace(ss, "")

    units_strings = s.split(_DONATION_KEY)
    if len(units_strings) > 2:
        raise ValueError(
            f"encountered more than one donation flag ({_DONATION_KEY}) in string '{s}'",
        )

    non_donation_string = units_strings[0]
    counted_units = _from_string(non_donation_string, sidcon.units.key_to_non_donation_unit)
    if len(units_strings) == 2:
        donation_string = units_strings[1]
        counted_donation_units = _from_string(donation_string, sidcon.units.key_to_donation_unit)
        counted_units = add(counted_units, counted_donation_units)

    return counted_units


def _from_string(s: str, key_map: Mapping[str, type[Unit]]) -> CountedUnits:
    for key in s:
        if not key.isdigit() and key not in key_map:
            raise ValueError(f"input string '{s}' contains unmapped key '{key}'")

    d: MutableCountedUnits = dict()

    unit: type[Unit] | None = None
    digits: list[str] = []
    for i, key in enumerate(s):
        if key.isdigit():
            digits.append(key)
        else:
            unit = key_map[key]

        # If it's the end of the string or the next key is not a digit, then we need to flush
        # the current unit count.
        if i == len(s) - 1 or not s[i + 1].isdigit():
            if unit is None:
                raise ValueError(
                    f"input string '{s}' contains either only numerals or a leading numeral"
                )
            if digits:
                to_add = int("".join(digits))
            else:
                to_add = 1
            d[unit] = d.setdefault(unit, 0) + to_add

    return d


def add(a: CountedUnits, b: CountedUnits) -> CountedUnits:
    summ: MutableCountedUnits = dict()
    for k, v in a.items():
        try:
            summ[k] += v
        except KeyError:
            summ[k] = v
    for k, v in b.items():
        try:
            summ[k] += v
        except KeyError:
            summ[k] = v
    return summ


def subtract(left: CountedUnits, right: CountedUnits) -> CountedUnits:
    difference: MutableCountedUnits = dict(left)
    for k, v in right.items():
        try:
            difference[k] -= v
        except KeyError:
            raise ValueError(
                "cannot subtract right from left because "
                f"it contains a key that the left lacks: {k}"
            )
    for k, v in difference.items():
        if v < 0:
            raise ValueError("CountedUnits subtraction resulted in negative count for key '{k}'")
    return {k: v for k, v in difference.items() if v != 0}
