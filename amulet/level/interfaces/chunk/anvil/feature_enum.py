from enum import Enum


class BiomeState(Enum):
    BA256 = "256BA"  # 2D 16x16 byte array
    IA256 = "256IA"  # 2D 16x16 int array
    IA1024 = "1024IA"  # 3D 4x64x4 int array
    # 3D 4x4Nx4 int array. 4x4x4 array per sub-chunk with N sub-chunks
    IANx64 = "NX64IA"


class HeightState(Enum):
    Fixed256 = "fixed256"  # 0 start, 265 stop
    Variable1_17 = "variable1.17"  # a*16 start, b*16 stop
