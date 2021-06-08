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

    # tell GLFW to capture our mouse
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)

    # configure global opengl state
    # -----------------------------
    glEnable(GL_DEPTH_TEST)

    # build and compile shaders
    # -------------------------
    shaderRed = Shader("8.advanced_glsl.vs", "8.red.fs")
    shaderGreen = Shader("8.advanced_glsl.vs", "8.green.fs")
    shaderBlue = Shader("8.advanced_glsl.vs", "8.blue.fs")
    shaderYellow = Shader("8.advanced_glsl.vs", "8.yellow.fs")
    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    cubeVertices = glm.array(glm.float32,
        # positions         
        -0.5, -0.5, -0.5, 
         0.5, -0.5, -0.5,  
         0.5,  0.5, -0.5,  
         0.5,  0.5, -0.5,  
        -0.5,  0.5, -0.5, 
        -0.5, -0.5, -0.5, 

        -0.5, -0.5,  0.5, 
         0.5, -0.5,  0.5,  
         0.5,  0.5,  0.5,  
         0.5,  0.5,  0.5,  
        -0.5,  0.5,  0.5, 
        -0.5, -0.5,  0.5, 

        -0.5,  0.5,  0.5, 
        -0.5,  0.5, -0.5, 
        -0.5, -0.5, -0.5, 
        -0.5, -0.5, -0.5, 
        -0.5, -0.5,  0.5, 
        -0.5,  0.5,  0.5, 

         0.5,  0.5,  0.5,  
         0.5,  0.5, -0.5,  
         0.5, -0.5, -0.5,  
         0.5, -0.5, -0.5,  
         0.5, -0.5,  0.5,  
         0.5,  0.5,  0.5,  

        -0.5, -0.5, -0.5, 
         0.5, -0.5, -0.5,  
         0.5, -0.5,  0.5,  
         0.5, -0.5,  0.5,  
        -0.5, -0.5,  0.5, 
        -0.5, -0.5, -0.5, 

        -0.5,  0.5, -0.5, 
         0.5,  0.5, -0.5,  
         0.5,  0.5,  0.5,  
         0.5,  0.5,  0.5,  
        -0.5,  0.5,  0.5, 
        -0.5,  0.5, -0.5)

    # cube VAO
    cubeVAO = glGenVertexArrays(1)
    cubeVBO = glGenBuffers(1)
    glBindVertexArray(cubeVAO)
    glBindBuffer(GL_ARRAY_BUFFER, cubeVBO)
    glBufferData(GL_ARRAY_BUFFER, cubeVertices.nbytes, cubeVertices.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * glm.sizeof(glm.float32), None)

    # configure a uniform buffer object
    # ---------------------------------
    # first. We get the relevant block indices
    uniformBlockIndexRed = glGetUniformBlockIndex(shaderRed.ID, "Matrices")
    uniformBlockIndexGreen = glGetUniformBlockIndex(shaderGreen.ID, "Matrices")
    uniformBlockIndexBlue = glGetUniformBlockIndex(shaderBlue.ID, "Matrices")
    uniformBlockIndexYellow = glGetUniformBlockIndex(shaderYellow.ID, "Matrices")
    # then we link each shader's uniform block to this uniform binding point
    glUniformBlockBinding(shaderRed.ID, uniformBlockIndexRed, 0)
    glUniformBlockBinding(shaderGreen.ID, uniformBlockIndexGreen, 0)
    glUniformBlockBinding(shaderBlue.ID, uniformBlockIndexBlue, 0)
    glUniformBlockBinding(shaderYellow.ID, uniformBlockIndexYellow, 0)
    # Now actually create the buffer
    uboMatrices = glGenBuffers(1)
    glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices)
    glBufferData(GL_UNIFORM_BUFFER, 2 * glm.sizeof(glm.mat4), None, GL_STATIC_DRAW)
    glBindBuffer(GL_UNIFORM_BUFFER, 0)
    # define the range of the buffer that links to a uniform binding point
    glBindBufferRange(GL_UNIFORM_BUFFER, 0, uboMatrices, 0, 2 * glm.sizeof(glm.mat4))

    # store the projection matrix (we only do this once now) (note: we're not using zoom anymore by changing the FoV)
    projection = glm.perspective(45.0, SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
    glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices)
    glBufferSubData(GL_UNIFORM_BUFFER, 0, glm.sizeof(glm.mat4), glm.value_ptr(projection))
    glBindBuffer(GL_UNIFORM_BUFFER, 0)
  
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

        # set the view and projection matrix in the uniform block - we only have to do this once per loop iteration.
        view = camera.GetViewMatrix()
        glBindBuffer(GL_UNIFORM_BUFFER, uboMatrices)
        glBufferSubData(GL_UNIFORM_BUFFER, glm.sizeof(glm.mat4), glm.sizeof(glm.mat4), glm.value_ptr(view))
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

        # draw 4 cubes 
        # RED
        glBindVertexArray(cubeVAO)
        shaderRed.use()
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(-0.75, 0.75, 0.0)) # move top-left
        shaderRed.setMat4("model", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # GREEN
        shaderGreen.use()
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.75, 0.75, 0.0)) # move top-right
        shaderGreen.setMat4("model", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # YELLOW
        shaderYellow.use()
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(-0.75, -0.75, 0.0)) # move bottom-left
        shaderYellow.setMat4("model", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # BLUE
        shaderBlue.use()
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(0.75, -0.75, 0.0)) # move bottom-right
        shaderBlue.setMat4("model", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (cubeVAO,))
    glDeleteBuffers(1, (cubeVBO,))

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


main()
