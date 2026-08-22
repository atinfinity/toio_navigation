#!/usr/bin/env python3
# Copyright (C) 2025 atinfinity
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Draw the spiral maps (issue #24).

Corridors are 18 cells (9 cm) wide so that 6 cm stay passable after the
inflation layer's inscribed band (3 cells on each side), and the inner wall
is 6 cells (3 cm) thick so that the U-turn around its tip is wide and the two
legs of the turn sit 0.11 m apart, beyond the 0.1 m RPP lookahead. The A4 mat
(40 rows) only fits one wall: top corridor 18, wall 6, pocket 14, plus the
border. The A3 mat (60 rows) fits the full spiral: 18, 6, 14, 6, 14.

Run from the maps directory: python3 make_spiral_maps.py
"""

import numpy as np
from PIL import Image

CORRIDOR = 18  # cells
WALL = 6  # cells
POCKET = 14  # cells


def blank(width, height):
    a = np.full((height, width), 255, np.uint8)
    a[0, :] = a[-1, :] = a[:, 0] = a[:, -1] = 0
    return a


def a4():
    """Draw the A4 hook: top corridor -> right corridor -> pocket under the wall."""
    w, h = 60, 40
    a = blank(w, h)
    r = 1 + CORRIDOR
    a[r:r + WALL, 0:w - 1 - CORRIDOR] = 0
    return a


def a3():
    """Draw the A3 spiral: top corridor -> right -> bottom -> left gap -> pocket."""
    w, h = 84, 60
    a = blank(w, h)
    r = 1 + CORRIDOR
    a[r:r + WALL, 0:w - 1 - CORRIDOR] = 0
    r = r + WALL + POCKET
    a[r:r + WALL, 1 + CORRIDOR:w - 1 - CORRIDOR] = 0
    return a


if __name__ == '__main__':
    Image.fromarray(a4()).save('toio_a4_map_spiral.png')
    Image.fromarray(a3()).save('toio_a3_map_spiral.png')
