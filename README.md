**Houdini** allows easy hotswapping of Python code. The snippet is currently
at ALPHA stage, but should soon be top notch.

### Basic usage example

Create the files **swapped.py**:
```python
from houdini import hotswap

@hotswap
def foo():
    return '0x0'
```

and **client.py**:
```python
import time
import swapped

while True:
    print swapped.foo()
    time.sleep(1)
```

Then, launch `client.py` and edit `swapped.py`. 


### Limitations

Currently only top-level functions and methods in top-level classes are
supported.
