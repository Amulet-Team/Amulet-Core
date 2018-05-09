from pyglet import resource
from pyglet.graphics import TextureGroup
from pyglet.gl import glTexParameteri, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_NEAREST


def add_textures_folder(folder: str) -> None:
    """
    Adds a folder of textures to the possible folders list where it can check later for textures
    :param folder: location of a folder where textures will be located
    """
    resource.path.append(folder)
    resource.reindex()


def get_texture_group(texture_file_name: str) -> TextureGroup:
    """
    Gets a texture group object of a texture needed. Can be used later to draw the texture
    :param texture_file_name: Name of the file of the texture. The name has to include the extension of the file.
                              The file has to be in a folder that was added with the `add_textures_folder` function
    :return: A TextureGroup object of the texture that can be used later to draw the texture
    """
    texture = resource.texture(texture_file_name)
    glTexParameteri(texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    return TextureGroup(texture)
