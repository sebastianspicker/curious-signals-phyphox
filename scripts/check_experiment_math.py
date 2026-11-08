#!/usr/bin/env python3
"""Exercise phyphox XML against independent numerical and processing-cycle fixtures.

This focused interpreter implements only the documented analysis modules used by
these fixtures; it is software evidence, not a replacement for importing files
in the Android and iOS apps. Module semantics follow the official file-format
reference and Android Analysis.java (inspected 2026-10-26).
"""

from __future__ import annotations

import argparse
import ast
import bisect
import math
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NAN = float("nan")


def ieee_divide(left: float, right: float) -> float:
    """Java double division, including nonfinite intermediate results."""
    if right != 0:
        return left / right
    if left == 0 or math.isnan(left):
        return NAN
    return math.copysign(math.inf, left * math.copysign(1.0, right))


def ieee_power(left: float, right: float) -> float:
    try:
        return math.pow(left, right)
    except ValueError:
        if left == 0 and right < 0:
            odd = math.isfinite(right) and right.is_integer() and int(right) % 2
            return math.copysign(math.inf, left) if odd else math.inf
        return NAN
    except OverflowError:
        odd = right.is_integer() and int(right) % 2
        return -math.inf if left < 0 and odd else math.inf


def ieee_remainder(left: float, right: float) -> float:
    try:
        return math.fmod(left, right)
    except ValueError:
        return NAN


def ieee_math(function, value: float) -> float:
    """Preserve Java Math domain/overflow values within a larger expression."""
    if function in (math.floor, math.ceil) and not math.isfinite(value):
        return value
    if function is math.log and value == 0:
        return -math.inf
    try:
        return float(function(value))
    except ValueError:
        return NAN
    except OverflowError:
        return math.inf


class NativeArithmetic(ast.NodeTransformer):
    """Use IEEE arithmetic without giving XML access to arbitrary Python."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        name = {ast.Div: "ieee_divide", ast.Pow: "ieee_power", ast.Mod: "ieee_remainder"}.get(
            type(node.op)
        )
        if name:
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id=name, ctx=ast.Load()),
                    args=[node.left, node.right],
                    keywords=[],
                ),
                node,
            )
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        return ast.copy_location(ast.Constant(value=float(node.value)), node)


class Experiment:
    """Small module runner for evaluating the checked-in analysis definitions."""

    def __init__(self, path: Path):
        self.root = ET.parse(path).getroot()
        # Explicit fixture time, never a wall-clock or sample-count surrogate.
        self.timer_time = 0.0
        self.buffers: dict[str, list[float]] = {}
        self.sizes: dict[str, int] = {}
        for item in self.root.findall("./data-containers/container"):
            name = (item.text or "").strip()
            self.sizes[name] = int(item.get("size", "1"))
            initial = item.get("init", "").split(",")
            self.buffers[name] = [float(v) for v in initial if v.strip()]
        for edit in self.root.findall("./views/view/edit"):
            output = edit.findtext("output")
            if output and not self.buffers[output]:
                self.buffers[output] = [float(edit.get("default", "0"))]

    def set(self, name: str, values: float | list[float]) -> None:
        if name not in self.buffers:
            raise ValueError(f"Unknown fixture buffer: {name}")
        self.buffers[name] = list(values) if isinstance(values, list) else [values]

    def last(self, name: str) -> float:
        """Latest value; NaN for an empty buffer, because phyphox shows neither as a value.

        A fixture that needs a produced value must assert on ``self.buffers[name]``.
        """
        values = self.buffers[name]
        return values[-1] if values else NAN

    def press(self, label: str) -> None:
        """Apply native button transfers between cycles; do not run analysis.

        Android ExpView.buttonElement replaces each destination and copies the
        entire source buffer, irrespective of the output's append attribute.
        Record buttons therefore capture singleton pending fields; the next
        analysis cycle appends them once. This deliberately does not emulate
        a more convenient last-value/append interpretation of the docs.
        """
        buttons = [
            item for item in self.root.findall("./views/view/button") if item.get("label") == label
        ]
        if len(buttons) != 1:
            raise ValueError(f"Expected one button labelled {label!r}")
        inputs = buttons[0].findall("input")
        outputs = buttons[0].findall("output")
        if len(inputs) != len(outputs):
            raise ValueError("Fixture buttons require paired inputs and outputs")
        for source, target in zip(inputs, outputs):
            # Native code clears the destination before reading this source.
            self.buffers[(target.text or "").strip()] = []
            self._write(target, self._read(source))

    def _read(self, item: ET.Element) -> list[float]:
        kind = item.get("type", "buffer")
        if kind == "empty":
            return []
        if kind == "value":
            return [float(item.text or "nan")]
        return list(self.buffers[(item.text or "").strip()])

    def _write(self, item: ET.Element, values: list[float]) -> None:
        name = (item.text or "").strip()
        if item.get("clear", "true") == "false" or item.get("append") == "true":
            values = self.buffers[name] + values
        size = self.sizes[name]
        self.buffers[name] = values[-size:] if size else values

    @staticmethod
    def _last(values: list[float], default: float = NAN) -> float:
        return values[-1] if values else default

    @staticmethod
    def _formula(expr: str, inputs: list[list[float]]) -> list[float]:
        referenced = [int(m.group(1)) - 1 for m in re.finditer(r"\[(\d+)_?\]", expr)]
        # Native Source.get throws on an empty scalar as well as an empty vector;
        # execute then stops emitting values. A spare constant input cannot fill it.
        if any(not inputs[i] for i in referenced):
            return []
        vector = [int(m.group(1)) - 1 for m in re.finditer(r"\[(\d+)_\]", expr)]
        length = min((len(inputs[i]) for i in vector), default=max(map(len, inputs), default=0))
        functions = {
            "sqrt": lambda x: ieee_math(math.sqrt, x),
            "floor": lambda x: ieee_math(math.floor, x),
            "ceil": lambda x: ieee_math(math.ceil, x),
            "abs": abs,
            "min": lambda a, b: NAN if math.isnan(a) or math.isnan(b) else min(a, b),
            "max": lambda a, b: NAN if math.isnan(a) or math.isnan(b) else max(a, b),
            "exp": lambda x: ieee_math(math.exp, x),
            "log": lambda x: ieee_math(math.log, x),
            "sin": lambda x: ieee_math(math.sin, x),
            "cos": lambda x: ieee_math(math.cos, x),
            "atan2": math.atan2,
            "sign": lambda x: NAN if math.isnan(x) else (x > 0) - (x < 0),
            "heaviside": lambda x: NAN if math.isnan(x) else float(x >= 0),
        }
        result = []
        for row in range(length):

            def substitute(match: re.Match) -> str:
                values = inputs[int(match.group(1)) - 1]
                index = row if match.group(2) else len(values) - 1
                value = values[index] if 0 <= index < len(values) else NAN
                return "(" + repr(value) + ")"

            code = re.sub(r"\[(\d+)(_)??\]", substitute, expr).replace("^", "**")
            # Accept arithmetic, named math functions and numeric literals only.
            # XML under review must not become unrestricted Python code.
            tree = ast.parse(code, mode="eval")
            allowed = (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Call,
                ast.Name,
                ast.Load,
                ast.Constant,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Pow,
                ast.Mod,
                ast.USub,
                ast.UAdd,
            )
            for part in ast.walk(tree):
                if not isinstance(part, allowed):
                    raise ValueError("Unsupported formula syntax")
                if isinstance(part, ast.Name) and part.id not in {*functions, "nan", "inf"}:
                    raise ValueError("Unknown formula name")
                if isinstance(part, ast.Call) and (
                    not isinstance(part.func, ast.Name)
                    or part.func.id not in functions
                    or part.keywords
                ):
                    raise ValueError("Unsupported formula call")
                if isinstance(part, ast.Constant) and type(part.value) not in (int, float):
                    raise ValueError("Formula constants must be numeric")
            tree = ast.fix_missing_locations(NativeArithmetic().visit(tree))
            try:
                value = eval(
                    compile(tree, "<phyphox-formula>", "eval"),
                    {
                        "__builtins__": {},
                        "nan": NAN,
                        "inf": math.inf,
                        "ieee_divide": ieee_divide,
                        "ieee_power": ieee_power,
                        "ieee_remainder": ieee_remainder,
                    },
                    functions,
                )
                result.append(float(value))
            except (ValueError, ZeroDivisionError, OverflowError):
                result.append(NAN)
        return result

    def run(self) -> None:
        for node in self.root.findall("./analysis/*"):
            if not isinstance(node.tag, str):
                continue
            source_nodes = node.findall("input")
            sources = [self._read(item) for item in source_nodes]
            outputs = node.findall("output")
            mapped = {item.get("as"): data for item, data in zip(source_nodes, sources)}
            for item in source_nodes:
                if (
                    item.get("type", "buffer") == "buffer"
                    and item.get("clear", "true") == "true"
                    and item.get("keep") != "true"
                ):
                    self.buffers[(item.text or "").strip()] = []
            result: list[list[float]]
            if node.tag == "formula":
                result = [self._formula(node.get("formula", ""), sources)]
            elif node.tag == "append":
                result = [[v for source in sources for v in source]]
            elif node.tag == "if":
                aa, bb = self._last(sources[0]), self._last(sources[1])
                condition = (
                    (node.get("equal") == "true" and aa == bb)
                    or (node.get("greater") == "true" and aa > bb)
                    or (node.get("less") == "true" and aa < bb)
                )
                branch = 2 if condition else 3
                if len(sources) <= branch:
                    continue
                result = [sources[branch]]
            elif node.tag == "count":
                result = [[float(len(sources[0]))]]
            elif node.tag in {"min", "max"}:
                ys = mapped.get("y", sources[0])
                xs = mapped.get("x", list(range(len(ys))))
                valid = [(x, y) for x, y in zip(xs, ys) if math.isfinite(y)]
                pair = (
                    (min if node.tag == "min" else max)(valid, key=lambda p: p[1])
                    if valid
                    else (NAN, NAN)
                )
                result = [
                    [pair[1] if item.get("as", node.tag) == node.tag else pair[0]]
                    for item in outputs
                ]
            elif node.tag == "threshold":
                ys = mapped["y"]
                xs = mapped.get("x", list(range(len(ys))))
                threshold = self._last(mapped.get("threshold", [0]))
                armed, found = False, NAN
                for xx, yy in zip(xs, ys):
                    crossed = yy < threshold if node.get("falling") == "true" else yy > threshold
                    if crossed and armed:
                        found = xx
                        break
                    if not crossed:
                        armed = True
                result = [[found]]
            elif node.tag == "rangefilter":
                arrays: list[list[float]] = []
                bounds: list[dict[str, float]] = []
                for item, values in zip(source_nodes, sources):
                    if item.get("as") in {"min", "max"}:
                        bounds[-1][item.get("as")] = self._last(values)
                    else:
                        arrays.append(values)
                        bounds.append({})
                result = [[] for _ in outputs]
                for row in range(max(map(len, arrays), default=0)):
                    values = [arr[row] if row < len(arr) else NAN for arr in arrays]
                    if any(
                        value < lim.get("min", -math.inf) or value > lim.get("max", math.inf)
                        for value, lim in zip(values, bounds)
                    ):
                        continue
                    for target, value in zip(result, values):
                        target.append(value)
            elif node.tag == "match":
                result = [[] for _ in outputs]
                for values in zip(*sources):
                    if all(math.isfinite(value) for value in values):
                        for target, value in zip(result, values):
                            target.append(value)
            elif node.tag == "average":
                values = [v for v in sources[0] if math.isfinite(v)]
                mean = sum(values) / len(values) if values else NAN
                sd = (
                    math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))
                    if len(values) > 1
                    else NAN
                )
                result = [[sd if item.get("as") == "stddev" else mean] for item in outputs]
            elif node.tag == "integrate":
                total = 0.0
                data = []
                for value in sources[0]:
                    total += value
                    data.append(total)
                result = [data]
            elif node.tag == "differentiate":
                values = sources[0]
                result = [[b - a for a, b in zip(values, values[1:])]]
            elif node.tag == "timer":
                if node.get("linearTime", "false") != "false" or any(
                    item.get("as", "out") != "out" for item in outputs
                ):
                    raise AssertionError("Fixture timer supports experiment time only")
                result = [[float(self.timer_time)] for _ in outputs]
            elif node.tag == "interpolate":
                xs, ys, xi = mapped["x"], mapped["y"], mapped["xi"]
                if node.get("method", "linear") != "previous":
                    raise AssertionError("Only previous interpolation is used in these fixtures")
                result = [
                    [ys[max(0, min(len(ys) - 1, bisect.bisect_right(xs, x) - 1))] for x in xi]
                    if xs and ys
                    else []
                ]
            elif node.tag in {"add", "subtract", "multiply", "divide", "power"}:
                expression = {
                    "add": "+",
                    "subtract": "-",
                    "multiply": "*",
                    "divide": "/",
                    "power": "^",
                }[node.tag]
                result = [
                    self._formula(
                        expression.join(
                            f"[{i + 1}]"
                            if source_nodes[i].get("type") == "value"
                            else f"[{i + 1}_]"
                            for i in range(len(sources))
                        ),
                        sources,
                    )
                ]
            else:
                raise AssertionError(f"Unsupported fixture module: {node.tag}")
            for item, data in zip(outputs, result):
                self._write(item, data)


def all_nan(values: list[float]) -> bool:
    """True only for a non-empty buffer of NaN; an empty buffer must not pass."""
    return len(values) > 0 and all(math.isnan(v) for v in values)


def all_close(actual: list[float], expected: list[float]) -> bool:
    return len(actual) == len(expected) and all(
        math.isclose(a, b) for a, b in zip(actual, expected)
    )


def reference_errors(root: ET.Element, name: str) -> list[str]:
    """Unique containers and export headings; every buffer reference is declared."""
    names = [n.text for n in root.findall("./data-containers/container")]
    errors = []
    if len(names) != len(set(names)):
        errors.append(f"{name}: duplicate data container")
    for section in ("input", "output", "analysis", "views", "export"):
        parent = root.find(section)
        if parent is None:
            continue
        for item in parent.iterfind(".//*"):
            if (
                item.tag in {"input", "output", "data"}
                and len(item) == 0
                and item.get("type", "buffer") == "buffer"
                and (item.text or "").strip() not in names
            ):
                errors.append(f"{name}: {section} references undeclared buffer {item.text!r}")
    for export in root.findall("./export/set"):
        headings = [n.get("name") for n in export.findall("data")]
        if len(headings) != len(set(headings)):
            errors.append(f"{name}: duplicate export heading in {export.get('name')!r}")
    return errors


def ingest_nano(exp: Experiment, payload: bytes, arrival: float) -> dict[str, float]:
    """Decode a float32 Nano packet using the checked-in XML offsets, keeping history."""
    decoded = {}
    for item in exp.root.findall("./input/bluetooth/output"):
        name = item.text.strip()
        if item.get("extra") == "time":
            value = arrival
        else:
            assert item.get("conversion") == "float32LittleEndian"
            value = struct.unpack_from("<f", payload, int(item.get("offset", "0")))[0]
        decoded[name] = value
        history = exp.buffers[name] + [value]
        size = exp.sizes[name]
        exp.set(name, history[-size:] if size else history)
    return decoded


def check(path: Path) -> None:
    for name in ["albedo", "transitmethode", "ir-dist_habitable", "owon_digital_multimeter-debug"]:
        root = ET.parse(path / (name + ".phyphox")).getroot()
        errors = reference_errors(root, name)
        assert not errors, errors
        assert {"de", "fr"} <= {n.get("locale") for n in root.findall("./translations/translation")}
        assert all(
            g.get("partialUpdate", "false") == "false" for g in root.findall("./views/view/graph")
        )
    # Relative reflectance is checked against a declared dark/reference pair.
    exp = Experiment(path / "albedo.phyphox")
    for prefix in ["phone", "st"]:
        exp.set(prefix + "_dark", 10)
        exp.set(prefix + "_reference", 110)
        exp.set(prefix + "_sample", 46.4)
        exp.set(prefix + "_use_means", 1)
    exp.run()
    assert math.isclose(exp.last("phone_ratio"), 0.364)
    assert math.isclose(exp.last("st_ratio"), 0.364)
    exp.set("phone_reference", 10)
    exp.run()
    assert math.isnan(exp.last("phone_ratio"))
    exp.set("phone_reference", 9)
    exp.run()
    assert math.isnan(exp.last("phone_ratio"))
    exp.set("phone_reference", 110)
    exp.set("phone_sample", 9)
    exp.run()
    assert math.isnan(exp.last("phone_ratio"))
    exp.set("RawInt", []) if "RawInt" in exp.buffers else None
    exp.set("st_RawInt", [100, 4196, 8292])
    exp.set("st_t", [0.2, 1, 3.4])
    exp.run()
    assert exp.buffers["st_amplitude"] == [1, 2, 4]
    assert exp.buffers["st_t"] == [0.2, 1, 3.4]
    # Source histories remain independent over repeated analysis cycles.
    exp = Experiment(path / "transitmethode.phyphox")
    exp.set("phone_t", [0, 1, 2])
    exp.set("phone_amplitude", [100, 95, 100])
    exp.set("st_t", [0.2, 2.7])
    exp.set("RawInt", [1000, 2000])
    exp.set("tin", [0.4, 1.4])
    exp.set("str", [1000, 1200])
    exp.set("dec", [1, 1])
    exp.set("unit", [0, 0])
    exp.set("18value", [1, 2])
    exp.set("18bitmask", [32, 32])
    for source, times, values in [
        (1, [0, 1, 2], [100, 95, 100]),
        (2, [0.2, 2.7], [10, 20]),
        (3, [0.4, 1.4], [1, 1.2]),
    ]:
        exp.set("source", source)
        for _ in range(3):
            exp.run()
            assert exp.buffers["t"] == times
            assert all_close(exp.buffers["amplitude"], values)
        assert exp.buffers["phone_t"] == [0, 1, 2]
    # Model selection never accepts a W18B interpretation for an invalid B35T code.
    for name in ["transitmethode", "owon_digital_multimeter-debug"]:
        exp = Experiment(path / (name + ".phyphox"))
        exp.set("tin", [0, 0.5, 2])
        exp.set("str", [1000, 1000, 1000])
        exp.set("dec", [1, 3, 1])
        exp.set("unit", [0, 0, 255])
        exp.set("18value", [0x03E8, 0x83E8, 0])
        exp.set("18bitmask", [32, 32, 32])
        exp.set("meter_model", 1)
        exp.run()
        assert exp.buffers["V"][0] == 1
        assert all(math.isnan(v) for v in exp.buffers["V"][1:])
        exp.set("meter_model", 2)
        exp.run()
        assert exp.buffers["V"] == [1000, -1000, 0]
        exp.set("meter_model", 3)
        exp.run()
        assert all(math.isnan(v) for v in exp.buffers["V"])
    # Known projected-radius geometry and invalid-depth bounds.
    exp = Experiment(path / "transitmethode.phyphox")
    for key, value in [
        ("baseline", 100),
        ("plateau", 96),
        ("dark", 0),
        ("use_means", 1),
        ("R_star", 1),
        ("distance_ratio", 0.5),
    ]:
        exp.set(key, value)
    exp.run()
    assert math.isclose(exp.last("R_planet"), 0.1)
    for baseline, plateau, dark in [(0, 0, 0), (10, 9, 11), (100, 101, 0), (100, -1, 0)]:
        exp.set("baseline", baseline)
        exp.set("plateau", plateau)
        exp.set("dark", dark)
        exp.run()
        assert math.isnan(exp.last("R_planet"))
    # Three complete events give means immediately; an initial partial dip and
    # a final unfinished dip contribute no duration and cannot replay old events.
    exp = Experiment(path / "transitmethode.phyphox")
    times = list(range(28))
    signal = [96 if t < 2 or 5 <= t < 8 or 14 <= t < 17 or 23 <= t < 26 else 100 for t in times]
    exp.set("phone_t", times)
    exp.set("phone_amplitude", signal)
    exp.set("baseline", 100)
    exp.run()
    assert exp.last("complete_count") == 3
    assert exp.last("avg_transit_time") == 3
    assert exp.last("avg_year_duration") == 9
    for i in range(3):
        assert exp.last(f"on{i}") == [5, 14, 23][i]
    assert math.isnan(exp.last("on3"))
    exp.set("phone_t", list(range(25)))
    exp.set("phone_amplitude", signal[:25])
    exp.run()
    assert exp.last("complete_count") == 2
    assert math.isnan(exp.last("off2"))
    assert math.isnan(exp.last("on3"))
    exp.set("threshold_high", 0.98)
    exp.run()
    assert exp.last("complete_count") == 0
    exp = Experiment(path / "transitmethode.phyphox")
    exp.set("phone_t", list(range(6)))
    exp.set("phone_amplitude", [96, 96, NAN, 96, 96, 100])
    exp.set("baseline", 100)
    exp.run()
    assert exp.last("complete_count") == 0
    # Signed IR conversion and asynchronous, sample-and-hold mouse positions.
    exp = Experiment(path / "ir-dist_habitable.phyphox")
    raw = [struct.unpack("<h", struct.pack("<H", word))[0] for word in [0xFF80, 0, 0x0C80]]
    exp.set("T_IR_raw", raw)
    exp.set("T_amb_raw", [0, 0, 0])
    exp.set("ir_t", [0.2, 0.8, 1.5])
    exp.set("mouse_t", [0, 0.5, 1])
    exp.set("dx", [0, 10, 10])
    exp.set("dy", [0, 0, 0])
    exp.set("distance_origin", 0.2)
    exp.set("distance_scale", 0.001)
    exp.run()
    assert exp.buffers["T_IRHist"] == [-1, 0, 25]
    assert exp.buffers["dHist"] == [0, 10, 20]
    assert all_close(exp.buffers["distance_m"], [0.2, 0.21, 0.22])
    for _ in range(5):
        exp.run()
        assert len(exp.buffers["T_IRHist"]) == 3
    exp.set("mouse_t", [0, 0.5, 1, 2])
    exp.set("dx", [0, 10, 10, 10])
    exp.set("dy", [0, 0, 0, 0])
    exp.run()
    assert exp.buffers["dHist"] == [0, 10, 20]
    assert len(exp.buffers["T_IRHist"]) == 3
    exp.set("distance_scale", 0)
    exp.run()
    assert all_nan(exp.buffers["distance_m"])
    print(
        "Optical XML references, model guards, source isolation, "
        "event timing, and IR cycle fixtures passed."
    )


def check_core(path: Path) -> None:
    """Known physical inputs, independent units and immutable original readings."""
    # Opposed static orientations after a measured additive bias; the raw
    # firmware magnitude is deliberately wrong, so copying it cannot pass.
    for stem, scale, suffix in [
        ("accelerometer", 9.80665, "norm"),
        ("gyroscope", math.pi / 180, "norm"),
        ("magnetometer", 1, "cal"),
    ]:
        exp = Experiment(path / f"{stem}_plot_v1-2.phyphox")
        exp.set("CH1", [0, 0.05, 0.1])
        exp.set("CH0", [0.1, 0.15, 0.2])
        raw = {
            "CH2": [1.1, -0.9, NAN],
            "CH3": [0.2, 0.2, NAN],
            "CH4": [0.3, 0.3, NAN],
            "CH5": [999, 999, NAN],
        }
        for name, values in raw.items():
            exp.set(name, values)
        for axis, bias in zip("xyz", [0.1, 0.2, 0.3]):
            exp.set("bias_" + axis, bias)
        exp.run()
        assert math.isclose(exp.buffers[f"CH2_{suffix}"][0], scale)
        assert math.isclose(exp.buffers[f"CH2_{suffix}"][1], -scale)
        assert all(math.isclose(x, scale) for x in exp.buffers[f"CH5_{suffix}"][:2])
        assert math.isnan(exp.last(f"CH5_{suffix}"))
        exp.set("gain_x", 2)
        exp.run()
        exp.run()
        assert len(exp.buffers[f"CH2_{suffix}"]) == 3
        assert math.isclose(exp.buffers[f"CH2_{suffix}"][0], 2 * scale)
        for name, values in raw.items():
            assert exp.buffers[name][:2] == values[:2]
            assert math.isnan(exp.last(name))
    exp = Experiment(path / "analog_input_plot_v1-2.phyphox")
    for channel in range(2, 5):
        exp.set(f"CH{channel}", [0, 512, 1023, NAN])
    exp.run()
    assert exp.buffers["CH2_norm"][0] == 0
    assert math.isclose(exp.buffers["CH2_norm"][2], 3300)
    exp.set("gain_A0", 2.5)
    exp.set("offset_A0", 12)
    exp.run()
    assert exp.buffers["CH2_norm"][:3] == [12, 1292, 2569.5]
    assert math.isnan(exp.last("CH2_norm"))
    assert exp.buffers["CH2"][:3] == [0, 512, 1023]
    exp = Experiment(path / "pressure_plot_v1-2.phyphox")
    exp.set("CH2", [100, 100.1, NAN])
    exp.set("pressure_bias", 0.25)
    exp.run()
    assert exp.buffers["pressure_change"] == []
    exp.set("pressure_reference", 999.75)
    exp.run()
    assert exp.buffers["CH2_norm"][:2] == [999.75, 1000.75]
    assert exp.buffers["pressure_change"][:2] == [0, 1]
    exp.set("pressure_reference", -1)
    exp.run()
    assert exp.buffers["pressure_change"] == []
    exp = Experiment(path / "temperature_plot_v1-2.phyphox")
    exp.set("CH2", [23, 24])
    exp.set("CH3", [50, 101])
    exp.set("temperature_bias", 0.5)
    exp.set("humidity_bias", -0.5)
    exp.run()
    assert exp.buffers["CH2_cal"] == [22.5, 23.5]
    assert exp.buffers["CH3_cal"] == [50.5, 101.5]  # No silent physical-range clipping.
    exp = Experiment(path / "light_plot_v1-2.phyphox")
    for channel in range(2, 6):
        exp.set(f"CH{channel}", [20, 4099, 4100, NAN])
    exp.set("dark_clear", 25)
    exp.run()
    assert exp.buffers["CH2_dark_corrected"][:3] == [-5, 4074, 4075]
    assert exp.buffers["nominal_clipping"][:3] == [0, 0, 1]
    assert math.isnan(exp.last("nominal_clipping"))
    # An unavailable channel cannot certify that the detector is below its ceiling.
    exp.set("CH3", [NAN, 4099, 4100, NAN])
    exp.run()
    assert math.isnan(exp.buffers["nominal_clipping"][0])
    print("Seven core calibration, units, missing-value and repeat-cycle fixtures passed.")


def check_thermal(path: Path) -> None:
    exp = Experiment(path / "greenhouse.phyphox")
    exp.set("tempRaw1", [2300, 2400, 2500])
    exp.set("tempRaw2", [2400, 2600])
    exp.set("baseline1", 23)
    exp.set("baseline2", 24)
    # Use the declared receive outputs so this also detects a lost/reused clock.
    for i, bt in enumerate(exp.root.findall("./input/bluetooth")):
        clock = next(x.text for x in bt.findall("output") if x.get("extra") == "time")
        exp.set(clock, [[0.2, 1.2, 4.2], [1.4, 5.4]][i])
    exp.run()
    exp.run()
    assert exp.buffers["t"] == [0.2 / 60, 1.2 / 60, 4.2 / 60]
    assert exp.buffers["t2"] == [1.4 / 60, 5.4 / 60]
    assert exp.buffers["tempCal1_rise"] == [0, 1, 2]
    assert exp.buffers["tempCal2_rise"] == [0, 2]
    exp = Experiment(path / "pt-star.phyphox")
    exp.set("tempRaw", [0, 2300])
    exp.run()
    assert exp.buffers["tempK"] == [273.15, 296.15]
    exp = Experiment(path / "missiontomars.phyphox")
    assert exp.root.find("./input/sensor").get("ignoreUnavailable") == "true"
    exp.set("st_pRaw", [100000, 100100])
    exp.set("st_t", [0.2, 5.2])
    exp.run()
    assert exp.buffers["st_t"] == [0.2, 5.2]
    assert exp.buffers["st_p"] == [1000, 1001]
    exp = Experiment(path / "tidal-locking.phyphox")
    for output in exp.root.findall("./input/bluetooth/output"):
        if output.text.startswith(("ambRaw", "objRaw")):
            assert output.get("conversion") == "int16LittleEndian"
            values = [-25, -1, -0.03125, 0, 0.03125, 25]
            signed = [
                struct.unpack("<h", struct.pack("<H", (round(t / 0.03125) << 2) & 0xFFFF))[0]
                for t in values
            ]
            exp.set(output.text, signed)
    exp.run()
    for name in ["ambCal1", "objCal1", "ambCal2", "objCal2"]:
        assert exp.buffers[name] == values
    clocks = {
        "tempCal1": "bmp_t1",
        "tempCal2": "bmp_t2",
        "ambCal1": "ir_t1",
        "objCal1": "ir_t1",
        "ambCal2": "ir_t2",
        "objCal2": "ir_t2",
        "amplitude1": "light_t1",
        "amplitude2": "light_t2",
    }
    for graph in exp.root.findall("./views/view/graph"):
        clock = None
        for item in graph.findall("input"):
            if item.get("axis") == "x":
                clock = item.text
            if item.get("axis") == "y":
                assert clock == clocks[item.text.removesuffix("_rise")]
    for experiment in path.glob("*.phyphox"):
        root = ET.parse(experiment).getroot()
        for dataset in root.findall("./export/set"):
            headings = [d.get("name") for d in dataset.findall("data")]
            assert len(headings) == len(set(headings)), (experiment.name, dataset.get("name"))
    print("Four thermal clock, baseline, signed-temperature and export fixtures passed.")


def main() -> None:
    if not __debug__:
        sys.exit("Fixture checks rely on assert; run without -O or PYTHONOPTIMIZE.")
    assert Experiment._formula("sqrt([1_]^2+[2_]^2)", [[-3, 4], [0]]) == [3]
    assert Experiment._formula("[1]+0*[2]", [[], [1]]) == []
    assert Experiment._formula("[1]", [[1, 2], [0]]) == [2, 2]
    assert Experiment._formula("[1_]/0", [[-1, 1]]) == [-math.inf, math.inf]
    assert Experiment._formula("1/([1_]/0)^2", [[-1]]) == [0]
    assert math.isnan(Experiment._formula("0/0", [[1]])[0])
    assert Experiment._formula("log([1_])", [[0]]) == [-math.inf]
    assert Experiment._formula("floor([1_])", [[math.inf]]) == [math.inf]
    for expression in ("min([1_],[2_])", "max([1_],[2_])"):
        assert math.isnan(Experiment._formula(expression, [[20], [NAN]])[0])
        assert math.isnan(Experiment._formula(expression, [[NAN], [20]])[0])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "experiments" / "astronomy",
    )
    args = parser.parse_args()
    check(args.directory)
    check_core(args.directory.parent)
    check_thermal(args.directory)


if __name__ == "__main__":
    main()
