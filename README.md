# learnopengl.com code repository (Python version)
Python translation of the popular [LearnOpenGL](https://learnopengl.com)'s source code and exercise repository.
Currently only chapters 1-5 have been completely translated.

The translation is very close to the original C++ source code, which makes it easy to use alongside the tutorial.

Most examples should run right out of the box, as they install the PyPI requirements automatically from the respective `requirements.txt`.

For chapters 3 and up you need the `assimp-py` library, which has a broken source distro on the PyPI.  
If you can install assimp-py from the PyPI using `pip install assimp-py`, you're all set.  
Otherwise, please navigate to the `assimp-py distro` folder, where I put a working distro.  
Run `pip install assimp_py-1.0.2.tar.gz` to install it (requires a working C compiler).

(Work in progress)
