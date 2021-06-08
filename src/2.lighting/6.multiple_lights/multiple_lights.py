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

from shader_m import Shader
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

# lighting
lightPos = glm.vec3(1.2, 1.0, 2.0)

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

    # build and compile our shader zprogram
    # ------------------------------------
    lightingShader = Shader("6.multiple_lights.vs", "6.multiple_lights.fs")
    lightCubeShader = Shader("6.light_cube.vs", "6.light_cube.fs")
    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    vertices = glm.array(glm.float32,
        # positions          # normals           # texture coords
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  0.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  1.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,

        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,

        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0,  1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0,  0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,

         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  1.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  0.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0,  0.0,

        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  1.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0,  1.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0,  0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  1.0,

        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0,  0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0
    )

    # positions all containers
    cubePositions = [
        glm.vec3( 0.0,  0.0,  0.0),
        glm.vec3( 2.0,  5.0, -15.0),
        glm.vec3(-1.5, -2.2, -2.5),
        glm.vec3(-3.8, -2.0, -12.3),
        glm.vec3( 2.4, -0.4, -3.5),
        glm.vec3(-1.7,  3.0, -7.5),
        glm.vec3( 1.3, -2.0, -2.5),
        glm.vec3( 1.5,  2.0, -2.5),
        glm.vec3( 1.5,  0.2, -1.5),
        glm.vec3(-1.3,  1.0, -1.5)
    ]

    # positions of the point lights
    pointLightPositions = [
        glm.vec3( 0.7,  0.2,  2.0),
        glm.vec3( 2.3, -3.3, -4.0),
        glm.vec3(-4.0,  2.0, -12.0),
        glm.vec3( 0.0,  0.0, -3.0)
    ]

    # first, configure the cube's VAO (and VBO)
    cubeVAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

    glBindVertexArray(cubeVAO)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), ctypes.c_void_p(6 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(2)

    # second, configure the light's VAO (VBO stays the same the vertices are the same for the light object which is also a 3D cube)
    lightCubeVAO = glGenVertexArrays(1)
    glBindVertexArray(lightCubeVAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    # note that we update the lamp's position attribute's stride to reflect the updated buffer data
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # load textures (we now use a utility function to keep the code more organized)
    # -----------------------------------------------------------------------------
    diffuseMap = loadTexture("container2.png")
    specularMap = loadTexture("container2_specular.png")

    # shader configuration
    # --------------------
    lightingShader.use()
    lightingShader.setInt("material.diffuse", 0)
    lightingShader.setInt("material.specular", 1)


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

        # be sure to activate shader when setting uniforms/drawing objects
        lightingShader.use()
        lightingShader.setVec3("viewPos", camera.Position)
        lightingShader.setFloat("material.shininess", 32.0)

        
        #   Here we set all the uniforms for the 5/6 types of lights we have. We have to set them manually and index 
        #   the proper PointLight struct in the array to set each uniform variable. This can be done more code-friendly
        #   by defining light types as classes and set their values in there, or by using a more efficient uniform approach
        #   by using 'Uniform buffer objects', but that is something we'll discuss in the 'Advanced GLSL' tutorial.
           
        # directional light
        lightingShader.setVec3("dirLight.direction", -0.2, -1.0, -0.3)
        lightingShader.setVec3("dirLight.ambient", 0.05, 0.05, 0.05)
        lightingShader.setVec3("dirLight.diffuse", 0.4, 0.4, 0.4)
        lightingShader.setVec3("dirLight.specular", 0.5, 0.5, 0.5)
        # point light 1
        lightingShader.setVec3("pointLights[0].position", pointLightPositions[0])
        lightingShader.setVec3("pointLights[0].ambient", 0.05, 0.05, 0.05)
        lightingShader.setVec3("pointLights[0].diffuse", 0.8, 0.8, 0.8)
        lightingShader.setVec3("pointLights[0].specular", 1.0, 1.0, 1.0)
        lightingShader.setFloat("pointLights[0].constant", 1.0)
        lightingShader.setFloat("pointLights[0].linear", 0.09)
        lightingShader.setFloat("pointLights[0].quadratic", 0.032)
        # point light 2
        lightingShader.setVec3("pointLights[1].position", pointLightPositions[1])
        lightingShader.setVec3("pointLights[1].ambient", 0.05, 0.05, 0.05)
        lightingShader.setVec3("pointLights[1].diffuse", 0.8, 0.8, 0.8)
        lightingShader.setVec3("pointLights[1].specular", 1.0, 1.0, 1.0)
        lightingShader.setFloat("pointLights[1].constant", 1.0)
        lightingShader.setFloat("pointLights[1].linear", 0.09)
        lightingShader.setFloat("pointLights[1].quadratic", 0.032)
        # point light 3
        lightingShader.setVec3("pointLights[2].position", pointLightPositions[2])
        lightingShader.setVec3("pointLights[2].ambient", 0.05, 0.05, 0.05)
        lightingShader.setVec3("pointLights[2].diffuse", 0.8, 0.8, 0.8)
        lightingShader.setVec3("pointLights[2].specular", 1.0, 1.0, 1.0)
        lightingShader.setFloat("pointLights[2].constant", 1.0)
        lightingShader.setFloat("pointLights[2].linear", 0.09)
        lightingShader.setFloat("pointLights[2].quadratic", 0.032)
        # point light 4
        lightingShader.setVec3("pointLights[3].position", pointLightPositions[3])
        lightingShader.setVec3("pointLights[3].ambient", 0.05, 0.05, 0.05)
        lightingShader.setVec3("pointLights[3].diffuse", 0.8, 0.8, 0.8)
        lightingShader.setVec3("pointLights[3].specular", 1.0, 1.0, 1.0)
        lightingShader.setFloat("pointLights[3].constant", 1.0)
        lightingShader.setFloat("pointLights[3].linear", 0.09)
        lightingShader.setFloat("pointLights[3].quadratic", 0.032)
        # spotLight
        lightingShader.setVec3("spotLight.position", camera.Position)
        lightingShader.setVec3("spotLight.direction", camera.Front)
        lightingShader.setVec3("spotLight.ambient", 0.0, 0.0, 0.0)
        lightingShader.setVec3("spotLight.diffuse", 1.0, 1.0, 1.0)
        lightingShader.setVec3("spotLight.specular", 1.0, 1.0, 1.0)
        lightingShader.setFloat("spotLight.constant", 1.0)
        lightingShader.setFloat("spotLight.linear", 0.09)
        lightingShader.setFloat("spotLight.quadratic", 0.032)
        lightingShader.setFloat("spotLight.cutOff", glm.cos(glm.radians(12.5)))
        lightingShader.setFloat("spotLight.outerCutOff", glm.cos(glm.radians(15.0)))     

        # view/projection transformations
        projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
        view = camera.GetViewMatrix()
        lightingShader.setMat4("projection", projection)
        lightingShader.setMat4("view", view)

        # world transformation
        model = glm.mat4(1.0)
        lightingShader.setMat4("model", model)

        # bind diffuse map
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, diffuseMap)
        # bind specular map
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, specularMap)

        # render containers
        glBindVertexArray(cubeVAO)
        for i in range(10):

            # calculate the model matrix for each object and pass it to shader before drawing
            model = glm.mat4(1.0)
            model = glm.translate(model, cubePositions[i])
            angle = 20.0 * i
            model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
            lightingShader.setMat4("model", model)

            glDrawArrays(GL_TRIANGLES, 0, 36)

        # also draw the lamp object(s)
        lightCubeShader.use()
        lightCubeShader.setMat4("projection", projection)
        lightCubeShader.setMat4("view", view)

        # we now draw as many light bulbs as we have point lights.
        glBindVertexArray(lightCubeVAO)
        for i in range(4):

         model = glm.mat4(1.0)
         model = glm.translate(model, pointLightPositions[i])
         model = glm.scale(model, glm.vec3(0.2)) # Make it a smaller cube
         lightCubeShader.setMat4("model", model)
         glDrawArrays(GL_TRIANGLES, 0, 36)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (cubeVAO,))
    glDeleteVertexArrays(1, (lightCubeVAO,))
    glDeleteBuffers(1, (VBO,))

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
def loadTexture(path: str) -> int:

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
