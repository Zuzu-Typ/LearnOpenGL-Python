try:
    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow

    import imageio

    import numpy
    
    import glm

except ImportError:
    import requirements

    from OpenGL.GL import *
    from glfw.GLFW import *
    
    from glfw import _GLFWwindow as GLFWwindow

    import imageio

    import numpy
    
    import glm

from shader import Shader
from camera import Camera, Camera_Movement

import platform, ctypes, os

imageio.plugins.freeimage.download()

# the relative path where the textures are located
IMAGE_RESOURCE_PATH = "../../../resources/textures/"

# function that loads an HDR image using ImageIO
LOAD_HDR_IMAGE = lambda name: imageio.imread(os.path.join(IMAGE_RESOURCE_PATH, name), format="HDR-FI")

# settings
SCR_WIDTH = 1280
SCR_HEIGHT = 720

# camera
camera = Camera(glm.vec3(0.0, 0.0, 3.0))
lastX = 800.0 / 2.0
lastY = 600.0 / 2.0
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
    glfwWindowHint(GLFW_SAMPLES, 4)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

    if (platform.system() == "Darwin"): # APPLE
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    # glfw window creation
    # --------------------
    window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", None, None)
    glfwMakeContextCurrent(window)
    if (window == None):

        print("Failed to create GLFW window")
        glfwTerminate()
        return -1

    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)
    glfwSetCursorPosCallback(window, mouse_callback)
    glfwSetScrollCallback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)

    # configure global opengl state
    # -----------------------------
    glEnable(GL_DEPTH_TEST)
    # set depth function to less than AND equal for skybox depth trick.
    glDepthFunc(GL_LEQUAL)
    # enable seamless cubemap sampling for lower mip levels in the pre-filter map.
    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)

    # build and compile shaders
    # -------------------------
    pbrShader = Shader("2.2.1.pbr.vs", "2.2.1.pbr.fs")
    equirectangularToCubemapShader = Shader("2.2.1.cubemap.vs", "2.2.1.equirectangular_to_cubemap.fs")
    irradianceShader = Shader("2.2.1.cubemap.vs", "2.2.1.irradiance_convolution.fs")
    prefilterShader = Shader("2.2.1.cubemap.vs", "2.2.1.prefilter.fs")
    brdfShader = Shader("2.2.1.brdf.vs", "2.2.1.brdf.fs")
    backgroundShader = Shader("2.2.1.background.vs", "2.2.1.background.fs")
    pbrShader.use()
    pbrShader.setInt("irradianceMap", 0)
    pbrShader.setInt("prefilterMap", 1)
    pbrShader.setInt("brdfLUT", 2)
    pbrShader.setVec3("albedo", 0.5, 0.0, 0.0)
    pbrShader.setFloat("ao", 1.0)

    backgroundShader.use()
    backgroundShader.setInt("environmentMap", 0)

  
    # lights
    # ------
    lightPositions = glm.array(
        glm.vec3(-10.0,  10.0, 10.0),
        glm.vec3( 10.0,  10.0, 10.0),
        glm.vec3(-10.0, -10.0, 10.0),
        glm.vec3( 10.0, -10.0, 10.0),
    )

    lightColors = glm.array(
        glm.vec3(300.0, 300.0, 300.0),
        glm.vec3(300.0, 300.0, 300.0),
        glm.vec3(300.0, 300.0, 300.0),
        glm.vec3(300.0, 300.0, 300.0)
    )

    nrRows = 7
    nrColumns = 7
    spacing = 2.5

    # pbr: setup framebuffer
    # ----------------------
    captureFBO = glGenFramebuffers(1)
    captureRBO = glGenRenderbuffers(1)

    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    glBindRenderbuffer(GL_RENDERBUFFER, captureRBO)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 512, 512)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, captureRBO)

    # pbr: load the HDR environment map
    # ---------------------------------
    hdrTexture = 0
    try:
        img = LOAD_HDR_IMAGE("hdr/newport_loft.hdr")

        height, width, nrComponents = img.shape

        hdrTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, hdrTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_FLOAT, numpy.flip(img, axis=0)) # note how we specify the texture's data value to be float

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    except:
        print("Failed to load HDR image.")
        return

    # pbr: setup cubemap to render to and attach to framebuffer
    # ---------------------------------------------------------
    envCubemap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap)
    for i in range(6):

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB16F, 512, 512, 0, GL_RGB, GL_FLOAT, None)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR) # enable pre-filter mipmap sampling (combatting visible dots artifact)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # pbr: set up projection and view matrices for capturing data onto the 6 cubemap face directions
    # ----------------------------------------------------------------------------------------------
    captureProjection = glm.perspective(glm.radians(90.0), 1.0, 0.1, 10.0)
    captureViews = glm.array(

        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)),
        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(-1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)),
        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0,  1.0,  0.0), glm.vec3(0.0,  0.0,  1.0)),
        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, -1.0,  0.0), glm.vec3(0.0,  0.0, -1.0)),
        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0,  0.0,  1.0), glm.vec3(0.0, -1.0,  0.0)),
        glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0,  0.0, -1.0), glm.vec3(0.0, -1.0,  0.0))
    )

    # pbr: convert HDR equirectangular environment map to cubemap equivalent
    # ----------------------------------------------------------------------
    equirectangularToCubemapShader.use()
    equirectangularToCubemapShader.setInt("equirectangularMap", 0)
    equirectangularToCubemapShader.setMat4("projection", captureProjection)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, hdrTexture)

    glViewport(0, 0, 512, 512) # don't forget to configure the viewport to the capture dimensions.
    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    for i in range(6):

        equirectangularToCubemapShader.setMat4("view", captureViews[i])
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, envCubemap, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        renderCube()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # then let OpenGL generate mipmaps from first mip face (combatting visible dots artifact)
    glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap)
    glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

    # pbr: create an irradiance cubemap, and re-scale capture FBO to irradiance scale.
    # --------------------------------------------------------------------------------
    irradianceMap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, irradianceMap)
    for i in range(6):

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB16F, 32, 32, 0, GL_RGB, GL_FLOAT, None)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    glBindRenderbuffer(GL_RENDERBUFFER, captureRBO)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 32, 32)

    # pbr: solve diffuse integral by convolution to create an irradiance (cube)map.
    # -----------------------------------------------------------------------------
    irradianceShader.use()
    irradianceShader.setInt("environmentMap", 0)
    irradianceShader.setMat4("projection", captureProjection)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap)

    glViewport(0, 0, 32, 32) # don't forget to configure the viewport to the capture dimensions.
    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    for i in range(6):

        irradianceShader.setMat4("view", captureViews[i])
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, irradianceMap, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        renderCube()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # pbr: create a pre-filter cubemap, and re-scale capture FBO to pre-filter scale.
    # --------------------------------------------------------------------------------
    prefilterMap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, prefilterMap)
    for i in range(6):

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB16F, 128, 128, 0, GL_RGB, GL_FLOAT, None)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR) # be sure to set minification filter to mip_linear 
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # generate mipmaps for the cubemap so OpenGL automatically allocates the required memory.
    glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

    # pbr: run a quasi monte-carlo simulation on the environment lighting to create a prefilter (cube)map.
    # ----------------------------------------------------------------------------------------------------
    prefilterShader.use()
    prefilterShader.setInt("environmentMap", 0)
    prefilterShader.setMat4("projection", captureProjection)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap)

    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    maxMipLevels = 5
    for mip in range(maxMipLevels):

        # reisze framebuffer according to mip-level size.
        mipWidth  = int(128 * pow(0.5, mip))
        mipHeight = int(128 * pow(0.5, mip))
        glBindRenderbuffer(GL_RENDERBUFFER, captureRBO)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, mipWidth, mipHeight)
        glViewport(0, 0, mipWidth, mipHeight)

        roughness = mip / (maxMipLevels - 1)
        prefilterShader.setFloat("roughness", roughness)
        for i in range(6):

            prefilterShader.setMat4("view", captureViews[i])
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, prefilterMap, mip)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            renderCube()


    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # pbr: generate a 2D LUT from the BRDF equations used.
    # ----------------------------------------------------
    brdfLUTTexture = glGenTextures(1)

    # pre-allocate enough memory for the LUT texture.
    glBindTexture(GL_TEXTURE_2D, brdfLUTTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RG16F, 512, 512, 0, GL_RG, GL_FLOAT, None)
    # be sure to set wrapping mode to GL_CLAMP_TO_EDGE
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # then re-configure capture framebuffer object and render screen-space quad with BRDF shader.
    glBindFramebuffer(GL_FRAMEBUFFER, captureFBO)
    glBindRenderbuffer(GL_RENDERBUFFER, captureRBO)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 512, 512)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, brdfLUTTexture, 0)

    glViewport(0, 0, 512, 512)
    brdfShader.use()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    renderQuad()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)


    # initialize static shader uniforms before rendering
    # --------------------------------------------------
    projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
    pbrShader.use()
    pbrShader.setMat4("projection", projection)
    backgroundShader.use()
    backgroundShader.setMat4("projection", projection)

    # then before rendering, configure the viewport to the original framebuffer's screen dimensions
    scrWidth, scrHeight = glfwGetFramebufferSize(window)
    glViewport(0, 0, scrWidth, scrHeight)

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
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # render scene, supplying the convoluted irradiance map to the final shader.
        # ------------------------------------------------------------------------------------------
        pbrShader.use()
        view = camera.GetViewMatrix()
        pbrShader.setMat4("view", view)
        pbrShader.setVec3("camPos", camera.Position)

        # bind pre-computed IBL data
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, irradianceMap)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, prefilterMap)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, brdfLUTTexture)

        # render rows*column number of spheres with varying metallic/roughness values scaled by rows and columns respectively
        model = glm.mat4(1.0)
        for row in range(nrRows):

            pbrShader.setFloat("metallic", row / nrRows)
            for col in range(nrColumns):

                # we clamp the roughness to 0.025 - 1.0 as perfectly smooth surfaces (roughness of 0.0) tend to look a bit off
                # on direct lighting.
                pbrShader.setFloat("roughness", glm.clamp(col / nrColumns, 0.05, 1.0))

                model = glm.mat4(1.0)
                model = glm.translate(model, glm.vec3(
                    (col - (nrColumns / 2)) * spacing,
                    (row - (nrRows / 2)) * spacing,
                    -2.0
                ))
                pbrShader.setMat4("model", model)
                pbrShader.setMat3("normalMatrix", glm.transpose(glm.inverse(glm.mat3(model))))
                renderSphere()


        # render light source (simply re-render sphere at light positions)
        # this looks a bit off as we use the same shader, but it'll make their positions obvious and 
        # keeps the codeprint small.
        for i in range(lightPositions.length):

            newPos = lightPositions[i] + glm.vec3(glm.sin(glfwGetTime() * 5.0) * 5.0, 0.0, 0.0)
            newPos = lightPositions[i]
            pbrShader.setVec3("lightPositions[" + str(i) + "]", newPos)
            pbrShader.setVec3("lightColors[" + str(i) + "]", lightColors[i])

            model = glm.mat4(1.0)
            model = glm.translate(model, newPos)
            model = glm.scale(model, glm.vec3(0.5))
            pbrShader.setMat4("model", model)
            pbrShader.setMat3("normalMatrix", glm.transpose(glm.inverse(glm.mat3(model))))
            renderSphere()

        # render skybox (render as last to prevent overdraw)
        backgroundShader.use()
        backgroundShader.setMat4("view", view)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, envCubemap)
        #glBindTexture(GL_TEXTURE_CUBE_MAP, irradianceMap) # display irradiance map
        #glBindTexture(GL_TEXTURE_CUBE_MAP, prefilterMap) # display prefilter map
        renderCube()


        # render BRDF map to screen
        #brdfShader.Use()
        #renderQuad()


        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # glfw: terminate, clearing all previously allocated GLFW resources.
    # ------------------------------------------------------------------
    glfwTerminate()
    return 0

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:

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
    global firstMouse, lastX, lastY

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

# renders (and builds at first invocation) a sphere
# -------------------------------------------------
sphereVAO = 0
def renderSphere() -> None:
    global sphereVAO, indexCount

    if (sphereVAO == 0):

        sphereVAO = glGenVertexArrays(1)
        
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)

        positions = []
        uv = []
        normals = []
        indices = []

        X_SEGMENTS = 64
        Y_SEGMENTS = 64
        PI = 3.14159265359
        for x in range(X_SEGMENTS + 1):

            for y in range(Y_SEGMENTS + 1):

                xSegment = x / X_SEGMENTS
                ySegment = y / Y_SEGMENTS
                xPos = glm.cos(xSegment * 2.0 * PI) * glm.sin(ySegment * PI)
                yPos = glm.cos(ySegment * PI)
                zPos = glm.sin(xSegment * 2.0 * PI) * glm.sin(ySegment * PI)

                positions.append(glm.vec3(xPos, yPos, zPos))
                uv.append(glm.vec2(xSegment, ySegment))
                normals.append(glm.vec3(xPos, yPos, zPos))


        oddRow = False
        for y in range(Y_SEGMENTS):

            if (not oddRow): # even rows: y == 0, y == 2 and so on

                for x in range(X_SEGMENTS + 1):

                    indices.append(y * (X_SEGMENTS + 1) + x)
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)


            else:

                for x in range(X_SEGMENTS, -1, -1):

                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    indices.append(y * (X_SEGMENTS + 1) + x)


            oddRow = not oddRow

        indexCount = len(indices)

        data = []
        for i in range(len(positions)):

            data.append(positions[i].x)
            data.append(positions[i].y)
            data.append(positions[i].z)

            if (len(normals) > 0):

                data.append(normals[i].x)
                data.append(normals[i].y)
                data.append(normals[i].z)

            if (len(uv) > 0):

                data.append(uv[i].x)
                data.append(uv[i].y)

        dataArray = glm.array.from_numbers(glm.float32, *data)
        indicesArray = glm.array.from_numbers(glm.uint32, *indices)

        glBindVertexArray(sphereVAO)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, dataArray.nbytes, dataArray.ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indicesArray.nbytes, indicesArray.ptr, GL_STATIC_DRAW)
        stride = (3 + 2 + 3) * glm.sizeof(glm.float32)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * glm.sizeof(glm.float32)))

    glBindVertexArray(sphereVAO)
    glDrawElements(GL_TRIANGLE_STRIP, indexCount, GL_UNSIGNED_INT, None)

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


main()
