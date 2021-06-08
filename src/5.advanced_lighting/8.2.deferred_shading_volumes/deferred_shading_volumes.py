try:
    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow
    
    import glm

except ImportError:
    import requirements

    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow
    
    import glm
    
from shader import Shader
from camera import Camera, Camera_Movement
from model import Model

import platform, ctypes, os

# the relative path where the models are located
MODEL_RESOURCE_PATH = "../../../resources/objects"

# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600

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
    shaderGeometryPass = Shader("8.2.g_buffer.vs", "8.2.g_buffer.fs")
    shaderLightingPass = Shader("8.2.deferred_shading.vs", "8.2.deferred_shading.fs")
    shaderLightBox = Shader("8.2.deferred_light_box.vs", "8.2.deferred_light_box.fs")
    # load models
    # -----------
    backpack = Model(os.path.join(MODEL_RESOURCE_PATH, "backpack/backpack.obj"))
    objectPositions = []
    objectPositions.append(glm.vec3(-3.0, -0.5, -3.0))
    objectPositions.append(glm.vec3( 0.0, -0.5, -3.0))
    objectPositions.append(glm.vec3( 3.0, -0.5, -3.0))
    objectPositions.append(glm.vec3(-3.0, -0.5,  0.0))
    objectPositions.append(glm.vec3( 0.0, -0.5,  0.0))
    objectPositions.append(glm.vec3( 3.0, -0.5,  0.0))
    objectPositions.append(glm.vec3(-3.0, -0.5,  3.0))
    objectPositions.append(glm.vec3( 0.0, -0.5,  3.0))
    objectPositions.append(glm.vec3( 3.0, -0.5,  3.0))


    # configure g-buffer framebuffer
    # ------------------------------
    gBuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, gBuffer)
    # position color buffer
    gPosition = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, gPosition)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, gPosition, 0)
    # normal color buffer
    gNormal = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, gNormal)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, gNormal, 0)
    # color + specular color buffer
    gAlbedoSpec = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, gAlbedoSpec)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, gAlbedoSpec, 0)
    # tell OpenGL which color attachments we'll use (of this framebuffer) for rendering 
    attachments = glm.array(glm.uint32, GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2)
    glDrawBuffers(3, attachments.ptr)
    # create and attach depth buffer (renderbuffer)
    rboDepth = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rboDepth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, SCR_WIDTH, SCR_HEIGHT)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rboDepth)
    # finally check if framebuffer is complete
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
        print("Framebuffer not complete!")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # lighting info
    # -------------
    NR_LIGHTS = 32
    lightPositions = []
    lightColors = []
    glm.setSeed(13)
    for i in range(NR_LIGHTS):

        # calculate slightly random offsets
        xPos = glm.linearRand(-3, 3)
        yPos = glm.linearRand(-4, 2)
        zPos = glm.linearRand(-3, 3)
        lightPositions.append(glm.vec3(xPos, yPos, zPos))
        # also calculate random color
        rColor = glm.linearRand(0.5, 1) # between 0.5 and 1.0
        gColor = glm.linearRand(0.5, 1) # between 0.5 and 1.0
        bColor = glm.linearRand(0.5, 1) # between 0.5 and 1.0
        lightColors.append(glm.vec3(rColor, gColor, bColor))

    # shader configuration
    # --------------------
    shaderLightingPass.use()
    shaderLightingPass.setInt("gPosition", 0)
    shaderLightingPass.setInt("gNormal", 1)
    shaderLightingPass.setInt("gAlbedoSpec", 2)

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

        # 1. geometry pass: render scene's geometry/color data into gbuffer
        # -----------------------------------------------------------------
        glBindFramebuffer(GL_FRAMEBUFFER, gBuffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        model = glm.mat4(1.0)
        shaderGeometryPass.use()
        shaderGeometryPass.setMat4("projection", projection)
        shaderGeometryPass.setMat4("view", view)
        for i in range(len(objectPositions)):
            model = glm.mat4(1.0)
            model = glm.translate(model, objectPositions[i])
            model = glm.scale(model, glm.vec3(0.25))
            shaderGeometryPass.setMat4("model", model)
            backpack.Draw(shaderGeometryPass)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # 2. lighting pass: calculate lighting by iterating over a screen filled quad pixel-by-pixel using the gbuffer's content.
        # -----------------------------------------------------------------------------------------------------------------------
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shaderLightingPass.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gPosition)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, gNormal)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, gAlbedoSpec)
        # send light relevant uniforms
        for i in range(len(lightPositions)):

            shaderLightingPass.setVec3("lights[" + str(i) + "].Position", lightPositions[i])
            shaderLightingPass.setVec3("lights[" + str(i) + "].Color", lightColors[i])
            # update attenuation parameters and calculate radius
            constant = 1.0 # note that we don't send this to the shader, we assume it is always 1.0 (in our case)
            linear = 0.7
            quadratic = 1.8
            shaderLightingPass.setFloat("lights[" + str(i) + "].Linear", linear)
            shaderLightingPass.setFloat("lights[" + str(i) + "].Quadratic", quadratic)
            # then calculate radius of light volume/sphere
            maxBrightness = max(max(lightColors[i].r, lightColors[i].g), lightColors[i].b)
            radius = (-linear + glm.sqrt(linear * linear - 4 * quadratic * (constant - (256.0 / 5.0) * maxBrightness))) / (2.0 * quadratic)
            shaderLightingPass.setFloat("lights[" + str(i) + "].Radius", radius)

        shaderLightingPass.setVec3("viewPos", camera.Position)
        # finally render quad
        renderQuad()

        # 2.5. copy content of geometry's depth buffer to default framebuffer's depth buffer
        # ----------------------------------------------------------------------------------
        glBindFramebuffer(GL_READ_FRAMEBUFFER, gBuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0) # write to default framebuffer
        # blit to default framebuffer. Note that this may or may not work as the internal formats of both the FBO and default framebuffer have to match.
        # the internal formats are implementation defined. This works on all of my systems, but if it doesn't on yours you'll likely have to write to the 		
        # depth buffer in another shader stage (or somehow see to match the default framebuffer's internal format with the FBO's internal format).
        glBlitFramebuffer(0, 0, SCR_WIDTH, SCR_HEIGHT, 0, 0, SCR_WIDTH, SCR_HEIGHT, GL_DEPTH_BUFFER_BIT, GL_NEAREST)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # 3. render lights on top of scene
        # --------------------------------
        shaderLightBox.use()
        shaderLightBox.setMat4("projection", projection)
        shaderLightBox.setMat4("view", view)
        for i in range(len(lightPositions)):

            model = glm.mat4(1.0)
            model = glm.translate(model, lightPositions[i])
            model = glm.scale(model, glm.vec3(0.125))
            shaderLightBox.setMat4("model", model)
            shaderLightBox.setVec3("lightColor", lightColors[i])
            renderCube()

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
