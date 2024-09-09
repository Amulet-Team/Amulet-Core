from __future__ import annotations

import math as math
import types

import numpy as numpy

__all__ = [
    "FloatTriplet",
    "PointCoordinates",
    "decompose_transformation_matrix",
    "displacement_matrix",
    "inverse_transform_matrix",
    "math",
    "numpy",
    "rotation_matrix_x",
    "rotation_matrix_xy",
    "rotation_matrix_xyz",
    "rotation_matrix_y",
    "rotation_matrix_yx",
    "rotation_matrix_z",
    "scale_matrix",
    "transform_matrix",
]

def _rotation_matrix(*angles: float, order: str) -> numpy.ndarray:
    """

    Create a rotation matrix from the inputs specified

    :param angles: The angles in radians
    :param order: The order the angles are specified. Transforms will be applied in this order.
    :return: The 4x4 rotation matrix

    """

def decompose_transformation_matrix(
    matrix: numpy.ndarray,
) -> typing.Tuple[
    typing.Tuple[float, float, float],
    typing.Tuple[float, float, float],
    typing.Tuple[float, float, float],
]:
    """

    Decompose a 4x4 transformation matrix into scale, rotation and displacement tuples.

    :param matrix: The matrix to decompose.
    :return: The scale, rotation and displacement.

    """

def displacement_matrix(x: float, y: float, z: float) -> numpy.ndarray:
    """

    Create a displacement matrix from the inputs specified

    :param x: The displacement in the x axis
    :param y: The displacement in the y axis
    :param z: The displacement in the z axis
    :return: The 4x4 displacement matrix

    """

def inverse_transform_matrix(
    scale: tuple[float, float, float],
    rotation: tuple[float, float, float],
    displacement: tuple[float, float, float],
    order: typing.Literal["xyz", "xzy", "yxz", "yzx", "zxy", "zyx"] = "xyz",
) -> numpy.ndarray:
    """
    Create the inverse of the 4x4 transformation matrix from the scale, rotation and displacement specified.
        This should be the inverse of transform_matrix

        :param scale: The scale in the x, y and z axis
        :param rotation: The rotation in the x, y and z axis (axis can be changed using `order`)
        :param displacement: The displacement in the x, y and z axis
        :param order: The order to apply the rotations in.
        :return: The 4x4 transformation matrix of combined scale, rotation and displacement

    """

def rotation_matrix_x(rx: float) -> numpy.ndarray:
    """

    Create a rotation matrix in the x axis

    :param rx: The angle in radians
    :return: The 4x4 rotation matrix

    """

def rotation_matrix_xy(rx: float, ry: float) -> numpy.ndarray:
    """

    Create a rotation matrix from the inputs specified

    :param rx: The rotation in radians in the x axis
    :param ry: The rotation in radians in the y axis
    :return: The 4x4 rotation matrix

    """

def rotation_matrix_xyz(x: float, y: float, z: float) -> numpy.ndarray:
    """

    Create a rotation matrix from the inputs specified

    :param x: The rotation in radians in the x axis
    :param y: The rotation in radians in the y axis
    :param z: The rotation in radians in the z axis
    :return: The 4x4 rotation matrix

    """

def rotation_matrix_y(ry: float) -> numpy.ndarray:
    """

    Create a rotation matrix in the x axis

    :param ry: The angle in radians
    :return: The 4x4 rotation matrix

    """

def rotation_matrix_yx(ry: float, rx: float) -> numpy.ndarray:
    """

    Create a rotation matrix from the inputs specified

    :param rx: The rotation in radians in the x axis
    :param ry: The rotation in radians in the y axis
    :return: The 4x4 rotation matrix

    """

def rotation_matrix_z(rz: float) -> numpy.ndarray:
    """

    Create a rotation matrix in the x axis

    :param rz: The angle in radians
    :return: The 4x4 rotation matrix

    """

def scale_matrix(sx: float, sy: float, sz: float) -> numpy.ndarray:
    """

    Create a scale matrix from the inputs specified

    :param sx: The scale in the x axis
    :param sy: The scale in the y axis
    :param sz: The scale in the z axis
    :return: The 4x4 scale matrix

    """

def transform_matrix(
    scale: tuple[float, float, float],
    rotation: tuple[float, float, float],
    displacement: tuple[float, float, float],
    order: typing.Literal["xyz", "xzy", "yxz", "yzx", "zxy", "zyx"] = "xyz",
) -> numpy.ndarray:
    """
    Create a 4x4 transformation matrix from the scale, rotation and displacement specified.

        :param scale: The scale in the x, y and z axis
        :param rotation: The rotation in the x, y and z axis in radians. (axis can be changed using `order`)
        :param displacement: The displacement in the x, y and z axis
        :param order: The order to apply the rotations in.
        :return: The 4x4 transformation matrix of combined scale, rotation and displacement

    """

FloatTriplet: types.GenericAlias  # value = tuple[float, float, float]
PointCoordinates: types.GenericAlias  # value = tuple[float, float, float]
