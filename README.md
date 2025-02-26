# learnopengl.com code repository (Python version)
Python translation of the popular [LearnOpenGL](https://learnopengl.com)'s source code and exercise repository.
Currently chapters 1-6 have been completely translated.

The translation is very close to the original C++ source code, which makes it easy to use alongside the tutorial.
It's partially machine translated. Please create an issue if you notice any mistakes, incorrect requirements or wrong formatting.

Most examples should run right out of the box, as they install the PyPI requirements automatically from the respective `requirements.txt`.
**Python `3.9+`** is required.

## Getting started
You can find the examples in the `src` folder.  
You may want to use them alongside [LearnOpenGL.com](https://learnopengl.com).  
To run the first example you simply need to run `src/1.getting_started/1.1.hello_window/hello_window.py`.

Here are some screenshots of the examples (one from each chapter):  
## Chapter 1, [Exercise 5.1](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/1.getting_started/5.1.transformations)
![Chapter 1](screenshots/1.5.1.png)
## Chapter 2, [Exercise 6](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/2.lighting/6.multiple_lights)
![Chapter 2](screenshots/2.6.png)
## Chapter 3, [Exercise 1](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/3.model_loading/1.model_loading)
![Chapter 3](screenshots/3.1.png)
## Chapter 4, [Exercise 10.3](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/4.advanced_opengl/10.3.asteroids_instanced)
![Chapter 4](screenshots/4.10.3.png)
## Chapter 5, [Exercise 8.1](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/5.advanced_lighting/8.1.deferred_shading)
![Chapter 5](screenshots/5.8.1.png)
## Chapter 6, [Exercise 2.2.1](https://github.com/Zuzu-Typ/LearnOpenGL-Python/tree/master/src/6.pbr/2.2.1.ibl_specular)
![Chapter 6](screenshots/6.2.2.1.png)

## Troubleshooting
### NumPy related error
If you get an error related to `numpy` when running one of the examples, make sure to install version `1.26.4`:
```
pip install numpy==1.26.4
```

### Other errors
If an example does not run out of the box, please make sure the required packages are installed. This should happen automatically,
however, this project uses an old version of my requirements installer, which might not work correctly on all platforms.
If you suspect that required packages are missing, please take a look at `master_requirements.dat` and install the packages listed there.

Otherwise, feel free to open a new issue.
