#pragma once

#include "machine.h"
#include <thread>

namespace lpmalgos
{

unsigned num_threads()
{
    unsigned nthreads = std::thread::hardware_concurrency();
    if (!nthreads) return 1;
    return nthreads;
}

} // namespace lpmalgos