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

import platform, ctypes, os

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

    # build and compile shaders
    # -------------------------
    shader = Shader("1.1.pbr.vs", "1.1.pbr.fs")
    shader.use()
    shader.setVec3("albedo", 0.5, 0.0, 0.0)
    shader.setFloat("ao", 1.0)

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

    nrRows    = 7
    nrColumns = 7
    spacing = 2.5

    # initialize static shader uniforms before rendering
    # --------------------------------------------------
    projection = glm.perspective(glm.radians(camera.Zoom), SCR_WIDTH / SCR_HEIGHT, 0.1, 100.0)
    shader.use()
    shader.setMat4("projection", projection)

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

        shader.use()
        view = camera.GetViewMatrix()
        shader.setMat4("view", view)
        shader.setVec3("camPos", camera.Position)

        # render rows*column number of spheres with varying metallic/roughness values scaled by rows and columns respectively
        model = glm.mat4(1.0)
        for row in range(nrRows):

            shader.setFloat("metallic", row / nrRows)
            for col in range(nrColumns): 

                # we clamp the roughness to 0.05 - 1.0 as perfectly smooth surfaces (roughness of 0.0) tend to look a bit off
                # on direct lighting.
                shader.setFloat("roughness", glm.clamp(col / nrColumns, 0.05, 1.0))
                
                model = glm.mat4(1.0)
                model = glm.translate(model, glm.vec3(
                    (col - (nrColumns / 2)) * spacing, 
                    (row - (nrRows / 2)) * spacing, 
                    0.0
                ))
                shader.setMat4("model", model)
                shader.setMat3("normalMatrix", glm.transpose(glm.inverse(glm.mat3(model))))
                renderSphere()


        # render light source (simply re-render sphere at light positions)
        # this looks a bit off as we use the same shader, but it'll make their positions obvious and 
        # keeps the codeprint small.
        for i in range(lightPositions.length):

            newPos = lightPositions[i] + glm.vec3(glm.sin(glfwGetTime() * 5.0) * 5.0, 0.0, 0.0)
            newPos = lightPositions[i]
            shader.setVec3("lightPositions[" + str(i) + "]", newPos)
            shader.setVec3("lightColors[" + str(i) + "]", lightColors[i])

            model = glm.mat4(1.0)
            model = glm.translate(model, newPos)
            model = glm.scale(model, glm.vec3(0.5))
            shader.setMat4("model", model)
            shader.setMat3("normalMatrix", glm.transpose(glm.inverse(glm.mat3(model))))
            renderSphere()

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

                    indices.append(y       * (X_SEGMENTS + 1) + x)
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)


            else:

                for x in range(X_SEGMENTS, -1, -1):

                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    indices.append(y       * (X_SEGMENTS + 1) + x)


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


main()
