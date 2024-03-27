# Copyright 2022 Pulser Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Special register layouts defined for convenience."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import pulser
import pulser.register._patterns as patterns
from pulser.json.utils import obj_to_dict
from pulser.register.register_layout import RegisterLayout

if TYPE_CHECKING:
    from pulser.register import Register

import numpy as np
from scipy.spatial.distance import cdist


class RectangularLatticeLayout(RegisterLayout):
    """A RegisterLayout with a rectangular lattice pattern in a rectangular
    shape.

    Args:
        rows: The number of rows of traps.
        columns: The number of columns of traps.
        x_spacing: Horizontal distance between neighbouring traps (in µm).
        y_spacing: Vertical distance between neighbouring traps (in µm)
    """

    def __init__(
        self, rows: int, columns: int, x_spacing: float, y_spacing: float
    ):
        """Initializes a RectangularLatticeLayout."""
        self._rows = int(rows)
        self._columns = int(columns)
        self._x_spacing = float(x_spacing)
        self._y_spacing = float(y_spacing)
        slug = (
            f"RectangularLatticeLayout(Shape : {self._rows}x{self._columns}, "
            f"Lattice pattern : {self._x_spacing}x{self._y_spacing}µm)"
        )
        self._traps = patterns.square_rect(self._rows, self._columns)
        self._traps[:, 0] = self._traps[:, 0] * self._x_spacing
        self._traps[:, 1] = self._traps[:, 1] * self._y_spacing
        super().__init__(
            trap_coordinates=self._traps,
            slug=slug,
        )

    def square_register(self, side: int, prefix: str = "q") -> Register:
        """Defines a register with a square shape.

        Args:
            side: The length of the square's side, in number of atoms.
            prefix: The prefix for the qubit ids. Each qubit ID starts
                with the prefix, followed by an int from 0 to N-1
                (e.g. prefix='q' -> IDs: 'q0', 'q1', 'q2', ...).

        Returns:
            The register instance created from this layout.
        """
        return self.rectangular_register(side, side, prefix=prefix)

    def rectangular_register(
        self,
        rows: int,
        columns: int,
        prefix: str = "q",
    ) -> Register:
        """Defines a register with a rectangular shape.

        Args:
            rows: The number of rows in the register.
            columns: The number of columns in the register.
            prefix: The prefix for the qubit ids. Each qubit ID starts
                with the prefix, followed by an int from 0 to N-1
                (e.g. prefix='q' -> IDs: 'q0', 'q1', 'q2', ...).

        Returns:
            The register instance created from this layout.
        """
        if rows > self._rows or columns > self._columns:
            raise ValueError(
                f"A '{rows}x{columns}' array doesn't fit a "
                f"{self._rows}x{self._columns} RectangularLatticeLayout."
            )
        points = patterns.square_rect(rows, columns)
        points[:, 0] = points[:, 0] * self._x_spacing
        points[:, 1] = points[:, 1] * self._y_spacing
        trap_ids = self.get_traps_from_coordinates(*points)
        qubit_ids = [f"{prefix}{i}" for i in range(len(trap_ids))]
        return cast(
            pulser.Register,
            self.define_register(*trap_ids, qubit_ids=qubit_ids),
        )

    def _to_dict(self) -> dict[str, Any]:
        return obj_to_dict(
            self, self._rows, self._columns, self._x_spacing, self._y_spacing
        )


class SquareLatticeLayout(RectangularLatticeLayout):
    """A RegisterLayout with a square lattice pattern in a rectangular shape.

    Args:
        rows: The number of rows of traps.
        columns: The number of columns of traps.
        spacing: The distance between neighbouring traps (in µm).
    """

    def __init__(self, rows: int, columns: int, spacing: float):
        """Initializes a SquareLatticeLayout."""
        self._rows = int(rows)
        self._columns = int(columns)
        self._spacing = float(spacing)
        super().__init__(
            self._rows, self._columns, self._spacing, self._spacing
        )

    def _to_dict(self) -> dict[str, Any]:
        return obj_to_dict(self, self._rows, self._columns, self._spacing)


class TriangularLatticeLayout(RegisterLayout):
    """A RegisterLayout with a triangular lattice pattern in a hexagonal shape.

    Args:
        n_traps: The number of traps in the layout.
        spacing: The distance between neighbouring traps (in µm).
    """

    def __init__(self, n_traps: int, spacing: float):
        """Initializes a TriangularLatticeLayout."""
        self._spacing = float(spacing)
        slug = f"TriangularLatticeLayout({int(n_traps)}, {self._spacing}µm)"
        super().__init__(
            patterns.triangular_hex(int(n_traps)) * self._spacing, slug=slug
        )

    def hexagonal_register(self, n_atoms: int, prefix: str = "q") -> Register:
        """Defines a register with an hexagonal shape.

        Args:
            n_atoms: The number of atoms in the register.
            prefix: The prefix for the qubit ids. Each qubit ID starts
                with the prefix, followed by an int from 0 to N-1
                (e.g. prefix='q' -> IDs: 'q0', 'q1', 'q2', ...).

        Returns:
            The register instance created from this layout.
        """
        if n_atoms > self.number_of_traps:
            raise ValueError(
                f"The desired register has more atoms ({n_atoms}) than there"
                " are traps in this TriangularLatticeLayout"
                f" ({self.number_of_traps})."
            )
        points = patterns.triangular_hex(n_atoms) * self._spacing
        trap_ids = self.get_traps_from_coordinates(*points)
        qubit_ids = [f"{prefix}{i}" for i in range(len(trap_ids))]
        return cast(
            pulser.Register,
            self.define_register(*trap_ids, qubit_ids=qubit_ids),
        )

    def rectangular_register(
        self, rows: int, atoms_per_row: int, prefix: str = "q"
    ) -> Register:
        """Defines a register with a rectangular shape.

        Args:
            rows: The number of rows in the register.
            atoms_per_row: The number of atoms in each row.
            prefix: The prefix for the qubit ids. Each qubit ID starts
                with the prefix, followed by an int from 0 to N-1
                (e.g. prefix='q' -> IDs: 'q0', 'q1', 'q2', ...).

        Returns:
            The register instance created from this layout.
        """
        if rows * atoms_per_row > self.number_of_traps:
            raise ValueError(
                f"A '{rows}x{atoms_per_row}' rectangular subset of a "
                "triangular lattice has more atoms than there are traps in "
                f"this TriangularLatticeLayout ({self.number_of_traps})."
            )
        points = patterns.triangular_rect(rows, atoms_per_row) * self._spacing
        trap_ids = self.get_traps_from_coordinates(*points)
        qubit_ids = [f"{prefix}{i}" for i in range(len(trap_ids))]
        return cast(
            pulser.Register,
            self.define_register(*trap_ids, qubit_ids=qubit_ids),
        )

    def _to_dict(self) -> dict[str, Any]:
        return obj_to_dict(self, self.number_of_traps, self._spacing)


class TriangularLatticeLayoutRectShape(RegisterLayout):
    """A RegisterLayout with a triangular lattice pattern in a rectangular
    shape.

    Args:
        n_traps: The number of traps in the layout.
        spacing: The distance between neighbouring traps (in µm).
    """

    def __init__(self, columns: int, rows: int, spacing: float = 5):
        """Initializes a TriangularLatticeLayout."""
        self._spacing = float(spacing)
        self._columns = int(columns)
        self._rows = int(rows)
        slug = (
            f"TriangularLatticeLayoutRectshape({self._rows}x{self._columns}, "
            f"{self._spacing}µm)"
        )
        super().__init__(
            patterns.triangular_rect(self._rows, self._columns)
            * self._spacing,
            slug=slug,
        )


class RandomLayout(RegisterLayout):
    """A RegisterLayout generated randomly.

    Args :
        n_traps : the number of traps in the layout
        radius : radius defining the working area
        min_dist : minimum distance between traps
        max_iter = maximum number of iterations to compute the random layout
    """

    def __init__(
        self,
        n_traps: int,
        radius: float = 35,
        min_spacing: float = 5,
        max_iter: int = 1000,
    ):
        """Initializes a random layout"""
        self._pts = []
        self._n_traps = int(n_traps)
        self._min_spacing = float(min_spacing)
        i = 0
        while len(self._pts) < n_traps and i < max_iter:
            pt_x = np.random.uniform(low=-radius, high=radius, size=1)
            pt_y = np.random.uniform(low=-radius, high=radius, size=1)
            pt = np.stack([pt_x, pt_y], axis=1)
            if not self._pts and pt_x**2 + pt_y**2 <= radius**2:
                self._pts.append(pt)
                continue
            if len(self._pts) == 0:
                continue
            dist = cdist(np.concatenate(self._pts), pt)
            if pt_x**2 + pt_y**2 <= radius**2 and np.all(
                dist > self._min_spacing
            ):
                self._pts.append(pt)
            i += 1
        if len(self._pts) < n_traps:
            raise ValueError(
                "Could not compute random traps in max iterations"
            )
        slug = (
            f"RandomLayout({self._n_traps} traps, "
            f"min spacing {self._min_spacing}µm)"
        )
        super().__init__(trap_coordinates=np.concatenate(self._pts), slug=slug)
