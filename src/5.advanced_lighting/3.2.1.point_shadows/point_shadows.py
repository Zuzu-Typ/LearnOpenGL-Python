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
shadows = True
shadowsKeyPressed = False

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
    glEnable(GL_CULL_FACE)

    # build and compile shaders
    # -------------------------
    shader = Shader("3.2.1.point_shadows.vs", "3.2.1.point_shadows.fs")
    simpleDepthShader = Shader("3.2.1.point_shadows_depth.vs", "3.2.1.point_shadows_depth.fs", "3.2.1.point_shadows_depth.gs")
    # load textures
    # -------------
    woodTexture = loadTexture("wood.png")

    # configure depth map FBO
    # -----------------------
    SHADOW_WIDTH = 1024
    SHADOW_HEIGHT = 1024
    depthMapFBO = glGenFramebuffers(1)
    # create depth cubemap texture
    depthCubemap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, depthCubemap)
    for i in range(6):
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    # attach depth texture as FBO's depth buffer
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depthCubemap, 0)
    glDrawBuffer(GL_NONE)
    glReadBuffer(GL_NONE)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)


    # shader configuration
    # --------------------
    shader.use()
    shader.setInt("diffuseTexture", 0)
    shader.setInt("depthMap", 1)

    # lighting info
    # -------------
    lightPos = glm.vec3(0.0, 0.0, 0.0)
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

        # move light position over time
        lightPos.z = glm.sin(glfwGetTime() * 0.5) * 3.0

        # render
        # ------
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 0. create depth cubemap transformation matrices
        # -----------------------------------------------
        near_plane = 1.0
        far_plane  = 25.0
        shadowProj = glm.perspective(glm.radians(90.0), SHADOW_WIDTH / SHADOW_HEIGHT, near_plane, far_plane)
        shadowTransforms = []
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3( 1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3(-1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3( 0.0,  1.0,  0.0), glm.vec3(0.0,  0.0,  1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3( 0.0, -1.0,  0.0), glm.vec3(0.0,  0.0, -1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3( 0.0,  0.0,  1.0), glm.vec3(0.0, -1.0,  0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(lightPos, lightPos + glm.vec3( 0.0,  0.0, -1.0), glm.vec3(0.0, -1.0,  0.0)))

        # 1. render scene to depth cubemap
        # --------------------------------
        glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
        glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)
        simpleDepthShader.use()
        for i in range(6):
            simpleDepthShader.setMat4("shadowMatrices[" + str(i) + "]", shadowTransforms[i])
        simpleDepthShader.setFloat("far_plane", far_plane)
        simpleDepthShader.setVec3("lightPos", lightPos)
        renderScene(simpleDepthShader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # 2. render scene as normal 
        # -------------------------
        glViewport(0, 0, SCR_WIDTH, SCR_HEIGHT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shader.use()
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        shader.setMat4("projection", projection)
        shader.setMat4("view", view)
        # set lighting uniforms
        shader.setVec3("lightPos", lightPos)
        shader.setVec3("viewPos", camera.Position)
        shader.setInt("shadows", shadows) # enable/disable shadows by pressing 'SPACE'
        shader.setFloat("far_plane", far_plane)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, woodTexture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, depthCubemap)
        renderScene(shader)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
    return 0

# renders the 3D scene
# --------------------
def renderScene(shader : Shader) -> None:

    # room cube
    model = glm.mat4(1.0)
    model = glm.scale(model, glm.vec3(5.0))
    shader.setMat4("model", model)
    glDisable(GL_CULL_FACE) # note that we disable culling here since we render 'inside' the cube instead of the usual 'outside' which throws off the normal culling methods.
    shader.setInt("reverse_normals", 1) # A small little hack to invert normals when drawing cube from the inside so lighting still works.
    renderCube()
    shader.setInt("reverse_normals", 0) # and of course disable it
    glEnable(GL_CULL_FACE)
    # cubes
    model = glm.mat4(1.0)
    model = glm.translate(model, glm.vec3(4.0, -3.5, 0.0))
    model = glm.scale(model, glm.vec3(0.5))
    shader.setMat4("model", model)
    renderCube()
    model = glm.mat4(1.0)
    model = glm.translate(model, glm.vec3(2.0, 3.0, 1.0))
    model = glm.scale(model, glm.vec3(0.75))
    shader.setMat4("model", model)
    renderCube()
    model = glm.mat4(1.0)
    model = glm.translate(model, glm.vec3(-3.0, -1.0, 0.0))
    model = glm.scale(model, glm.vec3(0.5))
    shader.setMat4("model", model)
    renderCube()
    model = glm.mat4(1.0)
    model = glm.translate(model, glm.vec3(-1.5, 1.0, 1.5))
    model = glm.scale(model, glm.vec3(0.5))
    shader.setMat4("model", model)
    renderCube()
    model = glm.mat4(1.0)
    model = glm.translate(model, glm.vec3(-1.5, 2.0, -3.0))
    model = glm.rotate(model, glm.radians(60.0), glm.normalize(glm.vec3(1.0, 0.0, 1.0)))
    model = glm.scale(model, glm.vec3(0.75))
    shader.setMat4("model", model)
    renderCube()

# renderCube() renders a 1x1 3D cube in NDC.
# -------------------------------------------------
cubeVAO = 0
cubeVBO = 0
def renderCube() -> None:
    global cubeVAO, cubeVBO

    # initialize (if necessary)
    if (cubeVAO == 0):

        vertices = glm.array(glm.float32,
            # back face
            -1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0, # bottom-left
             1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0, # top-right
             1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 0.0, # bottom-right         
             1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0, # top-right
            -1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0, # bottom-left
            -1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 1.0, # top-left
            # front face
            -1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0, # bottom-left
             1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 0.0, # bottom-right
             1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0, # top-right
             1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0, # top-right
            -1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 1.0, # top-left
            -1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0, # bottom-left
            # left face
            -1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0, # top-right
            -1.0,  1.0, -1.0, -1.0,  0.0,  0.0, 1.0, 1.0, # top-left
            -1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0, # bottom-left
            -1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0, # bottom-left
            -1.0, -1.0,  1.0, -1.0,  0.0,  0.0, 0.0, 0.0, # bottom-right
            -1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0, # top-right
            # right face
             1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0, # top-left
             1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0, # bottom-right
             1.0,  1.0, -1.0,  1.0,  0.0,  0.0, 1.0, 1.0, # top-right         
             1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0, # bottom-right
             1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0, # top-left
             1.0, -1.0,  1.0,  1.0,  0.0,  0.0, 0.0, 0.0, # bottom-left     
            # bottom face
            -1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0, # top-right
             1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 1.0, 1.0, # top-left
             1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0, # bottom-left
             1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0, # bottom-left
            -1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 0.0, 0.0, # bottom-right
            -1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0, # top-right
            # top face
            -1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0, # top-left
             1.0,  1.0 , 1.0,  0.0,  1.0,  0.0, 1.0, 0.0, # bottom-right
             1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 1.0, 1.0, # top-right     
             1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 1.0, 0.0, # bottom-right
            -1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0, # top-left
            -1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 0.0, 0.0)  # bottom-left        

        cubeVAO = glGenVertexArrays(1)
        cubeVBO = glGenBuffers(1)
        # fill buffer
        glBindBuffer(GL_ARRAY_BUFFER, cubeVBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)
        # link vertex attributes
        glBindVertexArray(cubeVAO)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    # render Cube
    glBindVertexArray(cubeVAO)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glBindVertexArray(0)

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:
    global shadows, shadowsKeyPressed

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

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS and not shadowsKeyPressed):

        shadows = not shadows
        shadowsKeyPressed = True

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_RELEASE):

        shadowsKeyPressed = False

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
