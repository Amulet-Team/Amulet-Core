import numpy


def rotate_3d(
    verts: numpy.ndarray, x: float, y: float, z: float, dx: float, dy: float, dz: float
) -> numpy.ndarray:
    sb, sh, sa = numpy.sin(numpy.radians([x, y, z]))
    cb, ch, ca = numpy.cos(numpy.radians([x, y, z]))
    trmtx = numpy.array(
        [
            [ch * ca, -ch * sa * cb + sh * sb, ch * sa * sb + sh * cb],
            [sa, ca * cb, -ca * sb],
            [-sh * ca, sh * sa * cb + ch * sb, -sh * sa * sb + ch * cb],
        ]
    )
    origin = numpy.array([dx, dy, dz])
    return numpy.matmul(verts - origin, trmtx) + origin  # type: ignore
