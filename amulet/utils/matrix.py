import math
import numpy
from amulet.api.data_types import FloatTriplet, PointCoordinates


def scale_matrix(sx: float, sy: float, sz: float) -> numpy.ndarray:
    return numpy.array(
        [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]], dtype=numpy.float64
    )


def displacement_matrix(x: float, y: float, z: float) -> numpy.ndarray:
    return numpy.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [x, y, z, 1]], dtype=numpy.float64
    )


def rotation_matrix(*angles, order="xy") -> numpy.ndarray:
    mat = numpy.identity(4, dtype=numpy.float64)

    for angle, axis in zip(angles, order):
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == "x":
            mat = numpy.matmul(
                numpy.array(
                    [[1, 0, 0, 0], [0, c, s, 0], [0, -s, c, 0], [0, 0, 0, 1]],
                    dtype=numpy.float64,
                ),
                mat,
            )
        elif axis == "y":
            mat = numpy.matmul(
                numpy.array(
                    [[c, 0, -s, 0], [0, 1, 0, 0], [s, 0, c, 0], [0, 0, 0, 1]],
                    dtype=numpy.float64,
                ),
                mat,
            )
        elif axis == "z":
            mat = numpy.matmul(
                numpy.array(
                    [[c, s, 0, 0], [-s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                    dtype=numpy.float64,
                ),
                mat,
            )

    return mat


def transform_matrix(
    location: PointCoordinates, scale: FloatTriplet, rotation: FloatTriplet, order="xyz"
):
    scale_transform = scale_matrix(*scale)
    rotation_transform = rotation_matrix(*rotation, order=order)
    displacement_transform = displacement_matrix(*location)
    return numpy.matmul(
        numpy.matmul(scale_transform, rotation_transform), displacement_transform
    )
