##########################
 partial_3d_array package
##########################

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

    *

*************
 The Problem
*************

There was the need for a 3D array with an unlimited vertical height to
store block and biome data.

This was originally implemented to support the Cubic Chunks format but
it is also required now that Java and Bedrock are modifying the build
height limits.

*************
 Definitions
*************

    -  A 3D array: A three dimensional grid of values. In this context it
       will always store integer values greater than or equal to zero.

    -  A chunk: A part of a Minecraft world which is saved as one piece.
       Chunks are 16 blocks long in the x and z directions and are a
       variable number of blocks tall.

    -  A sub-chunk/section: A sub-chunk is a piece of a chunk. In the
       same way that a chunk is a 16 block wide slice of the world, a
       chunk is a 16 block tall slice of the chunk. This makes a
       sub-chunk represent a 16x16x16 block volume.

    -  sub-chunk coordinate: The y coordinate of the sub-chunk within the
       chunk. This is not the same as block coordinate.

**********
 Solution
**********

As you would expect, creating a single array with an infinite y
dimension would require an infinite amount of memory so it is not
possible.

Instead we create an array for each sub-chunk that contains data.

This saves a lot of memory and allows the array to have a variable
height.

The name partial array was chosen because it is an array that is able to
be partially defined.

:class:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray`
is the implementation of this behaviour.

Internally it stores the arrays for each sub-chunk in a dictionary of
the form ``Dict[SubChunkCoordinate, numpy.ndarray]``.

There are two ways to read and write the data contained within this class:
    #. The sub-chunk arrays can be directly read and written to. This is
       the fastest and preferable way.
    #. The class can be used in a similar way to a numpy array. This adds
       a bit of overhead which slows it down.

The direct API consists of:
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.sections`
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.create_section`
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.add_section`
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.get_section`

The numpy-like API consists of:
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.__getitem__`
    #. :meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.__setitem__`

These are used via the ``value = array[x, y, z]`` and ``array[x, y, z] =
value`` syntax respectively.

The getter method of a numpy array would return a view into the original
array such that modifying a slice of the original array will also modify
the original array.

This behaviour has been emulated with
:class:`~amulet.api.partial_3d_array.bounded_partial_3d_array.BoundedPartial3DArray`
which is returned by the
:meth:`~amulet.api.partial_3d_array.unbounded_partial_3d_array.UnboundedPartial3DArray.__getitem__`
methods.

As the names suggest the Unbounded variant has no vertical height limit
whereas the Bounded variant represents a finite volume of the original
Unbounded variant.

Modifying the Bounded variant via the numpy-like API will in turn modify
the original Unbounded version.
