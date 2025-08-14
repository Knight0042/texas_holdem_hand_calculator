from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "equity_calc",  # module name
        ["equity_calc.cpp"],  # source file
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["/std:c++17"]  
    ),
]

setup(
    name="equity_calc",
    version="0.1",
    author="Dillon Barnes",
    description="Poker equity calculator in C++ with pybind11",
    ext_modules=ext_modules,
)
