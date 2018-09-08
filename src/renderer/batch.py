from typing import Union
from collections import Sequence
from numpy import ndarray
from pyglet.graphics import TextureGroup, Batch
from pyglet.gl import GL_QUADS


def add_texture_to_batch(
    texture_group: TextureGroup, vertices: Union[Sequence, ndarray], batch: Batch = None
):
    """
    Adding a 2d texture for future draw in the vertices specified
    :param texture_group: Object you can get using `get_texture_group` to specify a 2d texture to draw
    :param vertices: The vertices of the quads you want to draw
                     The order of the vertices is:
                     1) top left
                     2) bottom left
                     3) top right
                     4) bottom right
    :param batch: Optional. The batch to add the texture to. If gets None, it creates a new Batch object
    :return: The batch object the texture was added to
    """
    if not isinstance(vertices, (Sequence, ndarray)):
        raise TypeError("Type of vertices has to be a list or a numpy array")
    if not isinstance(texture_group, TextureGroup):
        raise TypeError("Type of texture has to be TextureGroup")
    if batch is None:
        batch = Batch()

    count = len(vertices) // 2
    batch.add(
        count,
        GL_QUADS,
        texture_group,
        ("v2f", vertices),
        ("t3f", texture_group.texture.tex_coords),
    )
    return batch
