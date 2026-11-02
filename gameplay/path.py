from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


# Normalized control points for the winding road (x_pct, y_pct)
DEFAULT_CONTROL_POINTS_PCT: List[Tuple[float, float]] = [
    (-0.02, 0.30),
    (0.10, 0.30),
    (0.22, 0.30),
    (0.24, 0.52),
    (0.25, 0.74),
    (0.39, 0.75),
    (0.53, 0.74),
    (0.55, 0.48),
    (0.57, 0.25),
    (0.68, 0.25),
    (0.75, 0.45),
    (0.78, 0.62),
    (0.85, 0.54),
    (0.91, 0.52),
]

# 10 Strategic Build Slots (Kingdom Rush style) placed in bends & chokepoints
DEFAULT_SLOTS_PCT: List[Tuple[float, float]] = [
    (0.14, 0.44),  # 0: Inner bend 1 (West)
    (0.33, 0.36),  # 1: Outer bend 1 (North-West)
    (0.15, 0.70),  # 2: South-West flank
    (0.38, 0.60),  # 3: Central Valley pocket (prime AoE / Frost spot)
    (0.41, 0.87),  # 4: Southern Riverbank
    (0.46, 0.24),  # 5: Northern Ridge west
    (0.64, 0.64),  # 6: Eastern Bridge overlook
    (0.66, 0.40),  # 7: Heart of the North-East bend
    (0.81, 0.35),  # 8: Royal Gate North bastion
    (0.78, 0.77),  # 9: Royal Gate South bastion
]


def _catmull_rom(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    t: float,
) -> Tuple[float, float]:
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * (
        (2.0 * p1[0])
        + (-p0[0] + p2[0]) * t
        + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
        + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
    )
    y = 0.5 * (
        (2.0 * p1[1])
        + (-p0[1] + p2[1]) * t
        + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
        + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
    )
    return (x, y)


@dataclass
class BuildSlot:
    index: int
    pos: Tuple[int, int]
    pct: Tuple[float, float]
    tower: Optional[ object ] = None


class RoadPath:
    """Represents the smoothed Catmull-Rom spline path and tactical build slots."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.waypoints: List[Tuple[float, float]] = []
        self.segment_lengths: List[float] = []
        self.cumulative_lengths: List[float] = []
        self.total_length: float = 0.0
        self.slots: List[BuildSlot] = []
        self.castle_pos: Tuple[int, int] = (int(width * 0.92), int(height * 0.48))
        self.rebuild(width, height)

    def rebuild(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        pts = [(px * width, py * height) for px, py in DEFAULT_CONTROL_POINTS_PCT]
        # Duplicate endpoints for Catmull-Rom
        ext = [pts[0]] + pts + [pts[-1]]
        sampled: List[Tuple[float, float]] = []
        steps_per_seg = 14
        for i in range(len(ext) - 3):
            p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
            for s in range(steps_per_seg):
                t = s / float(steps_per_seg)
                sampled.append(_catmull_rom(p0, p1, p2, p3, t))
        sampled.append(pts[-1])

        self.waypoints = sampled
        self.segment_lengths = []
        self.cumulative_lengths = [0.0]
        total = 0.0
        for i in range(len(sampled) - 1):
            dx = sampled[i + 1][0] - sampled[i][0]
            dy = sampled[i + 1][1] - sampled[i][1]
            seg_len = math.hypot(dx, dy)
            self.segment_lengths.append(seg_len)
            total += seg_len
            self.cumulative_lengths.append(total)
        self.total_length = max(1.0, total)
        self.castle_pos = (int(width * 0.92), int(height * 0.48))

        # Preserve existing towers if resizing
        old_towers = {sl.index: sl.tower for sl in self.slots} if self.slots else {}
        self.slots = []
        for idx, (sx, sy) in enumerate(DEFAULT_SLOTS_PCT):
            px, py = int(sx * width), int(sy * height)
            tw = old_towers.get(idx)
            if tw is not None and hasattr(tw, "pos"):
                tw.pos = (px, py)
            self.slots.append(BuildSlot(index=idx, pos=(px, py), pct=(sx, sy), tower=tw))

    def get_point_at_distance(self, dist: float) -> Tuple[float, float, float]:
        """Returns (x, y, angle_deg) along the path at given distance from start."""
        if not self.waypoints:
            return (0.0, 0.0, 0.0)
        if dist <= 0.0:
            p0, p1 = self.waypoints[0], self.waypoints[min(1, len(self.waypoints) - 1)]
            ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            return (p0[0], p0[1], ang)
        if dist >= self.total_length:
            p0, p1 = self.waypoints[-2], self.waypoints[-1]
            ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            return (p1[0], p1[1], ang)

        # Binary search in cumulative_lengths
        lo, hi = 0, len(self.segment_lengths) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.cumulative_lengths[mid + 1] < dist:
                lo = mid + 1
            elif self.cumulative_lengths[mid] > dist:
                hi = mid - 1
            else:
                lo = mid
                break
        seg_idx = max(0, min(len(self.segment_lengths) - 1, lo))
        seg_start_d = self.cumulative_lengths[seg_idx]
        seg_len = max(0.0001, self.segment_lengths[seg_idx])
        local_t = (dist - seg_start_d) / seg_len
        p0 = self.waypoints[seg_idx]
        p1 = self.waypoints[seg_idx + 1]
        x = p0[0] + (p1[0] - p0[0]) * local_t
        y = p0[1] + (p1[1] - p0[1]) * local_t
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        return (x, y, ang)

    def min_dist_to_path(self, x: float, y: float) -> float:
        best = float("inf")
        for wx, wy in self.waypoints[::2]:
            d = math.hypot(x - wx, y - wy)
            if d < best:
                best = d
        return best

