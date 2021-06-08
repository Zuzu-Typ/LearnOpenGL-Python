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

    # build and compile shaders
    # -------------------------
    shader = Shader("4.normal_mapping.vs", "4.normal_mapping.fs")
    # load textures
    # -------------
    diffuseMap = loadTexture("brickwall.jpg")
    normalMap  = loadTexture("brickwall_normal.jpg")

    # shader configuration
    # --------------------
    shader.use()
    shader.setInt("diffuseMap", 0)
    shader.setInt("normalMap", 1)

    # lighting info
    # -------------
    lightPos = glm.vec3(0.5, 1.0, 0.3)
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

        # configure view/projection matrices
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        shader.use()
        shader.setMat4("projection", projection)
        shader.setMat4("view", view)
        # render normal-mapped quad
        model = glm.mat4(1.0)
        model = glm.rotate(model, glm.radians(glfwGetTime() * -10.0), glm.normalize(glm.vec3(1.0, 0.0, 1.0))) # rotate the quad to show normal mapping from multiple directions
        shader.setMat4("model", model)
        shader.setVec3("viewPos", camera.Position)
        shader.setVec3("lightPos", lightPos)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, diffuseMap)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, normalMap)
        renderQuad()

        # render light source (simply re-renders a smaller plane at the light's position for debugging/visualization)
        model = glm.mat4(1.0)
        model = glm.translate(model, lightPos)
        model = glm.scale(model, glm.vec3(0.1))
        shader.setMat4("model", model)
        renderQuad()

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
    return 0

# renders a 1x1 quad in NDC with manually calculated tangent vectors
# ------------------------------------------------------------------
quadVAO = 0
def renderQuad() -> None:
    global quadVAO, quadVBO

    if (quadVAO == 0):

        # positions
        pos1 = glm.vec3(-1.0,  1.0, 0.0)
        pos2 = glm.vec3(-1.0, -1.0, 0.0)
        pos3 = glm.vec3( 1.0, -1.0, 0.0)
        pos4 = glm.vec3( 1.0,  1.0, 0.0)
        # texture coordinates
        uv1 = glm.vec2(0.0, 1.0)
        uv2 = glm.vec2(0.0, 0.0)
        uv3 = glm.vec2(1.0, 0.0)
        uv4 = glm.vec2(1.0, 1.0)
        # normal vector
        nm = glm.vec3(0.0, 0.0, 1.0)
        # calculate tangent/bitangent vectors of both triangles
        tangent1 = glm.vec3()
        tangent2 = glm.vec3()
        bitangent1 = glm.vec3()
        bitangent2 = glm.vec3()
        
        # triangle 1
        # ----------
        edge1 = pos2 - pos1
        edge2 = pos3 - pos1
        deltaUV1 = uv2 - uv1
        deltaUV2 = uv3 - uv1

        f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)

        tangent1.x = f * (deltaUV2.y * edge1.x - deltaUV1.y * edge2.x)
        tangent1.y = f * (deltaUV2.y * edge1.y - deltaUV1.y * edge2.y)
        tangent1.z = f * (deltaUV2.y * edge1.z - deltaUV1.y * edge2.z)

        bitangent1.x = f * (-deltaUV2.x * edge1.x + deltaUV1.x * edge2.x)
        bitangent1.y = f * (-deltaUV2.x * edge1.y + deltaUV1.x * edge2.y)
        bitangent1.z = f * (-deltaUV2.x * edge1.z + deltaUV1.x * edge2.z)

        # triangle 2
        # ----------
        edge1 = pos3 - pos1
        edge2 = pos4 - pos1
        deltaUV1 = uv3 - uv1
        deltaUV2 = uv4 - uv1

        f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)

        tangent2.x = f * (deltaUV2.y * edge1.x - deltaUV1.y * edge2.x)
        tangent2.y = f * (deltaUV2.y * edge1.y - deltaUV1.y * edge2.y)
        tangent2.z = f * (deltaUV2.y * edge1.z - deltaUV1.y * edge2.z)


        bitangent2.x = f * (-deltaUV2.x * edge1.x + deltaUV1.x * edge2.x)
        bitangent2.y = f * (-deltaUV2.x * edge1.y + deltaUV1.x * edge2.y)
        bitangent2.z = f * (-deltaUV2.x * edge1.z + deltaUV1.x * edge2.z)


        quadVertices = glm.array(glm.float32,
            # positions            # normal         # texcoords  # tangent                          # bitangent
            pos1.x, pos1.y, pos1.z, nm.x, nm.y, nm.z, uv1.x, uv1.y, tangent1.x, tangent1.y, tangent1.z, bitangent1.x, bitangent1.y, bitangent1.z,
            pos2.x, pos2.y, pos2.z, nm.x, nm.y, nm.z, uv2.x, uv2.y, tangent1.x, tangent1.y, tangent1.z, bitangent1.x, bitangent1.y, bitangent1.z,
            pos3.x, pos3.y, pos3.z, nm.x, nm.y, nm.z, uv3.x, uv3.y, tangent1.x, tangent1.y, tangent1.z, bitangent1.x, bitangent1.y, bitangent1.z,

            pos1.x, pos1.y, pos1.z, nm.x, nm.y, nm.z, uv1.x, uv1.y, tangent2.x, tangent2.y, tangent2.z, bitangent2.x, bitangent2.y, bitangent2.z,
            pos3.x, pos3.y, pos3.z, nm.x, nm.y, nm.z, uv3.x, uv3.y, tangent2.x, tangent2.y, tangent2.z, bitangent2.x, bitangent2.y, bitangent2.z,
            pos4.x, pos4.y, pos4.z, nm.x, nm.y, nm.z, uv4.x, uv4.y, tangent2.x, tangent2.y, tangent2.z, bitangent2.x, bitangent2.y, bitangent2.z)

        # configure plane VAO
        quadVAO = glGenVertexArrays(1)
        quadVBO = glGenBuffers(1)
        glBindVertexArray(quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
        glBufferData(GL_ARRAY_BUFFER, quadVertices.nbytes, quadVertices.ptr, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 14 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 14 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 14 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 14 * glm.sizeof(glm.float32), ctypes.c_void_p(8 * glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 14 * glm.sizeof(glm.float32), ctypes.c_void_p(11 * glm.sizeof(glm.float32)))

    glBindVertexArray(quadVAO)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindVertexArray(0)

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

# utility function for loading a 2D texture from file
# ---------------------------------------------------
def loadTexture(path : str) -> int:
    textureID = glGenTextures(1)

    try:
        img = LOAD_IMAGE(path)
        
        nrComponents = len(img.getbands())

        format = GL_RED if nrComponents == 1 else \
                 GL_RGB if nrComponents == 3 else \
                 GL_RGBA 

        glBindTexture(GL_TEXTURE_2D, textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, format, img.width, img.height, 0, format, GL_UNSIGNED_BYTE, img.tobytes())
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
