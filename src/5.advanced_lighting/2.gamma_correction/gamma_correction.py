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

import platform, ctypes, os

# the relative path where the textures are located
IMAGE_RESOURCE_PATH = "../../../resources/textures/"

# function that loads and automatically flips an image vertically
LOAD_IMAGE = lambda name: Image.open(os.path.join(IMAGE_RESOURCE_PATH, name)).transpose(Image.FLIP_TOP_BOTTOM)

# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600
gammaEnabled = False
gammaKeyPressed = False

# camera
camera = Camera(glm.vec3(0.0, 0.0, 3.0))
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
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # build and compile shaders
    # -------------------------
    shader = Shader("2.gamma_correction.vs", "2.gamma_correction.fs")
    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    planeVertices = glm.array(glm.float32,
        # positions            # normals         # texcoords
         10.0, -0.5,  10.0,  0.0, 1.0, 0.0,  10.0,  0.0,
        -10.0, -0.5,  10.0,  0.0, 1.0, 0.0,   0.0,  0.0,
        -10.0, -0.5, -10.0,  0.0, 1.0, 0.0,   0.0, 10.0,

         10.0, -0.5,  10.0,  0.0, 1.0, 0.0,  10.0,  0.0,
        -10.0, -0.5, -10.0,  0.0, 1.0, 0.0,   0.0, 10.0,
         10.0, -0.5, -10.0,  0.0, 1.0, 0.0,  10.0, 10.0)

    # plane VAO
    planeVAO = glGenVertexArrays(1)
    planeVBO = glGenBuffers(1)
    glBindVertexArray(planeVAO)
    glBindBuffer(GL_ARRAY_BUFFER, planeVBO)
    glBufferData(GL_ARRAY_BUFFER, planeVertices.nbytes, planeVertices.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
    glBindVertexArray(0)

    # load textures
    # -------------
    floorTexture               = loadTexture("wood.png", False)
    floorTextureGammaCorrected = loadTexture("wood.png", True)

    # shader configuration
    # --------------------
    shader.use()
    shader.setInt("floorTexture", 0)

    # lighting info
    # -------------
    lightPositions = glm.array(
        glm.vec3(-3.0, 0.0, 0.0),
        glm.vec3(-1.0, 0.0, 0.0),
        glm.vec3 (1.0, 0.0, 0.0),
        glm.vec3 (3.0, 0.0, 0.0)
    )

    lightColors = glm.array(
        glm.vec3(0.25),
        glm.vec3(0.50),
        glm.vec3(0.75),
        glm.vec3(1.00)
    )

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

        # draw objects
        shader.use()
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        shader.setMat4("projection", projection)
        shader.setMat4("view", view)
        # set light uniforms
        glUniform3fv(glGetUniformLocation(shader.ID, "lightPositions"), 4, lightPositions.ptr)
        glUniform3fv(glGetUniformLocation(shader.ID, "lightColors"), 4, lightColors.ptr)
        shader.setVec3("viewPos", camera.Position)
        shader.setInt("gamma", gammaEnabled)
        # floor
        glBindVertexArray(planeVAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, floorTextureGammaCorrected if gammaEnabled else floorTexture)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        print("Gamma enabled" if gammaEnabled else "Gamma disabled")

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (planeVAO,))
    glDeleteBuffers(1, (planeVBO,))

    glfwTerminate()
    return 0

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:
    global deltaTime, gammaEnabled, gammaKeyPressed

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

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS and not gammaKeyPressed):

        gammaEnabled = not gammaEnabled
        gammaKeyPressed = True

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_RELEASE):

        gammaKeyPressed = False


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

# utility function for loading a 2D texture from file
# ---------------------------------------------------
def loadTexture(path : str, gammaCorrection : bool) -> int:
    textureID = glGenTextures(1)

    try:
        img = LOAD_IMAGE(path)
        
        nrComponents = len(img.getbands())

        dataFormat = GL_RED if nrComponents == 1 else \
                 GL_RGB if nrComponents == 3 else \
                 GL_RGBA

        internalFormat = (GL_RED if nrComponents == 1 else \
                 GL_RGB if nrComponents == 3 else \
                 GL_RGBA)\
                 if gammaCorrection else \
                 (GL_RED if nrComponents == 1 else \
                 GL_SRGB if nrComponents == 3 else \
                 GL_SRGB_ALPHA)

        glBindTexture(GL_TEXTURE_2D, textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, img.width, img.height, 0, dataFormat, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        img.close()

    except:

        print("Texture failed to load at path: " + path)

    return textureID


main()
