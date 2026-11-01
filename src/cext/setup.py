"""
setup.py for pybind11 examples

Build:
    pip install .
    # or
    python setup.py build_ext --inplace
"""

from setuptools import setup, find_packages

try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext

    ext_modules = [
        Pybind11Extension(
            "example",
            ["example.cpp"],
        ),
        Pybind11Extension(
            "vector",
            ["vector.cpp"],
        ),
        Pybind11Extension(
            "numpy_example",
            ["numpy_example.cpp"],
        ),
        Pybind11Extension(
            "gil_example",
            ["gil_example.cpp"],
        ),
    ]

    setup(
        name="pysheeet_cext",
        version="1.0.0",
        description="pybind11 extension examples for pysheeet",
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        python_requires=">=3.8",
    )
except ImportError:
    # pybind11 未安装，创建最小设置
    setup(
        name="pysheeet_cext",
        version="1.0.0",
        description="pybind11 extension examples for pysheeet",
    )
