#pragma once

#pragma warning(disable: 4267)

#include "geodesics.h"
#include <queue>
#include <map>

namespace lpmalgos
{

static const double pi = std::acos(-1);

double angular_distance(const Location &A,
                        const Location &B,
                        const Location &C)
{
    Location u = A - C;
    Location v = B - C;
    if (u.norm() < 1e-15) {
        return pi / 2;
    }
    if (v.norm() < 1e-15) {
        return pi / 2;
    }
    return std::acos(std::fabs(u.dot(v) / (u.norm() * v.norm())));
}

std::vector<int> find_clusters(const Locations &locs,
                               const Ellipsoid &ani,
                               double r_tol, double angular_tol,
                               double support_threshold,
                               int min_support_size)
{
    angular_tol = std::fabs(pi * angular_tol / 180);
    unsigned n_threads = num_threads();
    Neighborhood nei(locs, ani);

    std::vector<std::vector<size_t>> neis(locs.size());

#pragma omp parallel for num_threads(n_threads)
    for (int i = 0; i < locs.size(); ++i) {
        neis[i] = nei.find_neighbors(locs[i], r_tol);
    }

    std::vector<int> support_size(locs.size(), 0);
    std::vector<int> total_size(locs.size(), 0);

    std::vector<std::map<int, int>> weight(locs.size());
    std::vector<std::map<int, int>> total_weight(locs.size());

    std::vector<std::vector<int>> G(locs.size());

#pragma omp parallel for num_threads(n_threads)
    for (int iA = 0; iA < locs.size(); ++iA) {
        const auto &A = locs[iA];

        for (size_t &iB : neis[iA]) {
            const auto &B = locs[iB];

            double angleAB = 0;
            double a1 = 1e30, a2 = 1e30;

            for (size_t &iC : neis[iB]) {
                const auto &C = locs[iC];
                double angle = angular_distance(A, B, C);
                a1 = std::min(angle, a1);

                if (angle < angular_tol) {
                    ++support_size[iA];
                    ++weight[iA][iB];
                }

                ++total_size[iA];
                ++total_weight[iA][iB];
            }

            for (size_t &iC : neis[iA]) {
                const auto &C = locs[iC];
                double angle = angular_distance(A, B, C);
                a2 = std::min(angle, a2);

                if (angle < angular_tol) {
                    ++support_size[iA];
                    ++weight[iA][iB];
                }

                ++total_size[iA];
                ++total_weight[iA][iB];
            }

            if (a2 > 1e20) {
                angleAB = a1;
            } else if (a1 > 1e20) {
                angleAB = a2;
            } else {
                angleAB = std::max(a1, a2);
            }

            if (angleAB < angular_tol) {
                if (weight[iA][iB] >= min_support_size) {
                    G[iA].push_back(iB);
                }
            }
        }
    }

    std::vector<int> cluster_ids(locs.size(), -1);

    int cluster_id = 0;

    for (int i = 0; i < locs.size(); ++i) {
        if (cluster_ids[i] == -1) {
            std::queue<int> Q;
            double t = support_size[i] / double(total_size[i]);
            if (t < support_threshold) {
                continue;
            }
            cluster_ids[i] = cluster_id;
            Q.push(i);
            while (!Q.empty()) {
                int iu = Q.front();
                Q.pop();
                for (int iv : G[iu]) {
                    double w = weight[iu][iv] / double(total_weight[iu][iv]);
                    if (w > support_threshold && cluster_ids[iv] == -1) {
                        cluster_ids[iv] = cluster_id;
                        Q.push(iv);
                    }
                }
            }
            ++cluster_id;
        }
    }

    return cluster_ids;
}

} // namespace lpmalgos

#pragma warning(default: 4267)