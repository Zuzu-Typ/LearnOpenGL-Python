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

import platform, ctypes


# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600

def main() -> int:

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

    # configure global opengl state
    # -----------------------------
    glEnable(GL_DEPTH_TEST)

    # build and compile shaders
    # -------------------------
    shader = Shader("9.1.geometry_shader.vs", "9.1.geometry_shader.fs", "9.1.geometry_shader.gs")
    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    points = glm.array(glm.float32,
        -0.5,  0.5, 1.0, 0.0, 0.0, # top-left
         0.5,  0.5, 0.0, 1.0, 0.0, # top-right
         0.5, -0.5, 0.0, 0.0, 1.0, # bottom-right
        -0.5, -0.5, 1.0, 1.0, 0.0) # bottom-left

    VBO = glGenBuffers(1)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, points.nbytes, points.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), 0)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(2 * glm.sizeof(glm.float32)))
    glBindVertexArray(0)

    # render loop
    # -----------
    while (not glfwWindowShouldClose(window)):

        # render
        # ------
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw points
        shader.use()
        glBindVertexArray(VAO)
        glDrawArrays(GL_POINTS, 0, 4)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (VAO,))
    glDeleteBuffers(1, (VBO,))

    glfwTerminate()
    return 0

# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)


main()
