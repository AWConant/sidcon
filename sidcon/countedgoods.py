from collections.abc import Mapping, MutableMapping

import sidcon.goods
from sidcon.goods import Good, ValuableGood

# All goods after _DONATION_KEY in a string are donation goods.
_DONATION_KEY = "+"
_STRIPPED_SUBSTRINGS = [" §"]


CountedGoods = Mapping[type[Good], int]
MutableCountedGoods = MutableMapping[type[Good], int]


def value(goods: CountedGoods) -> float:
    total = 0.0
    for good_type, count in goods.items():
        if issubclass(good_type, ValuableGood):
            total += count * good_type.value
    return total


def from_string(s: str) -> CountedGoods:
    for ss in _STRIPPED_SUBSTRINGS:
        s = s.replace(ss, "")

    goods_strings = s.split(_DONATION_KEY)
    if len(goods_strings) > 2:
        raise ValueError(
            f"encountered more than one donation flag ({_DONATION_KEY}) in string '{s}'",
        )

    non_donation_string = goods_strings[0]
    counted_goods = _from_string(non_donation_string, sidcon.goods.key_to_non_donation_good)
    if len(goods_strings) == 2:
        donation_string = goods_strings[1]
        counted_donation_goods = _from_string(donation_string, sidcon.goods.key_to_donation_good)
        counted_goods = add(counted_goods, counted_donation_goods)

    return counted_goods


def _from_string(s: str, key_map: Mapping[str, type[Good]]) -> CountedGoods:
    for key in s:
        if not key.isdigit() and key not in key_map:
            raise ValueError(f"input string '{s}' contains unmapped key '{key}'")

    d: MutableCountedGoods = dict()

    good: type[Good] | None = None
    digits: list[str] = []
    for i, key in enumerate(s):
        if key.isdigit():
            digits.append(key)
        else:
            good = key_map[key]

        # If it's the end of the string or the next key is not a digit, then we need to flush
        # the current good count.
        if i == len(s) - 1 or not s[i + 1].isdigit():
            if good is None:
                raise ValueError(
                    f"input string '{s}' contains either only numerals or a leading numeral"
                )
            if digits:
                to_add = int("".join(digits))
            else:
                to_add = 1
            d[good] = d.setdefault(good, 0) + to_add

    return d


def add(a: CountedGoods, b: CountedGoods) -> CountedGoods:
    summ: MutableCountedGoods = dict()
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


def subtract(left: CountedGoods, right: CountedGoods) -> CountedGoods:
    difference: MutableCountedGoods = dict(left)
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
            raise ValueError("CountedGoods subtraction resulted in negative count for key '{k}'")
    return {k: v for k, v in difference.items() if v != 0}
