#pragma once

#include "neighborhood.h"
#include "ellipsoid.h"
#include "geodesics.h"
#include "machine.h"

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;
using namespace py::literals;

const int flags = py::array::c_style + py::array::forcecast;

lpmalgos::Locations fromarray(const py::array_t<double, flags> &input)
{
    const size_t size = lpmalgos::Location::SizeAtCompileTime;
    if (input.ndim() != 2 || input.shape(1) != size) {
        throw py::cast_error("Cannot convert the input ndarray!");
    }
    lpmalgos::Locations output(input.shape(0));
    auto view = input.unchecked<2>();
    for (size_t i = 0; i < (size_t) input.shape(0); ++i) {
        output[i] = Eigen::Map<const lpmalgos::Location>(&view(i, 0));
    }
    return output;
}

py::array_t<double, flags> asarray(lpmalgos::Locations &&input)
{
    const size_t size = lpmalgos::Location::SizeAtCompileTime;
    py::array_t<double, flags> output({input.size(), size});
    auto view = output.mutable_unchecked<2>();
    for (size_t i = 0; i < input.size(); ++i) {
        Eigen::Map<lpmalgos::Location>(&view(i, 0)) = input[i];
    }
    return output;
}

template <typename T>
inline py::array_t<T> asarray(std::vector<T> &&input)
{
    size_t size = input.size();
    T *data = input.data();
    std::unique_ptr<std::vector<T>> ptr =
        std::make_unique<std::vector<T>>(std::move(input));
    py::capsule capsule(ptr.get(), [](void* foo) {
        delete reinterpret_cast<std::vector<T>*>(foo);
    });
    ptr.release();
    return py::array_t<T>(size, data, capsule);
}

void register_lpmalgos_module(py::module_ &m)
{
    m.def("angular_distance", lpmalgos::angular_distance,
        "A"_a, "B"_a, "C"_a);

    m.def("find_clusters", [](const py::array_t<int64_t, flags> &locs,
                              const lpmalgos::Ellipsoid &ani,
                              double r_tol, double angular_tol,
                              double support_threshold,
                              size_t min_support_size){
            return asarray(lpmalgos::find_clusters(fromarray(locs), ani,
                r_tol, angular_tol, support_threshold, min_support_size));
        }, "locs"_a.noconvert(), "anisotropy"_a.noconvert(), "r_tol"_a,
        "angular_tol"_a, "support_threshold"_a, "min_support_size"_a);

    using lpmalgos::EllipsoidInfo;
    py::class_<EllipsoidInfo> ellipsoid_info(m, "EllipsoidInfo",
                                             py::module_local());

    ellipsoid_info
        .def("r1", [](EllipsoidInfo &self) { return self.r1; })
        .def("r2", [](EllipsoidInfo &self) { return self.r2; })
        .def("r3", [](EllipsoidInfo &self) { return self.r3; })
        .def("azimuth", [](EllipsoidInfo &self) { return self.azimuth; })
        .def("dip", [](EllipsoidInfo &self) { return self.dip; })
        .def("rake", [](EllipsoidInfo &self) { return self.rake; });

    using lpmalgos::Ellipsoid;
    py::class_<Ellipsoid> ellipsoid(m, "Ellipsoid", py::module_local());

    ellipsoid
        .def(py::init([](double r1, double r2, double r3,
                         double azimuth, double dip, double rake) {
                return new Ellipsoid(r1, r2, r3, azimuth, dip, rake);
             }), "r1"_a, "r2"_a, "r3"_a, "azimuth"_a, "dip"_a, "rake"_a)
        .def(py::init([](const lpmalgos::Matrix &matrix) {
                return new Ellipsoid(matrix);
             }), "matrix"_a)
        .def(py::init([](const EllipsoidInfo &info) {
                return new Ellipsoid(info);
            }), "ellipsoid_info"_a.noconvert())
        .def(py::init([](){ return new Ellipsoid(); }))

        .def("forward",
            [](Ellipsoid &self, const lpmalgos::Location &loc) {
                return self.forward(loc); }, "loc"_a)
        .def("backward",
            [](Ellipsoid &self, const lpmalgos::Location &loc) {
                return self.backward(loc); }, "loc"_a)

        .def("forward",
            [](Ellipsoid &self, const py::array_t<int64_t, flags> &locs) {
                return asarray(self.forward(fromarray(locs)));
            }, "locs"_a.noconvert())
        .def("backward",
            [](Ellipsoid &self, const py::array_t<int64_t, flags> &locs) {
                return asarray(self.backward(fromarray(locs)));
            }, "locs"_a.noconvert())

        .def("matrix", [](Ellipsoid &self) { return self.matrix(); })
        .def("inv_matrix", [](Ellipsoid &self) { return self.inv_matrix(); })

        .def("major_axis", [](Ellipsoid &self) { return self.major_axis(); })
        .def("mid_axis", [](Ellipsoid &self) { return self.mid_axis(); })
        .def("minor_axis", [](Ellipsoid &self) { return self.minor_axis(); })

        .def("info", [](Ellipsoid &self) { return self.info(); })
        .def("__str__", [](Ellipsoid &self) { return self.to_string(); });

    m.def("extract_ellipsoid_info", lpmalgos::extract_ellipsoid_info, "T"_a);
    m.def("sort_matrix3d", lpmalgos::sort_matrix3d, "T"_a, "orthogonalize"_a = true);
    m.def("orthogonolize_axes", lpmalgos::orthogonolize_axes, "T"_a, "sort"_a = true);

    using lpmalgos::Neighborhood;
    py::class_<Neighborhood> neighborhood(m, "Neighborhood", py::module_local());

    neighborhood
        .def(py::init([](const py::array_t<int64_t, flags> &locs,
                         const Ellipsoid &ellipsoid) {
                return new Neighborhood(fromarray(locs), ellipsoid);
             }), "locs"_a.noconvert(), "ellipsoid"_a.noconvert())
        .def(py::init([](const py::array_t<int64_t, flags> &locs) {
                return new Neighborhood(fromarray(locs));
             }), "locs"_a.noconvert())

        .def("find_neighbors",
            [](Neighborhood &self, const lpmalgos::Location &loc, size_t max_size) {
                return asarray(self.find_neighbors(loc, max_size));
            }, "loc"_a, "max_size"_a.noconvert())
        .def("find_neighbors",
            [](Neighborhood &self, const lpmalgos::Location &loc, double max_radius) {
                return asarray(self.find_neighbors(loc, max_radius));
            }, "loc"_a, "max_radius"_a.noconvert())
        .def("nearest_neighbor",
            [](Neighborhood &self, const lpmalgos::Location &loc) {
                return self.nearest_neighbor(loc);
            }, "loc"_a);
}

PYBIND11_MODULE(lpmalgos, m) { register_lpmalgos_module(m); }