from pyglet import resource
from pyglet.graphics import TextureGroup
from pyglet.image import Texture
from pyglet.gl import (
    glTexParameteri,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_NEAREST,
)


def add_textures_folder(folder: str) -> None:
    """
    Adds a folder of textures to the possible folders list where it can check later for textures
    :param folder: location of a folder where textures will be located
    """
    resource.path.append(folder)
    resource.reindex()


def get_texture_group(texture_file_name: str) -> TextureGroup:
    """
    Gets a texture group object of a texture needed.
    Can be used later to draw the texture
    :param texture_file_name: Name of the file of the texture. The name has to include the extension of the file.
                              The file has to be in a folder that was added with the `add_textures_folder` function
    :return: A TextureGroup object of the texture that can be used later to draw the texture
    """
    texture = resource.texture(texture_file_name)
    return _get_texture_group_from_texture(texture)


def get_partial_texture_group(
    texture_file_name: str, x: int, y: int, z: int, width: int, height: int
) -> TextureGroup:
    """
    Gets a texture group object of a partial texture needed.
    Partial texture is where you want to take a small part of a texture image file.
    Can be used later to draw the texture.
    :param texture_file_name: Name of the file of the texture. The name has to include the extension of the file.
                              The file has to be in a folder that was added with the `add_textures_folder` function
    :param x: The x of the lowest point of the part of the texture needed
    :param y: The y of the lowest point of the part of the texture needed
    :param z: The z of the lowest point of the part of the texture needed
    :param width: The width of the part of the texture needed
    :param height: The height of the part of the texture needed
    :return: A TextureGroup object of the texture that can be used later to draw the texture
    """
    texture = resource.texture(texture_file_name)
    partial_texture = texture.region_class(x, y, z, width, height, texture)
    return _get_texture_group_from_texture(partial_texture)


def _get_texture_group_from_texture(texture: Texture) -> TextureGroup:
    glTexParameteri(texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    return TextureGroup(texture)
