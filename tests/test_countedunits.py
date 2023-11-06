import pytest

import sidcon.countedunits
from sidcon.unit import Green, Ultratech, Blue


class TestAdd(object):
    def test_basic(self):
        a = {Green: 1, Ultratech: 2}
        b = {Green: 2}
        want = {Green: 3, Ultratech: 2}
        got = sidcon.countedunits.add(a, b)
        assert got == want


class TestSubtract(object):
    @pytest.mark.parametrize(
        "left,right,want",
        [
            pytest.param(
                {Green: 2, Ultratech: 2}, {Green: 1}, {Green: 1, Ultratech: 2}, id="basic"
            ),
            pytest.param(
                {Green: 2, Ultratech: 2}, {Green: 2}, {Ultratech: 2}, id="zeroes_are_removed"
            ),
        ],
    )
    def test_basic(self, left, right, want):
        got = sidcon.countedunits.subtract(left, right)
        assert got == want

    @pytest.mark.parametrize(
        "left,right",
        [
            pytest.param(
                {Green: 2, Ultratech: 2},
                {Blue: 1},
                id="missing_key_from_minuend",
            ),
            pytest.param(
                {Green: 2, Ultratech: 2},
                {Green: 3},
                id="negative_result",
            ),
        ],
    )
    def test_raises_ValueError(self, left, right):
        with pytest.raises(ValueError):
            _ = sidcon.countedunits.subtract(left, right)
