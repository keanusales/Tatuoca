#pragma once

#include "neighborhood.h"

namespace lpmalgos
{

double angular_distance(const Location &A,
                        const Location &B,
                        const Location &C);

std::vector<int> find_clusters(const Locations &locs,
                               const Ellipsoid &ani,
                               double r_tol, double angular_tol,
                               double support_threshold,
                               int min_support_size);

} // namespace lpmalgos