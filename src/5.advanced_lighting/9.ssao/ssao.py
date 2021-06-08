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

def lerp(a : float, b : float, f : float) -> float:
    return a + f * (b - a)

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
    shaderGeometryPass = Shader("9.ssao_geometry.vs", "9.ssao_geometry.fs")
    shaderLightingPass = Shader("9.ssao.vs", "9.ssao_lighting.fs")
    shaderSSAO = Shader("9.ssao.vs", "9.ssao.fs")
    shaderSSAOBlur = Shader("9.ssao.vs", "9.ssao_blur.fs")
    # load models
    # -----------
    backpack = Model(os.path.join(MODEL_RESOURCE_PATH, "backpack/backpack.obj"))
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
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, gPosition, 0)
    # normal color buffer
    gNormal = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, gNormal)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, gNormal, 0)
    # color + specular color buffer
    gAlbedo = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, gAlbedo)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, SCR_WIDTH, SCR_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, gAlbedo, 0)
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

    # also create framebuffer to hold SSAO processing stage 
    # -----------------------------------------------------
    ssaoFBO = glGenFramebuffers(1)
    ssaoBlurFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, ssaoFBO)
    # SSAO color buffer
    ssaoColorBuffer = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ssaoColorBuffer)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, SCR_WIDTH, SCR_HEIGHT, 0, GL_RED, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, ssaoColorBuffer, 0)
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
        print("SSAO Framebuffer not complete!")
    # and blur stage
    glBindFramebuffer(GL_FRAMEBUFFER, ssaoBlurFBO)
    ssaoColorBufferBlur = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ssaoColorBufferBlur)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, SCR_WIDTH, SCR_HEIGHT, 0, GL_RED, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, ssaoColorBufferBlur, 0)
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
        print("SSAO Blur Framebuffer not complete!")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # generate sample kernel
    # ----------------------
    ssaoKernel = []
    for i in range(64):

        sample = glm.vec3(glm.linearRand(-1, 1), glm.linearRand(-1, 1), glm.linearRand(0, 1))
        sample = glm.normalize(sample)
        sample *= glm.linearRand(0, 1)
        scale = float(i) / 64.0

        # scale samples s.t. they're more aligned to center of kernel
        scale = lerp(0.1, 1.0, scale * scale)
        sample *= scale
        ssaoKernel.append(sample)

    # generate noise texture
    # ----------------------
    ssaoNoise = []
    for i in range(16):
        noise = glm.vec3(glm.linearRand(-1, 1), glm.linearRand(-1, 1), 0.0) # rotate around z-axis (in tangent space)
        ssaoNoise.append(noise)

    ssaoNoiseArr = glm.array(ssaoNoise)

    noiseTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, noiseTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 4, 4, 0, GL_RGB, GL_FLOAT, ssaoNoiseArr.ptr)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # lighting info
    # -------------
    lightPos = glm.vec3(2.0, 4.0, -2.0)
    lightColor = glm.vec3(0.2, 0.2, 0.7)

    # shader configuration
    # --------------------
    shaderLightingPass.use()
    shaderLightingPass.setInt("gPosition", 0)
    shaderLightingPass.setInt("gNormal", 1)
    shaderLightingPass.setInt("gAlbedo", 2)
    shaderLightingPass.setInt("ssao", 3)
    shaderSSAO.use()
    shaderSSAO.setInt("gPosition", 0)
    shaderSSAO.setInt("gNormal", 1)
    shaderSSAO.setInt("texNoise", 2)
    shaderSSAOBlur.use()
    shaderSSAOBlur.setInt("ssaoInput", 0)

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
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 50.0)
        view = camera.GetViewMatrix()
        model = glm.mat4(1.0)
        shaderGeometryPass.use()
        shaderGeometryPass.setMat4("projection", projection)
        shaderGeometryPass.setMat4("view", view)
        # room cube
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, 7.0, 0.0))
        model = glm.scale(model, glm.vec3(7.5, 7.5, 7.5))
        shaderGeometryPass.setMat4("model", model)
        shaderGeometryPass.setInt("invertedNormals", 1) # invert normals as we're inside the cube
        renderCube()
        shaderGeometryPass.setInt("invertedNormals", 0) 
        # backpack model on the floor
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.0, 0.5, 0.0))
        model = glm.rotate(model, glm.radians(-90.0), glm.vec3(1.0, 0.0, 0.0))
        model = glm.scale(model, glm.vec3(1.0))
        shaderGeometryPass.setMat4("model", model)
        backpack.Draw(shaderGeometryPass)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


        # 2. generate SSAO texture
        # ------------------------
        glBindFramebuffer(GL_FRAMEBUFFER, ssaoFBO)
        glClear(GL_COLOR_BUFFER_BIT)
        shaderSSAO.use()
        # Send kernel + rotation 
        for i in range(64):
            shaderSSAO.setVec3("samples[" + str(i) + "]", ssaoKernel[i])
        shaderSSAO.setMat4("projection", projection)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gPosition)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, gNormal)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, noiseTexture)
        renderQuad()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


        # 3. blur SSAO texture to remove noise
        # ------------------------------------
        glBindFramebuffer(GL_FRAMEBUFFER, ssaoBlurFBO)
        glClear(GL_COLOR_BUFFER_BIT)
        shaderSSAOBlur.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, ssaoColorBuffer)
        renderQuad()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


        # 4. lighting pass: traditional deferred Blinn-Phong lighting with added screen-space ambient occlusion
        # -----------------------------------------------------------------------------------------------------
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        shaderLightingPass.use()
        # send light relevant uniforms
        lightPosView = glm.vec3(camera.GetViewMatrix() * glm.vec4(lightPos, 1.0))
        shaderLightingPass.setVec3("light.Position", lightPosView)
        shaderLightingPass.setVec3("light.Color", lightColor)
        # Update attenuation parameters
        linear    = 0.09
        quadratic = 0.032
        shaderLightingPass.setFloat("light.Linear", linear)
        shaderLightingPass.setFloat("light.Quadratic", quadratic)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gPosition)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, gNormal)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, gAlbedo)
        glActiveTexture(GL_TEXTURE3) # add extra SSAO texture to lighting pass
        glBindTexture(GL_TEXTURE_2D, ssaoColorBufferBlur)
        renderQuad()


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
