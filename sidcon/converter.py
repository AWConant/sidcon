import dataclasses
import enum
import itertools
import logging
import typing as typ
from collections.abc import Mapping, Sequence

import abstractcp as acp

import sidcon.countedunits
import sidcon.exception
import sidcon.unit
from sidcon.countedunits import CountedUnits

logging.basicConfig()
logger = logging.getLogger(__name__)


_ALTERNATE_INPUT_OUTPUT_KEY = "/"

ConverterT = typ.TypeVar("ConverterT", bound="Converter")


Input = CountedUnits
Inputs = Input | Sequence[Input]


def inputs_from_string(s: str) -> Inputs:
    strings = s.split(_ALTERNATE_INPUT_OUTPUT_KEY)
    units: Inputs
    if len(strings) == 1:
        units = sidcon.countedunits.from_string(strings[0])
    else:
        units = [sidcon.countedunits.from_string(s) for s in strings]
    return units


def _merged_inputs(a: Inputs, b: Inputs) -> Inputs:
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return sidcon.countedunits.add(a, b)
    elif isinstance(a, Sequence) or isinstance(b, Sequence):
        if not isinstance(a, Sequence):
            a = [a]
        if not isinstance(b, Sequence):
            b = [b]
        return [sidcon.countedunits.add(inp_a, inp_b) for inp_a, inp_b in itertools.product(a, b)]
    else:
        raise ValueError(
            "unhandled inputs merge types:\n"
            f"            type(a) = {type(a)}, type(b) = {type(b)},\n"
            f"            a = {a}\n"
            f"            b = {b}"
        )


@typ.overload
def _inputs_value(inputs: CountedUnits) -> float:
    ...


@typ.overload
def _inputs_value(inputs: Sequence[Input]) -> list[float]:
    ...


def _inputs_value(inputs: Inputs) -> float | list[float]:
    if isinstance(inputs, Sequence):
        return [_input_value(inp) for inp in inputs]
    return _input_value(inputs)


def _input_value(inp: Input) -> float:
    return sidcon.countedunits.value(inp)


Output = typ.Union[CountedUnits, "UniqueOutput"]
Outputs = Output | Sequence[Output]


def outputs_from_string(s: str) -> Outputs:
    unique_output_error: ValueError
    try:
        return UniqueOutput(s)
    except ValueError as e:
        unique_output_error = e

    # Outputs are just Inputs if they aren't UniqueOutputs, so we can repurpose that function.
    inputs_error: KeyError
    try:
        return inputs_from_string(s)
    except KeyError as e:
        inputs_error = e

    raise OutputsParseError(s, unique_output_error, inputs_error)


def _merged_outputs(a: Outputs, b: Outputs) -> Outputs:
    if isinstance(a, Sequence) or isinstance(b, Sequence):
        if not isinstance(a, Sequence):
            a = [a]
        if not isinstance(b, Sequence):
            b = [b]
        return [_merged_output(outp_a, outp_b) for outp_a, outp_b in itertools.product(a, b)]
    else:
        return _merged_output(a, b)


def _merged_output(a: Output, b: Output) -> Output:
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return sidcon.countedunits.add(a, b)
    else:
        raise ValueError(
            "unhandled output merge types:\n"
            f"            type(a) = {type(a)}, type(b) = {type(b)},\n"
            f"            a = {a}\n"
            f"            b = {b}"
        )


@typ.overload
def _outputs_value(outputs: CountedUnits) -> float:
    ...


@typ.overload
def _outputs_value(outputs: Sequence[Output]) -> list[float]:
    ...


def _outputs_value(outputs: Outputs) -> float | list[float]:
    if isinstance(outputs, Sequence):
        return [_output_value(o) for o in outputs]
    return _output_value(outputs)


def _output_value(o: Output) -> float:
    if isinstance(o, UniqueOutput):
        return 0.0
    return sidcon.countedunits.value(o)


@typ.final
class OutputsParseError(Exception):
    s: typ.Final[str]
    unique_output_error: typ.Final[ValueError]
    inputs_error: typ.Final[KeyError]

    def __init__(
        self,
        s: str,
        unique_output_error: ValueError,
        inputs_error: KeyError,
    ) -> None:
        self.s = s
        self.unique_output_error = unique_output_error
        self.inputs_error = inputs_error
        super().__init__(f"couldn't parse Outputs from string '{s}'")

    def __str__(self):
        return "\n".join(
            [
                f"{super().__str__()}\n",
                "Unique converter output parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.unique_output_error)}\n",
                "Inputs parse attempt traceback:",
                f"{sidcon.exception.format_tb(self.inputs_error)}\n",
            ]
        )


@dataclasses.dataclass(frozen=True)
class Converter(acp.Abstract):
    key: typ.ClassVar[str] = acp.abstract_class_property(str)

    inputs: Inputs
    "The input or inputs to the Converter. A list indicates an option of multiple inputs."

    outputs: Outputs
    "The output or outputs of the Converter. A list indicates an option of multiple outputs."

    @property
    def net_value(self) -> float:
        return self.output_value - self.input_value

    @property
    def min_net_value(self) -> float:
        return self.min_output_value - self.max_input_value

    @property
    def max_net_value(self) -> float:
        return self.max_output_value - self.min_input_value

    @property
    def input_value(self) -> float:
        if isinstance(self.inputs, Sequence):
            raise ValueError("converter with multiple inputs has no unambiguous input value")
        return self.min_input_value

    @property
    def min_input_value(self) -> float:
        if isinstance(self.inputs, Sequence):
            return min(_inputs_value(self.inputs))
        else:
            return _input_value(self.inputs)

    @property
    def max_input_value(self) -> float:
        if isinstance(self.inputs, Sequence):
            return max(_inputs_value(self.inputs))
        else:
            return _input_value(self.inputs)

    @property
    def output_value(self) -> float:
        if isinstance(self.outputs, Sequence):
            raise ValueError("converter with multiple outputs has no unambiguous output value")
        return self.min_output_value

    @property
    def min_output_value(self) -> float:
        if isinstance(self.outputs, Sequence):
            return min(_outputs_value(self.outputs))
        else:
            return _output_value(self.outputs)

    @property
    def max_output_value(self) -> float:
        if isinstance(self.outputs, Sequence):
            return max(_outputs_value(self.outputs))
        else:
            return _output_value(self.outputs)

    @classmethod
    def from_string_with_unknown_key(cls: type[ConverterT], s: str) -> ConverterT:
        for converter_type in cls.__subclasses__():
            try:
                return converter_type.from_string(s)
            except NoMatchingArrow:
                pass
        raise ValueError(f"couldn't parse string '{s}' as a converter")

    @classmethod
    def from_string(cls: type[ConverterT], s: str) -> ConverterT:
        if cls.key not in s:
            raise NoMatchingArrow(s, cls.key)
        input_string, output_string = s.split(cls.key)
        inputs = inputs_from_string(input_string)
        outputs = outputs_from_string(output_string)
        return cls(inputs=inputs, outputs=outputs)

    @classmethod
    def from_counted_units(cls: type[ConverterT], cg: CountedUnits) -> ConverterT:
        return cls(inputs={}, outputs=cg)

    @classmethod
    def merged(cls: type[ConverterT], a: ConverterT, b: ConverterT) -> ConverterT:
        return cls(
            inputs=_merged_inputs(a.inputs, b.inputs),
            outputs=_merged_outputs(a.outputs, b.outputs),
        )


@typ.final
@dataclasses.dataclass(frozen=True)
class WhiteConverter(Converter):
    key = "➪"


@typ.final
@dataclasses.dataclass(frozen=True)
class PurpleConverter(Converter):
    key = "→"


@typ.final
@dataclasses.dataclass(frozen=True)
class RedConverter(Converter):
    key = "➾"


@typ.final
class NoMatchingArrow(Exception):
    s: typ.Final[str]
    arrow: typ.Final[str]
    message: typ.Final[str]

    def __init__(self, s: str, arrow: str) -> None:
        self.s = s
        self.arrow = arrow
        self.message = f"unable to find required '{arrow}' in string '{s}'"
        super().__init__(self.message)


@typ.final
@enum.unique
class UniqueOutput(enum.Enum):
    DOUBLE_OUTPUT_THEN_DISCARD = "double output; then discard"
