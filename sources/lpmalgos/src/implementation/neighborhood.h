#pragma once

#include "nanoflann.hpp"
#include "ellipsoid.h"
#include <memory>

namespace lpmalgos
{

namespace __private_nanoflann
{
template <typename T> struct PointCloud {
    struct Point {
        T x, y, z;
    };

    using coord_t = T; // The type of each coordinate

    std::vector<Point> pts;
    size_t size() const { return pts.size(); }

    // Must return the number of data points
    inline size_t kdtree_get_point_count() const { return pts.size(); }

    // Returns the dim'th component of the idx'th point in the class:
    // Since this is inlined and the "dim" argument is typically an immediate
    // value, the
    //  "if/else's" are actually solved at compile time.
    inline T kdtree_get_pt(const size_t idx, const size_t dim) const
    {
        if (dim == 0)
            return pts[idx].x;
        else if (dim == 1)
            return pts[idx].y;
        return pts[idx].z;
    }

    // Optional bounding-box computation: return false to default to a standard
    // bbox computation loop.
    //   Return true if the BBOX was already computed by the class and returned
    //   in "bb" so it can be avoided to redo it again. Look at bb.size() to
    //   find out the expected dimensionality (e.g. 2 or 3 for point clouds)
    template <class BBOX> bool kdtree_get_bbox(BBOX & /* bb */) const
    {
        return false;
    }
};
} // namespace __private_nanoflann

class Neighborhood
{
public:
    Neighborhood(const Locations &locs, const Ellipsoid &ani);
    Neighborhood(const Locations &locs);

    std::vector<size_t> find_neighbors(const Location &p,
                                       size_t max_neighbors) const;
    std::vector<size_t> find_neighbors(const Location &p,
                                       double max_radius) const;

    size_t nearest_neighbor(const Location &p);

    size_t size() const { return cloud.size(); }

private:
    using location_function = std::function<Location(size_t)>;
    using Point_cloud = __private_nanoflann::PointCloud<double>;
    using l2adaptor = nanoflann::L2_Simple_Adaptor<double, Point_cloud>;
    using kd_tree = nanoflann::KDTreeSingleIndexAdaptor<l2adaptor, Point_cloud, 3, size_t>;

    Neighborhood(size_t size, const location_function &loc);

    Point_cloud cloud;
    std::unique_ptr<kd_tree> kdtree;

    bool use_anisotropy = false;
    Ellipsoid anisotropy;
};

} // namespace lpmalgos