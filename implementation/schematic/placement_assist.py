"""Pure deterministic AIXEM placement snap/alignment assistance.

The helper is advisory and read-only.  It never mutates .aixlayout.json or any
other authoritative source artifact.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import math
from typing import Any, Iterable, Mapping, Sequence


def _decimal(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be a finite number")
    return Decimal(str(value))


def _number(value: Decimal) -> int | float:
    integral = value.to_integral_value()
    return int(integral) if value == integral else float(value)


def snap_scalar(value: float, origin: float, grid: float) -> int | float:
    """Snap using explicit round-half-away-from-zero semantics."""
    v = _decimal(value, "value")
    o = _decimal(origin, "origin")
    g = _decimal(grid, "grid")
    if g <= 0:
        raise ValueError("grid must be greater than zero")
    units = (v - o) / g
    # Decimal ROUND_HALF_UP is away from zero for signed values.
    snapped_units = units.to_integral_value(rounding=ROUND_HALF_UP)
    return _number(o + snapped_units * g)


def snap_point(point: Sequence[float], origin: Sequence[float], grid: float) -> list[int | float]:
    if len(point) != 2 or len(origin) != 2:
        raise ValueError("point and origin must each contain exactly two coordinates")
    return [snap_scalar(point[0], origin[0], grid), snap_scalar(point[1], origin[1], grid)]


def _distance_squared(a: Sequence[float], b: Sequence[float]) -> Decimal:
    ax, ay = _decimal(a[0], "a.x"), _decimal(a[1], "a.y")
    bx, by = _decimal(b[0], "b.x"), _decimal(b[1], "b.y")
    return (ax - bx) ** 2 + (ay - by) ** 2


def _coord_key(point: Sequence[float]) -> tuple[Decimal, Decimal]:
    return (_decimal(point[0], "x"), _decimal(point[1], "y"))


def suggest_placement(
    proposed: Sequence[float],
    existing_origins: Iterable[Sequence[float]],
    *,
    grid: float = 2.5,
    pin_pitch: float = 5.0,
    major_grid: float = 10.0,
    origin: Sequence[float] = (0.0, 0.0),
) -> dict[str, Any]:
    """Return a bounded deterministic base/X/Y/XY candidate decision."""
    base = snap_point(proposed, origin, grid)
    g = _decimal(grid, "grid")
    if g <= 0:
        raise ValueError("grid must be greater than zero")
    legal_existing: list[tuple[Decimal, Decimal]] = []
    for item in existing_origins:
        if len(item) != 2:
            raise ValueError("each existing origin must contain exactly two coordinates")
        point = _coord_key(item)
        # Only legal existing origins may attract a candidate.
        if list(point) != [Decimal(str(value)) for value in snap_point(item, origin, grid)]:
            continue
        legal_existing.append(point)
    legal_existing = sorted(set(legal_existing))
    bx, by = _coord_key(base)
    x_refs = [point for point in legal_existing if abs(point[0] - bx) <= g]
    y_refs = [point for point in legal_existing if abs(point[1] - by) <= g]

    def best_x() -> tuple[Decimal, Decimal] | None:
        return min(x_refs, key=lambda point: (abs(point[0] - bx), abs(point[1] - by), point)) if x_refs else None

    def best_y() -> tuple[Decimal, Decimal] | None:
        return min(y_refs, key=lambda point: (abs(point[1] - by), abs(point[0] - bx), point)) if y_refs else None

    xr, yr = best_x(), best_y()
    raw_candidates: list[dict[str, Any]] = [{"point": [base[0], base[1]], "alignment": "none", "references": []}]
    if xr is not None:
        raw_candidates.append({"point": [_number(xr[0]), base[1]], "alignment": "x", "references": [[_number(xr[0]), _number(xr[1])]]})
    if yr is not None:
        raw_candidates.append({"point": [base[0], _number(yr[1])], "alignment": "y", "references": [[_number(yr[0]), _number(yr[1])]]})
    if xr is not None and yr is not None:
        refs = sorted({(xr[0], xr[1]), (yr[0], yr[1])})
        raw_candidates.append({
            "point": [_number(xr[0]), _number(yr[1])],
            "alignment": "xy",
            "references": [[_number(x), _number(y)] for x, y in refs],
        })

    rank = {"xy": 0, "x": 1, "y": 1, "none": 2}
    unique: dict[tuple[Decimal, Decimal], dict[str, Any]] = {}
    for candidate in raw_candidates:
        key = _coord_key(candidate["point"])
        current = unique.get(key)
        if current is None or rank[candidate["alignment"]] < rank[current["alignment"]]:
            unique[key] = candidate
    candidates = list(unique.values())
    candidates.sort(key=lambda candidate: (
        rank[candidate["alignment"]],
        _distance_squared(candidate["point"], base),
        _distance_squared(candidate["point"], proposed),
        _coord_key(candidate["point"]),
    ))
    selected = candidates[0]
    return {
        "input": {"coordinate": [proposed[0], proposed[1]]},
        "profile": {
            "grid": grid,
            "pinPitch": pin_pitch,
            "majorGrid": major_grid,
            "origin": [origin[0], origin[1]],
            "alignmentWindow": grid,
            "rounding": "half-away-from-zero",
        },
        "baseSnappedCoordinate": base,
        "selectedCoordinate": selected["point"],
        "alignment": selected["alignment"],
        "alignmentReferences": selected["references"],
        "candidateCount": len(candidates),
        "candidates": candidates,
        "warnings": [],
        "mutated": False,
        "authority": "derived-advisory-only",
    }


__all__ = ["snap_scalar", "snap_point", "suggest_placement"]
