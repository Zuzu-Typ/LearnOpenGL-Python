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
    shader = Shader("10.1.instancing.vs", "10.1.instancing.fs")
    # generate a list of 100 quad locations/translation-vectors
    # ---------------------------------------------------------
    translations = glm.array.zeros(100, glm.vec2)
    index = 0
    offset = 0.1
    for y in range(-10, 10, 2):
        for x in range(-10, 10, 2):
            translation = glm.vec2()
            translation.x = x / 10.0 + offset
            translation.y = y / 10.0 + offset
            translations[index] = translation
            index += 1


    # store instance data in an array buffer
    # --------------------------------------
    instanceVBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
    glBufferData(GL_ARRAY_BUFFER, translations.nbytes, translations.ptr, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    quadVertices = glm.array(glm.float32,
        # positions     # colors
        -0.05,  0.05,  1.0, 0.0, 0.0,
         0.05, -0.05,  0.0, 1.0, 0.0,
        -0.05, -0.05,  0.0, 0.0, 1.0,

        -0.05,  0.05,  1.0, 0.0, 0.0,
         0.05, -0.05,  0.0, 1.0, 0.0,
         0.05,  0.05,  0.0, 1.0, 1.0)

    quadVAO = glGenVertexArrays(1)
    quadVBO = glGenBuffers(1)
    glBindVertexArray(quadVAO)
    glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
    glBufferData(GL_ARRAY_BUFFER, quadVertices.nbytes, quadVertices.ptr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), ctypes.c_void_p(2 * glm.sizeof(glm.float32)))
    # also set instance data
    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER, instanceVBO) # this attribute comes from a different vertex buffer
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 2 * glm.sizeof(glm.float32), None)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glVertexAttribDivisor(2, 1) # tell OpenGL this is an instanced vertex attribute.


    # render loop
    # -----------
    while (not glfwWindowShouldClose(window)):

        # render
        # ------
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw 100 instanced quads
        shader.use()
        glBindVertexArray(quadVAO)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, 100) # 100 triangles of 6 vertices each
        glBindVertexArray(0)

        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(1, (quadVAO,))
    glDeleteBuffers(1, (quadVBO,))

    glfwTerminate()
    return 0

# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)


main()
