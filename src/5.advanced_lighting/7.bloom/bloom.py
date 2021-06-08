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
bloom = True
bloomKeyPressed = False
exposure = 1.0

# camera
camera = Camera(glm.vec3(0.0, 0.0, 5.0))
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
    shader = Shader("7.bloom.vs", "7.bloom.fs")
    shaderLight = Shader("7.bloom.vs", "7.light_box.fs")
    shaderBlur = Shader("7.blur.vs", "7.blur.fs")
    shaderBloomFinal = Shader("7.bloom_final.vs", "7.bloom_final.fs")
    # load textures
    # -------------
    woodTexture      = loadTexture("wood.png", True) # note that we're loading the texture as an SRGB texture
    containerTexture = loadTexture("container2.png", True) # note that we're loading the texture as an SRGB texture

    # configure (floating point) framebuffers
    # ---------------------------------------
    hdrFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, hdrFBO)
    # create 2 floating point color buffers (1 for normal rendering, other for brightness threshold values)
    colorBuffers = glGenTextures(2)
    for i in range(2):

        glBindTexture(GL_TEXTURE_2D, colorBuffers[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)  # we clamp to the edge as the blur filter would otherwise sample repeated texture valuesnot 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        # attach texture to framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D, colorBuffers[i], 0)

    # create and attach depth buffer (renderbuffer)
    rboDepth = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rboDepth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, SCR_WIDTH, SCR_HEIGHT)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rboDepth)
    # tell OpenGL which color attachments we'll use (of this framebuffer) for rendering 
    attachments = glm.array(glm.uint32, GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1)
    glDrawBuffers(2, attachments.ptr)
    # finally check if framebuffer is complete
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
        print("Framebuffer not complete!")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # ping-pong-framebuffer for blurring
    pingpongFBO = glGenFramebuffers(2)
    pingpongColorbuffers = glGenTextures(2)
    for i in range(2):

        glBindFramebuffer(GL_FRAMEBUFFER, pingpongFBO[i])
        glBindTexture(GL_TEXTURE_2D, pingpongColorbuffers[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # we clamp to the edge as the blur filter would otherwise sample repeated texture valuesnot 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, pingpongColorbuffers[i], 0)
        # also check if framebuffers are complete (no need for depth buffer)
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
            print("Framebuffer not complete!")

    # lighting info
    # -------------
    # positions
    lightPositions = []
    lightPositions.append(glm.vec3( 0.0, 0.5,  1.5))
    lightPositions.append(glm.vec3(-4.0, 0.5, -3.0))
    lightPositions.append(glm.vec3( 3.0, 0.5,  1.0))
    lightPositions.append(glm.vec3(-.8,  2.4, -1.0))
    # colors
    lightColors = []
    lightColors.append(glm.vec3(5.0,   5.0,  5.0))
    lightColors.append(glm.vec3(10.0,  0.0,  0.0))
    lightColors.append(glm.vec3(0.0,   0.0,  15.0))
    lightColors.append(glm.vec3(0.0,   5.0,  0.0))


    # shader configuration
    # --------------------
    shader.use()
    shader.setInt("diffuseTexture", 0)
    shaderBlur.use()
    shaderBlur.setInt("image", 0)
    shaderBloomFinal.use()
    shaderBloomFinal.setInt("scene", 0)
    shaderBloomFinal.setInt("bloomBlur", 1)

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
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 1. render scene into floating point framebuffer
        # -----------------------------------------------
        glBindFramebuffer(GL_FRAMEBUFFER, hdrFBO)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        model = glm.mat4(1.0)
        shader.use()
        shader.setMat4("projection", projection)
        shader.setMat4("view", view)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, woodTexture)
        # set lighting uniforms
        for i in range(len(lightPositions)):

            shader.setVec3("lights[" + str(i) + "].Position", lightPositions[i])
            shader.setVec3("lights[" + str(i) + "].Color", lightColors[i])

        shader.setVec3("viewPos", camera.Position)
        # create one large cube that acts as the floor
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, -1.0, 0.0))
        model = glm.scale(model, glm.vec3(12.5, 0.5, 12.5))
        shader.setMat4("model", model)
        renderCube()
        # then create multiple cubes as the scenery
        glBindTexture(GL_TEXTURE_2D, containerTexture)
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, 1.5, 0.0))
        model = glm.scale(model, glm.vec3(0.5))
        shader.setMat4("model", model)
        renderCube()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(2.0, 0.0, 1.0))
        model = glm.scale(model, glm.vec3(0.5))
        shader.setMat4("model", model)
        renderCube()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(-1.0, -1.0, 2.0))
        model = glm.rotate(model, glm.radians(60.0), glm.normalize(glm.vec3(1.0, 0.0, 1.0)))
        shader.setMat4("model", model)
        renderCube()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, 2.7, 4.0))
        model = glm.rotate(model, glm.radians(23.0), glm.normalize(glm.vec3(1.0, 0.0, 1.0)))
        model = glm.scale(model, glm.vec3(1.25))
        shader.setMat4("model", model)
        renderCube()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(-2.0, 1.0, -3.0))
        model = glm.rotate(model, glm.radians(124.0), glm.normalize(glm.vec3(1.0, 0.0, 1.0)))
        shader.setMat4("model", model)
        renderCube()

        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(-3.0, 0.0, 0.0))
        model = glm.scale(model, glm.vec3(0.5))
        shader.setMat4("model", model)
        renderCube()

        # finally show all the light sources as bright cubes
        shaderLight.use()
        shaderLight.setMat4("projection", projection)
        shaderLight.setMat4("view", view)

        for i in range(len(lightPositions)):

            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(lightPositions[i]))
            model = glm.scale(model, glm.vec3(0.25))
            shaderLight.setMat4("model", model)
            shaderLight.setVec3("lightColor", lightColors[i])
            renderCube()

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # 2. blur bright fragments with two-pass Gaussian Blur 
        # --------------------------------------------------
        horizontal = True
        first_iteration = True
        amount = 10
        shaderBlur.use()
        for i in range(amount):

            glBindFramebuffer(GL_FRAMEBUFFER, pingpongFBO[int(horizontal)])
            shaderBlur.setInt("horizontal", horizontal)
            glBindTexture(GL_TEXTURE_2D, colorBuffers[1] if first_iteration else pingpongColorbuffers[int(not horizontal)])  # bind texture of other framebuffer (or scene if first iteration)
            renderQuad()
            horizontal = not horizontal
            if (first_iteration):
                first_iteration = False

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # 3. now render floating point color buffer to 2D quad and tonemap HDR colors to default framebuffer's (clamped) color range
        # --------------------------------------------------------------------------------------------------------------------------
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shaderBloomFinal.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, colorBuffers[0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, pingpongColorbuffers[int(not horizontal)])
        shaderBloomFinal.setInt("bloom", bloom)
        shaderBloomFinal.setFloat("exposure", exposure)
        renderQuad()

        print("bloom: " + ("on" if bloom else "off") + "| exposure: " + str(exposure))

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()
    return 0

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
            -1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 0.0, 0.0) # bottom-left        

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

# renderQuad() renders a 1x1 XY quad in NDC
# -----------------------------------------
quadVAO = 0
def renderQuad() -> None:
    global quadVAO, quadVBO

    if (quadVAO == 0):

        quadVertices = glm.array(glm.float32,
            # positions        # texture Coords
            -1.0,  1.0, 0.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0, 0.0,
             1.0,  1.0, 0.0, 1.0, 1.0,
             1.0, -1.0, 0.0, 1.0, 0.0)

        # setup plane VAO
        quadVAO = glGenVertexArrays(1)
        quadVBO = glGenBuffers(1)
        glBindVertexArray(quadVAO)
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
        glBufferData(GL_ARRAY_BUFFER, quadVertices.nbytes, quadVertices.ptr, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))

    glBindVertexArray(quadVAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glBindVertexArray(0)

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:
    global deltaTime, bloom, bloomKeyPressed, exposure

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

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS and not bloomKeyPressed):

        bloom = not bloom
        bloomKeyPressed = True

    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_RELEASE):

        bloomKeyPressed = False

    if (glfwGetKey(window, GLFW_KEY_Q) == GLFW_PRESS):

        if (exposure > 0.0):
            exposure -= 0.001
        else:
            exposure = 0.0

    elif (glfwGetKey(window, GLFW_KEY_E) == GLFW_PRESS):

        exposure += 0.001


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
