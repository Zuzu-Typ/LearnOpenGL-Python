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

# Properties
screenWidth = 800
screenHeight = 600

# Camera
camera = Camera(glm.vec3(0.0, 0.0, 3.0))
keys = {}
lastX = 400
lastY = 300
firstMouse = True

deltaTime = 0.0
lastFrame = 0.0

# The MAIN function, from here we start our application and run our Game loop
def main() -> int:
    global deltaTime, lastFrame

    # Init GLFW
    glfwInit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)
    glfwWindowHint(GLFW_RESIZABLE, GL_FALSE)

    if (platform.system() == "Darwin"): # APPLE
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfwCreateWindow(screenWidth, screenHeight, "LearnOpenGL", None, None) # Windowed
    glfwMakeContextCurrent(window)

    # Set the required callback functions
    glfwSetKeyCallback(window, key_callback)
    glfwSetCursorPosCallback(window, mouse_callback)
    glfwSetScrollCallback(window, scroll_callback)

    # Options
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)

    # Define the viewport dimensions
    glViewport(0, 0, screenWidth, screenHeight)

    # Setup some OpenGL options
    glEnable(GL_DEPTH_TEST)
    # glDepthFunc(GL_ALWAYS) # Set to always pass the depth test (same effect as glDisable(GL_DEPTH_TEST))

    # Setup and compile our shaders
    shader = Shader("csm.vs", "csm.fs")
    # Set the object data (buffers, vertex attributes)
    cubeVertices = glm.array(glm.float32,
        # Positions          # Texture Coords
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 0.0,

        -0.5, -0.5,  0.5,  0.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,

        -0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,
        -0.5,  0.5,  0.5,  1.0, 0.0,

         0.5,  0.5,  0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
         0.5, -0.5, -0.5,  0.0, 1.0,
         0.5, -0.5, -0.5,  0.0, 1.0,
         0.5, -0.5,  0.5,  0.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 0.0,

        -0.5, -0.5, -0.5,  0.0, 1.0,
         0.5, -0.5, -0.5,  1.0, 1.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,

        -0.5,  0.5, -0.5,  0.0, 1.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
         0.5,  0.5,  0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5,  0.5,  0.0, 0.0,
        -0.5,  0.5, -0.5,  0.0, 1.0)

    planeVertices = glm.array(glm.float32,
        # Positions            # Texture Coords (note we set these higher than 1 that together with GL_REPEAT as texture wrapping mode will cause the floor texture to repeat)
        5.0,  -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5,  5.0,  0.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,

        5.0,  -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,
        5.0,  -0.5, -5.0,  2.0, 2.0)							

    # Setup cube VAO
    cubeVAO = glGenVertexArrays(1)
    cubeVBO = glGenBuffers(1)
    glBindVertexArray(cubeVAO)
    glBindBuffer(GL_ARRAY_BUFFER, cubeVBO)
    glBufferData(GL_ARRAY_BUFFER, cubeVertices.nbytes, cubeVertices.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glBindVertexArray(0)
    # Setup plane VAO
    planeVAO = glGenVertexArrays(1)
    planeVBO = glGenBuffers(1)
    glBindVertexArray(planeVAO)
    glBindBuffer(GL_ARRAY_BUFFER, planeVBO)
    glBufferData(GL_ARRAY_BUFFER, planeVertices.nbytes, planeVertices.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glBindVertexArray(0)

    # Load textures
    cubeTexture = loadTexture("marble.jpg")
    floorTexture = loadTexture("metal.png")
    #pragma endregion

    # Game loop
    while(not glfwWindowShouldClose(window)):

        # Set frame time
        currentFrame = glfwGetTime()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        # Check and call events
        glfwPollEvents()
        Do_Movement()

        # Clear the colorbuffer
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw objects
        shader.use() 
        model = glm.mat4()
        view = camera.GetViewMatrix()
        projection = glm.perspective(camera.Zoom, screenWidth/screenHeight, 0.1, 100.0)
        shader.setMat4("view", view)
        shader.setMat4("projection", projection)
        # Cubes
        glBindVertexArray(cubeVAO)
        glBindTexture(GL_TEXTURE_2D, cubeTexture)  # We omit the glActiveTexture part since TEXTURE0 is already the default active texture unit. (sampler used in fragment is set to 0 as well as default)		
        model = glm.translate(model, glm.vec3(-1.0, 0.0, -1.0))
        shader.setMat4("view", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        model = glm.mat4()
        model = glm.translate(model, glm.vec3(2.0, 0.0, 0.0))
        shader.setMat4("view", model)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # Floor
        glBindVertexArray(planeVAO)
        glBindTexture(GL_TEXTURE_2D, floorTexture)
        model = glm.mat4()
        shader.setMat4("view", model)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)				


        # Swap the buffers
        glfwSwapBuffers(window)

    glfwTerminate()
    return 0

# This function loads a texture from file. Note: texture loading functions like these are usually 
# managed by a 'Resource Manager' that manages all resources (like textures, models, audio). 
# For learning purposes we'll just define it as a utility function.
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

# Moves/alters the camera positions based on user input
def Do_Movement() -> None:
    global deltaTime, keys

    # Camera controls
    if(keys.get(GLFW_KEY_W, False)):
        camera.ProcessKeyboard(Camera_Movement.FORWARD, deltaTime)
    if(keys.get(GLFW_KEY_S, False)):
        camera.ProcessKeyboard(Camera_Movement.BACKWARD, deltaTime)
    if(keys.get(GLFW_KEY_A, False)):
        camera.ProcessKeyboard(Camera_Movement.LEFT, deltaTime)
    if(keys.get(GLFW_KEY_D, False)):
        camera.ProcessKeyboard(Camera_Movement.RIGHT, deltaTime)

# Is called whenever a key is pressed/released via GLFW
def key_callback(window: GLFWwindow, key: int, scancode: int, action: int, mode: int) -> None:
    global keys

    if(key == GLFW_KEY_ESCAPE and action == GLFW_PRESS):
        glfwSetWindowShouldClose(window, GL_TRUE)

    if(action == GLFW_PRESS):
        keys[key] = True
    elif(action == GLFW_RELEASE):
        keys[key] = False	

def mouse_callback(window: GLFWwindow, xpos: float, ypos: float) -> None:
    global lastX, lastY, firstMouse

    if(firstMouse):

        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos 
    
    lastX = xpos
    lastY = ypos

    camera.ProcessMouseMovement(xoffset, yoffset)

def scroll_callback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:

    camera.ProcessMouseScroll(yoffset)


main()
