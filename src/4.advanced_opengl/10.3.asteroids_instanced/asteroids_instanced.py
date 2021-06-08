try:
    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow
    from PIL import Image
    
    import glm

except ImportError:
    import requirements

    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow
    from PIL import Image
    
    import glm




from shader import Shader
from camera import Camera, Camera_Movement
from model import Model

import platform, ctypes, os

# the relative path where the textures are located
IMAGE_RESOURCE_PATH = "../../../resources/textures/"

# the relative path where the models are located
MODEL_RESOURCE_PATH = "../../../resources/objects"

# function that loads and automatically flips an image vertically
LOAD_IMAGE = lambda name: Image.open(os.path.join(IMAGE_RESOURCE_PATH, name)).transpose(Image.FLIP_TOP_BOTTOM)

# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600

# camera
camera = Camera(glm.vec3(0.0, 0.0, 155.0))
lastX = SCR_WIDTH / 2.0
lastY = SCR_HEIGHT / 2.0
firstMouse = True

# timing
deltaTime = 0.0
lastFrame = 0.0

def main() -> int:
    global deltaTime, lastFrame

    # glfw: initialize and configure
    # ------------------------------
    glfwInit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    if (platform.system() == "Darwin"): # APPLE
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    # glfw window creation
    # --------------------
    window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", None, None)
    if (window == None):

        print("Failed to create GLFW window")
        glfwTerminate()
        return -1

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)
    glfwSetCursorPosCallback(window, mouse_callback)
    glfwSetScrollCallback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)

    # configure global opengl state
    # -----------------------------
    glEnable(GL_DEPTH_TEST)

    # build and compile shaders
    # -------------------------
    asteroidShader = Shader("10.3.asteroids.vs", "10.3.asteroids.fs")
    planetShader = Shader("10.3.planet.vs", "10.3.planet.fs")
    # load models
    # -----------
    rock = Model(os.path.join(MODEL_RESOURCE_PATH, "rock/rock.obj"))
    planet = Model(os.path.join(MODEL_RESOURCE_PATH, "planet/planet.obj"))
    # generate a large list of semi-random model transformation matrices
    # ------------------------------------------------------------------
    amount = 100000
    modelMatrices = glm.array.zeros(amount, glm.mat4)
    glm.setSeed(int(glfwGetTime())) # initialize random seed	
    radius = 150.0
    offset = 25.0
    for i in range(amount):
        model = glm.mat4(1.0)
        # 1. translation: displace along circle with 'radius' in range [-offset, offset]
        angle = float(i) / amount * 360.0
        displacement = glm.linearRand(-offset, offset)
        x = glm.sin(angle) * radius + displacement
        displacement = glm.linearRand(-offset, offset)
        y = displacement * 0.4 # keep height of asteroid field smaller compared to width of x and z
        displacement = glm.linearRand(-offset, offset)
        z = glm.cos(angle) * radius + displacement
        model = glm.translate(model, glm.vec3(x, y, z))

        # 2. scale: Scale between 0.05 and 0.25
        scale = glm.linearRand(0.05, 0.25)
        model = glm.scale(model, glm.vec3(scale))

        # 3. rotation: add random rotation around a (semi)randomly picked rotation axis vector
        rotAngle = glm.linearRand(0, 360)
        model = glm.rotate(model, rotAngle, glm.vec3(0.4, 0.6, 0.8))

        # 4. now add to list of matrices
        modelMatrices[i] = model

    # configure instanced array
    # -------------------------
    buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glBufferData(GL_ARRAY_BUFFER, modelMatrices.nbytes, modelMatrices.ptr, GL_STATIC_DRAW)

    # set transformation matrices as an instance vertex attribute (with divisor 1)
    # note: we're cheating a little by taking the, now publicly declared, VAO of the model's mesh(es) and adding new vertexAttribPointers
    # normally you'd want to do this in a more organized fashion, but for learning purposes this will do.
    # -----------------------------------------------------------------------------------------------------------------------------------
    for i in range(len(rock.meshes)):

        VAO = rock.meshes[i].VAO
        glBindVertexArray(VAO)
        # set attribute pointers for matrix (4 times vec4)
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, glm.sizeof(glm.mat4), None)
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, glm.sizeof(glm.mat4), ctypes.c_void_p(glm.sizeof(glm.vec4)))
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, glm.sizeof(glm.mat4), ctypes.c_void_p(2 * glm.sizeof(glm.vec4)))
        glEnableVertexAttribArray(6)
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, glm.sizeof(glm.mat4), ctypes.c_void_p(3 * glm.sizeof(glm.vec4)))

        glVertexAttribDivisor(3, 1)
        glVertexAttribDivisor(4, 1)
        glVertexAttribDivisor(5, 1)
        glVertexAttribDivisor(6, 1)

        glBindVertexArray(0)

    # render loop
    # -----------
    while (not glfwWindowShouldClose(window)):

        # per-frame time logic
        # --------------------
        currentFrame = glfwGetTime()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        # input
        # -----
        processInput(window)

        # render
        # ------
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # configure transformation matrices
        projection = glm.perspective(glm.radians(45.0), SCR_WIDTH / SCR_HEIGHT, 0.1, 1000.0)
        view = camera.GetViewMatrix()
        asteroidShader.use()
        asteroidShader.setMat4("projection", projection)
        asteroidShader.setMat4("view", view)
        planetShader.use()
        planetShader.setMat4("projection", projection)
        planetShader.setMat4("view", view)
        
        # draw planet
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, -3.0, 0.0))
        model = glm.scale(model, glm.vec3(4.0, 4.0, 4.0))
        planetShader.setMat4("model", model)
        planet.Draw(planetShader)

        # draw meteorites
        asteroidShader.use()
        asteroidShader.setInt("texture_diffuse1", 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, rock.textures_loaded[0].id) # note: we also made the textures_loaded vector public (instead of private) from the model class.
        for i in range(len(rock.meshes)):

            glBindVertexArray(rock.meshes[i].VAO)
            glDrawElementsInstanced(GL_TRIANGLES, len(rock.meshes[i].indices), GL_UNSIGNED_INT, None, amount)
            glBindVertexArray(0)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
    return 0

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:
    global deltaTime

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS):
        glfwSetWindowShouldClose(window, True)

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.FORWARD, deltaTime)
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.BACKWARD, deltaTime)
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.LEFT, deltaTime)
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.RIGHT, deltaTime)

# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)

# glfw: whenever the mouse moves, this callback is called
# -------------------------------------------------------
def mouse_callback(window: GLFWwindow, xpos: float, ypos: float) -> None:
    global lastX, lastY, firstMouse

    if (firstMouse):

        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos # reversed since y-coordinates go from bottom to top

    lastX = xpos
    lastY = ypos

    camera.ProcessMouseMovement(xoffset, yoffset)

# glfw: whenever the mouse scroll wheel scrolls, this callback is called
# ----------------------------------------------------------------------
def scroll_callback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:

    camera.ProcessMouseScroll(yoffset)


main()
