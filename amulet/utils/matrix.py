import math
import numpy
from typing import Optional
from amulet.api.data_types import FloatTriplet, PointCoordinates


def scale_matrix(sx: float, sy: float, sz: float) -> numpy.ndarray:
    return numpy.array(
        [
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ],
        dtype=numpy.float64
    )


def displacement_matrix(x: float, y: float, z: float) -> numpy.ndarray:
    return numpy.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [x, y, z, 1]
        ],
        dtype=numpy.float64
    )


def rotation_matrix(
        pitch: float,  # pitch (y axis) in radians
        yaw: float,  # pitch (transformed z axis) in radians
        roll: Optional[float] = None  # pitch (transformed x axis) in radians
) -> numpy.ndarray:
    c = math.cos(yaw)
    s = math.sin(yaw)

    y_rot = numpy.array(
        [
            [c, 0, -s, 0],
            [0, 1, 0, 0],
            [s, 0, c, 0],
            [0, 0, 0, 1]
        ],
        dtype=numpy.float64
    )

    c = math.cos(pitch)
    s = math.sin(pitch)

    x_rot = numpy.array(
        [
            [1, 0, 0, 0],
            [0, c, s, 0],
            [0, -s, c, 0],
            [0, 0, 0, 1]
        ],
        dtype=numpy.float64
    )

    mat = numpy.matmul(y_rot, x_rot)

    if roll:
        c = math.cos(roll)
        s = math.sin(roll)

        z_rot = numpy.array(
            [
                [c, s, 0, 0],
                [-s, c, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ],
            dtype=numpy.float64
        )
        mat = numpy.matmul(mat, z_rot)

    return mat


def transform_matrix(
    location: PointCoordinates,
    scale: FloatTriplet,
    rotation: FloatTriplet
):
    scale_transform = scale_matrix(*scale)
    rotation_transform = rotation_matrix(*rotation)
    displacement_transform = displacement_matrix(*location)
    return numpy.matmul(numpy.matmul(scale_transform, rotation_transform), displacement_transform)
