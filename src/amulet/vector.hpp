#pragma once

namespace Amulet {

template <typename T>
class Vec2 {
public:
    T x;
    T y;

    Vec2(T x, T y)
        : x(x)
        , y(y)
    {
    }
};

template <typename T>
class Vec3 {
public:
    T x;
    T y;
    T z;

    Vec3(T x, T y, T z)
        : x(x)
        , y(y)
        , z(z)
    {
    }
};

} // namespace Amulet
