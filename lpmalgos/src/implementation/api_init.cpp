#pragma once

#include "neighborhood.h"
#include "ellipsoid.h"
#include "geodesics.h"
#include "machine.h"

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace py::literals;

template <typename T>
inline py::array_t<T> asarray(std::vector<T> &&entrie) {
    using vector = std::vector<T>;
    vector *ptr = new vector(std::move(entrie));
    py::capsule capsule(ptr, [](void* foo) {
        delete reinterpret_cast<vector*>(foo);
    });
    return py::array_t<T>(
        (*ptr).size(), (*ptr).data(), capsule
    );
}

void register_lpmalgos_module(py::module_ &m)
{
    m.def("angular_distance", lpmalgos::angular_distance,
        "A"_a, "B"_a, "C"_a);

    m.def("find_clusters", [](const lpmalgos::Locations &locs,
                              const lpmalgos::Ellipsoid &ani,
                              double r_tol, double angular_tol,
                              double support_threshold,
                              int min_support_size){
            return asarray(lpmalgos::find_clusters(locs, ani, r_tol,
                angular_tol, support_threshold, min_support_size));
        }, "locs"_a, "anisotropy"_a.noconvert(), "r_tol"_a,
        "angular_tol"_a, "support_threshold"_a, "min_support_size"_a);

    using lpmalgos::EllipsoidInfo;
    py::class_<EllipsoidInfo> ellipsoid_info(m, "EllipsoidInfo",
                                             py::module_local());

    ellipsoid_info.def("r1", [](EllipsoidInfo &self) { return self.r1; });
    ellipsoid_info.def("r2", [](EllipsoidInfo &self) { return self.r2; });
    ellipsoid_info.def("r3", [](EllipsoidInfo &self) { return self.r3; });
    ellipsoid_info.def("azimuth", [](EllipsoidInfo &self) { return self.azimuth; });
    ellipsoid_info.def("dip", [](EllipsoidInfo &self) { return self.dip; });
    ellipsoid_info.def("rake", [](EllipsoidInfo &self) { return self.rake; });

    using lpmalgos::Ellipsoid;
    py::class_<Ellipsoid> ellipsoid(m, "Ellipsoid", py::module_local());

    ellipsoid
        .def(py::init<>([](const lpmalgos::Matrix &transpose) {
                return new Ellipsoid(transpose);
             }), "transpose"_a)

        .def(py::init<>([](double r1, double r2, double r3,
                           double azimuth, double dip, double rake) {
                return new Ellipsoid(r1, r2, r3, azimuth, dip, rake);
             }), "r1"_a, "r2"_a, "r3"_a, "azimuth"_a, "dip"_a, "rake"_a)

        .def(py::init<>([](Eigen::Vector3d length, Eigen::Vector3d rotton) {
                return new Ellipsoid(length.x(), length.y(), length.z(),
                                     rotton.x(), rotton.y(), rotton.z());
             }), "length"_a, "rotation"_a)

        .def(py::init<>( [](const EllipsoidInfo &info) {
                return new Ellipsoid(info);
            }), "ellipsoid_info"_a.noconvert())

        .def("info", [](Ellipsoid &self) { return self.info(); })

        .def("forward",
            [](Ellipsoid &self, const lpmalgos::Location &p) {
                return self.forward(p); }, "location"_a)
        .def("backward",
            [](Ellipsoid &self, const lpmalgos::Location &p) {
                return self.backward(p); }, "location"_a)

        .def("forward",
            [](Ellipsoid &self, const lpmalgos::Locations &locs) {
                return (self.forward(locs)); }, "locs"_a)
        .def("backward",
            [](Ellipsoid &self, const lpmalgos::Locations &locs) {
                return (self.backward(locs)); }, "locs"_a)

        .def("matrix", [](Ellipsoid &self) { return self.matrix(); })
        .def("inv_matrix", [](Ellipsoid &self) { return self.inv_matrix(); })

        .def("major_axis", [](Ellipsoid &self) { return self.major_axis(); })
        .def("mid_axis", [](Ellipsoid &self) { return self.mid_axis(); })
        .def("minor_axis", [](Ellipsoid &self) { return self.minor_axis(); })

        .def("__str__", [](Ellipsoid &self) { return self.to_string(); });

    m.def("extract_ellipsoid_info", lpmalgos::extract_ellipsoid_info, "T"_a);
    m.def("sort_matrix3d", lpmalgos::sort_matrix3d, "T"_a, "orthogonalize"_a = true);
    m.def("orthogonolize_axes", lpmalgos::orthogonolize_axes, "T"_a, "sort"_a = true);

    using lpmalgos::Neighborhood;
    py::class_<Neighborhood> neighborhood(m, "Neighborhood", py::module_local());

    neighborhood
        .def(py::init<>([](const lpmalgos::Locations &locs,
                           const Ellipsoid &ellipsoid) {
                return new Neighborhood(locs, ellipsoid);
             }), "locations"_a, "ellipsoid"_a.noconvert())
        .def(py::init<>([](const lpmalgos::Locations &locs) {
                return new Neighborhood(locs);
             }), "locations"_a)

        .def("find_neighbors",
            [](Neighborhood &self, const lpmalgos::Location &p, int max_size) {
                return asarray(self.find_neighbors(p, max_size));
            }, "point"_a, "max_size"_a)
        .def("find_neighbors",
            [](Neighborhood &self, const lpmalgos::Location &p, double max_radius) {
                return asarray(self.find_neighbors(p, max_radius));
            }, "point"_a, "max_radius"_a)
        .def("nearest_neighbor",
            [](Neighborhood &self, const lpmalgos::Location &p) {
                return self.nearest_neighbor(p);
            }, "point"_a);
}

PYBIND11_MODULE(lpmalgos, m) { register_lpmalgos_module(m); }