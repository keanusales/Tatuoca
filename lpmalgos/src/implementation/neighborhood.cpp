#pragma once

#pragma warning(disable: 4267)

#include "neighborhood.h"

namespace lpmalgos
{

Neighborhood::Neighborhood(size_t size, const location_function &loc)
{
    use_anisotropy = false;

    for (size_t i = 0; i < size; ++i) {
        auto p = loc(i);
        Point_cloud::Point point{p.x(), p.y(), p.z()};
        cloud.pts.push_back(point);
    }

    nanoflann::KDTreeSingleIndexAdaptorParams params;
    params.leaf_max_size = 10;
    kdtree = std::make_shared<my_kd_tree_t>(3, cloud, params);
}

Neighborhood::Neighborhood(const Locations &locs,
                           const Ellipsoid &ani)
    : Neighborhood(locs.size(), [&locs, &ani](size_t i)
                                { return ani.forward(locs[i]); })
{
    use_anisotropy = true;
    anisotropy = ani;
}

Neighborhood::Neighborhood(const Locations &locs)
    : Neighborhood(locs.size(), [&locs](size_t i) { return locs[i]; })
{
    use_anisotropy = false;
}

std::vector<size_t> Neighborhood::find_neighbors(const Location &p,
                                                 int max_neighbors) const
{
    if (max_neighbors > size()) {
        max_neighbors = size();
    }
    double query_pt[3];

    if (use_anisotropy) {
        Location q = anisotropy.forward(p);
        query_pt[0] = q.x();
        query_pt[1] = q.y();
        query_pt[2] = q.z();
    } else {
        query_pt[0] = p.x();
        query_pt[1] = p.y();
        query_pt[2] = p.z();
    }

    std::vector<size_t> neis(max_neighbors);
    double *dists = new double[max_neighbors];
    nanoflann::KNNResultSet<double> resultSet(max_neighbors);
    resultSet.init(neis.data(), dists);
    (*kdtree).findNeighbors(resultSet, &query_pt[0],
                            nanoflann::SearchParameters());
    delete[] dists;

    return neis;
}

std::vector<size_t> Neighborhood::find_neighbors(const Location &p,
                                                 double max_radius) const
{
    max_radius *= max_radius;
    double query_pt[3];

    if (use_anisotropy) {
        Location q = anisotropy.forward(p);
        query_pt[0] = q.x();
        query_pt[1] = q.y();
        query_pt[2] = q.z();
    } else {
        query_pt[0] = p.x();
        query_pt[1] = p.y();
        query_pt[2] = p.z();
    }

    std::vector<nanoflann::ResultItem<size_t, double>> ind;
    (*kdtree).radiusSearch(&query_pt[0], max_radius, ind,
                           nanoflann::SearchParameters());

    std::vector<size_t> neis(ind.size());
    for (size_t i = 0; i < ind.size(); i++) {
        neis[i] = ind[i].first;
    }

    return neis;
}

size_t Neighborhood::nearest_neighbor(const Location &p)
{
    auto neis = find_neighbors(p, 1);
    return neis[0];
}

} // namespace lpmalgos

#pragma warning(default: 4267)