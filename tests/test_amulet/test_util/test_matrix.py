import unittest
import numpy

from amulet.utils.matrix import (
    scale_matrix,
    displacement_matrix,
    rotation_matrix_xyz,
    transform_matrix,
    inverse_transform_matrix,
    decompose_transformation_matrix,
)


class MatrixTestCase(unittest.TestCase):
    def test_scale(self):
        numpy.testing.assert_array_equal(
            numpy.matmul(scale_matrix(1, 2, 3), (2, 2, 2, 1))[:3], (2, 4, 6)
        )

    def test_displacement(self):
        numpy.testing.assert_array_equal(
            numpy.matmul(displacement_matrix(1, 2, 3), (2, 2, 2, 1))[:3], (3, 4, 5)
        )

    def test_chain_displacement(self):
        numpy.testing.assert_array_equal(
            numpy.matmul(
                numpy.matmul(
                    displacement_matrix(1, 2, 3),
                    displacement_matrix(1, 2, 3),
                ),
                (2, 2, 2, 1),
            )[:3],
            (4, 6, 8),
        )

    def test_rotation_x(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    rotation_matrix_xyz(*numpy.deg2rad([90, 0, 0])), (1, 1, 1, 1)
                )[:3],
                1,
            ),
            (1, -1, 1),
        )

    def test_rotation_y(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    rotation_matrix_xyz(*numpy.deg2rad([0, 90, 0])), (1, 1, 1, 1)
                )[:3],
                1,
            ),
            (1, 1, -1),
        )

    def test_rotation_z(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    rotation_matrix_xyz(*numpy.deg2rad([0, 0, 90])), (1, 1, 1, 1)
                )[:3],
                1,
            ),
            (-1, 1, 1),
        )

    def test_chain_rotation(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    numpy.matmul(
                        rotation_matrix_xyz(*numpy.deg2rad([0, 90, 0])),
                        rotation_matrix_xyz(*numpy.deg2rad([0, 90, 0])),
                    ),
                    (1, 1, 1, 1),
                )[:3],
                1,
            ),
            (-1, 1, -1),
        )

    def test_chain_rotation_xy(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    numpy.matmul(
                        rotation_matrix_xyz(
                            *numpy.deg2rad([0, 90, 0])
                        ),  # y rotation applied second
                        rotation_matrix_xyz(
                            *numpy.deg2rad([90, 0, 0])
                        ),  # x rotation applied first
                    ),
                    (1, 1, 1, 1),
                )[:3],
                1,
            ),
            (1, -1, -1),
        )

    def test_rotation_xyz(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    rotation_matrix_xyz(*numpy.deg2rad([90, 90, 0])), (1, 1, 1, 1)
                )[:3],
                1,
            ),
            (1, -1, -1),
        )

    def test_transform(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    transform_matrix((1, 1, 1), (0, 0, 0), (10, 20, 30)), (1, 1, 1, 1)
                )[:3],
                1,
            ),
            (11, 21, 31),
        )

    def test_chain_transform(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    numpy.matmul(
                        transform_matrix(
                            (1, 1, 1), (0, numpy.deg2rad(90), 0), (0, 0, 0)
                        ),
                        transform_matrix((1, 1, 1), (0, 0, 0), (10, 20, 30)),
                    ),
                    (1, 1, 1, 1),
                )[:3],
                1,
            ),
            (31, 21, -11),
        )

    def test_chain_transform2(self):
        numpy.testing.assert_array_equal(
            numpy.round(
                numpy.matmul(
                    numpy.matmul(
                        transform_matrix((1, 1, 1), (0, 0, 0), (10, 20, 30)),
                        transform_matrix(
                            (1, 1, 1), (0, numpy.deg2rad(90), 0), (0, 0, 0)
                        ),
                    ),
                    (1, 1, 1, 1),
                )[:3],
                1,
            ),
            (11, 21, 29),
        )

    def test_inverse_transform(self):
        inputs = numpy.random.random(9).reshape((3, 3)).tolist()
        transform = transform_matrix(*inputs)
        inverse_transform = inverse_transform_matrix(*inputs)
        numpy.testing.assert_array_almost_equal(
            numpy.matmul(transform, inverse_transform), numpy.eye(4)
        )

    def test_decompose(self):
        rotation_ = (1, 1.5, 3)
        m = rotation_matrix_xyz(*rotation_)
        scale, rotation, displacement = decompose_transformation_matrix(m)
        numpy.testing.assert_array_almost_equal(
            displacement, (0, 0, 0), err_msg="decomposed displacement is incorrect"
        )
        numpy.testing.assert_array_almost_equal(
            scale, (1, 1, 1), err_msg="decomposed scale is incorrect"
        )
        numpy.testing.assert_array_almost_equal(
            rotation, rotation_, err_msg="decomposed rotation is incorrect"
        )

        m = transform_matrix((1, 2, 3), rotation_, (1, 2, 3))
        scale, rotation, displacement = decompose_transformation_matrix(m)
        numpy.testing.assert_array_almost_equal(
            displacement, (1, 2, 3), err_msg="decomposed displacement is incorrect"
        )
        numpy.testing.assert_array_almost_equal(
            scale, (1, 2, 3), err_msg="decomposed scale is incorrect"
        )
        numpy.testing.assert_array_almost_equal(
            rotation, rotation_, err_msg="decomposed rotation is incorrect"
        )


if __name__ == "__main__":
    unittest.main()
