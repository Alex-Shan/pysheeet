REQUIREMENT = requirements.txt

VER  = $(word 2, $(shell python --version 2>&1))
SRC  = app.py app_test.py
PY36 = $(shell expr $(VER) \>= 3.6)
CEXT_DIR = src/cext
CEXT_BUILD = $(CEXT_DIR)/build
CAPI_DIR = src/cext/capi
CPP_FROM_PY_DIR = src/cpp_from_python
CPP_FROM_PY_BUILD = $(CPP_FROM_PY_DIR)/build
PY_ARCH = $(shell python -c "import platform; print(platform.machine())")

.PHONY: build deps test format cext
build: html

%:
	cd docs && make $@

clean:
	cd docs && make clean
	rm -rf $(CEXT_BUILD)
	rm -rf $(CPP_FROM_PY_BUILD)
	rm -rf $(CAPI_DIR)/build $(CAPI_DIR)/*.so $(CAPI_DIR)/*.egg-info

cext:
	@echo "Building C/C++ extensions for $(PY_ARCH)..."
	mkdir -p $(CEXT_BUILD) && \
	cd $(CEXT_BUILD) && \
	cmake -DCMAKE_OSX_ARCHITECTURES=$(PY_ARCH) .. && \
	make
	cd $(CAPI_DIR) && python setup.py build_ext --inplace

cpp_from_python:
	@echo "Building C++ from Python examples..."
	mkdir -p $(CPP_FROM_PY_BUILD) && \
	cd $(CPP_FROM_PY_BUILD) && \
	cmake .. && \
	make

test: clean build cext cpp_from_python
	pycodestyle $(SRC)
	pydocstyle $(SRC)
	bandit app.py
	coverage run app_test.py && coverage report --fail-under=100 -m $(SRC)
	python -m pytest src/basic/*.py src/new_py3/*.py -v
	python -m pytest $(CEXT_DIR)/test_cext.py -v
	python -m pytest $(CAPI_DIR)/test_capi.py -v
	cd $(CPP_FROM_PY_BUILD) && make test
ifeq ($(PY36), 1)
	black --quiet --diff --check --line-length 79 $(SRC)
endif

deps:
	pip install -r requirements.txt
	pip install pybind11
ifeq ($(PY36), 1)
	pip install black==22.3.0
endif

format:
	black --line-length 79 $(SRC) src/
	find src/cext -type f \( -name "*.cpp" -o -name "*.c" -o -name "*.h" \) | xargs -I{} clang-format -style=file -i {}

# 中文文档构建与检查，不安装或升级示例运行依赖。
.PHONY: docs-deps docs-html docs-check docs-preview
docs-deps:
	python -m pip install --require-hashes -r requirements-docs.lock

docs-html:
	python -m sphinx -a -b html -d docs/_build/doctrees -W --keep-going docs docs/_build/html

docs-check: docs-html
	python tools/check_docs.py

docs-preview:
	python -m http.server 8000 --directory docs/_build/html
