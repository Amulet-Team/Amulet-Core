from typing import Tuple
import math
import numpy
from amulet.api.data_types import FloatTriplet, PointCoordinates


def scale_matrix(sx: float, sy: float, sz: float) -> numpy.ndarray:
    """
    Create a scale matrix from the inputs specified

    :param sx: The scale in the x axis
    :param sy: The scale in the y axis
    :param sz: The scale in the z axis
    :return: The 4x4 scale matrix
    """
    return numpy.array(
        [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]], dtype=numpy.float64
    )


def displacement_matrix(x: float, y: float, z: float) -> numpy.ndarray:
    """
    Create a displacement matrix from the inputs specified

    :param x: The displacement in the x axis
    :param y: The displacement in the y axis
    :param z: The displacement in the z axis
    :return: The 4x4 displacement matrix
    """
    return numpy.array(
        [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]], dtype=numpy.float64
    )


def _rotation_matrix(*angles: float, order=None) -> numpy.ndarray:
    """
    Create a rotation matrix from the inputs specified

    :param angles: The angles in radians
    :param order: The order the angles are specified. Transforms will be applied in this order.
    :return: The 4x4 rotation matrix
    """
    assert isinstance(order, str) and len(order) == len(
        angles
    ), "Order must be a string of the same length as angles."
    mat = numpy.identity(4, dtype=numpy.float64)

    for angle, axis in zip(angles, order):
        if angle:
            c = math.cos(angle)
            s = math.sin(angle)
            if axis == "x":
                mat = numpy.matmul(
                    numpy.array(
                        [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]],
                        dtype=numpy.float64,
                    ),
                    mat,
                )
            elif axis == "y":
                mat = numpy.matmul(
                    numpy.array(
                        [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]],
                        dtype=numpy.float64,
                    ),
                    mat,
                )
            elif axis == "z":
                mat = numpy.matmul(
                    numpy.array(
                        [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                        dtype=numpy.float64,
                    ),
                    mat,
                )

    return mat


def rotation_matrix_x(rx: float) -> numpy.ndarray:
    """
    Create a rotation matrix in the x axis

    :param rx: The angle in radians
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(rx, order="x")


def rotation_matrix_y(ry: float) -> numpy.ndarray:
    """
    Create a rotation matrix in the x axis

    :param ry: The angle in radians
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(ry, order="y")


def rotation_matrix_z(rz: float) -> numpy.ndarray:
    """
    Create a rotation matrix in the x axis

    :param rz: The angle in radians
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(rz, order="z")


def rotation_matrix_xy(rx: float, ry: float) -> numpy.ndarray:
    """
    Create a rotation matrix from the inputs specified

    :param rx: The rotation in radians in the x axis
    :param ry: The rotation in radians in the y axis
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(rx, ry, order="xy")


def rotation_matrix_yx(ry: float, rx: float) -> numpy.ndarray:
    """
    Create a rotation matrix from the inputs specified

    :param rx: The rotation in radians in the x axis
    :param ry: The rotation in radians in the y axis
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(ry, rx, order="yx")


def rotation_matrix_xyz(x: float, y: float, z: float) -> numpy.ndarray:
    """
    Create a rotation matrix from the inputs specified

    :param x: The rotation in radians in the x axis
    :param y: The rotation in radians in the y axis
    :param z: The rotation in radians in the z axis
    :return: The 4x4 rotation matrix
    """
    return _rotation_matrix(x, y, z, order="xyz")


def transform_matrix(
    scale: FloatTriplet,
    rotation: FloatTriplet,
    displacement: PointCoordinates,
    order="xyz",
):
    """Create a 4x4 transformation matrix from the scale, rotation and displacement specified.

    :param scale: The scale in the x, y and z axis
    :param rotation: The rotation in the x, y and z axis in radians. (axis can be changed using `order`)
    :param displacement: The displacement in the x, y and z axis
    :param order: The order to apply the rotations in.
    :return: The 4x4 transformation matrix of combined scale, rotation and displacement
    """
    scale_transform = scale_matrix(*scale)
    rotation_transform = _rotation_matrix(*rotation, order=order)
    displacement_transform = displacement_matrix(*displacement)
    return numpy.matmul(
        displacement_transform,
        numpy.matmul(rotation_transform, scale_transform),
    )


def inverse_transform_matrix(
    scale: FloatTriplet,
    rotation: FloatTriplet,
    displacement: PointCoordinates,
    order="xyz",
):
    """Create the inverse of the 4x4 transformation matrix from the scale, rotation and displacement specified.
    This should be the inverse of transform_matrix

    :param scale: The scale in the x, y and z axis
    :param rotation: The rotation in the x, y and z axis (axis can be changed using `order`)
    :param displacement: The displacement in the x, y and z axis
    :param order: The order to apply the rotations in.
    :return: The 4x4 transformation matrix of combined scale, rotation and displacement
    """
    scale_transform = scale_matrix(*1 / numpy.asarray(scale))
    ra, rb, rc = -numpy.asarray(rotation)
    rotation_transform = _rotation_matrix(
        rc, rb, ra, order="".join(list(reversed(order)))
    )
    displacement_transform = displacement_matrix(*-numpy.asarray(displacement))
    return numpy.matmul(
        scale_transform,
        numpy.matmul(rotation_transform, displacement_transform),
    )


def decompose_transformation_matrix(
    matrix: numpy.ndarray,
) -> Tuple[
    Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]
]:
    """
    Decompose a 4x4 transformation matrix into scale, rotation and displacement tuples.

    :param matrix: The matrix to decompose.
    :return: The scale, rotation and displacement.
    """
    assert isinstance(matrix, numpy.ndarray), "Matrix must be an ndarray"
    assert matrix.shape == (4, 4), "Expected a 4x4 numpy array"
    # https://gist.github.com/Aerilius/0cbc46271c163746717902b36bea8fd4
    # 0 4 8  12
    # 1 5 9  13
    # 2 6 10 14
    # 3 7 11 15
    matrix = matrix.copy()  # just in case
    displacement = tuple(matrix[:3, 3].tolist())
    matrix[:3, 3] = 0
    scale_np = numpy.linalg.norm(matrix[:3, :3], axis=0) * matrix[3, 3]
    scale = tuple(scale_np.tolist())
    matrix[:3, :3] = matrix[:3, :3] / scale_np

    matrix[3, 3] = 1

    if (
        numpy.dot(
            numpy.cross(
                matrix[:3, 0],
                matrix[:3, 1],
            ),
            matrix[:3, 2],
        )
        < 0
    ):
        scale = (-scale[0], scale[1], scale[2])
        matrix[:3, 0] *= -1

    rotation = (
        math.atan2(matrix[2, 1], matrix[2, 2]),
        math.atan2(
            -matrix[2, 0],
            (matrix[2, 1] ** 2 + matrix[2, 2] ** 2) ** 0.5,
        ),
        math.atan2(matrix[1, 0], matrix[0, 0]),
    )

    return scale, rotation, displacement
