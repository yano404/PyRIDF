PyRIDF
======

## Installation

Clone this repository.

```
git clone https://github.com/yano404/PyRIDF.git
```

Build PyRIDF and install to your environment.

```
cd PyRIDF
poetry build
pip install PyRIDF/dist/pyridf-x.y.z-py3-none-any.whl
```

## Usage

### Read RIDF file

```py
import pyridf
r = pyridf.read("/path/to/file.ridf")
```

### Write to RIDF file

```py
import pyridf
r = pyridf.ridf()
pyridf.write("/path/to/file.ridf", r)
```

## License
Copyright (c) 2023 Takayuki YANO

The source code is licensed under the MIT License, see LICENSE.
