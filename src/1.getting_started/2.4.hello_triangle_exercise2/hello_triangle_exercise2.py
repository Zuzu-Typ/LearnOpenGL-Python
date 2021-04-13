try:
    from OpenGL.GL import *
    from glfw.GLFW import *

    from glfw import _GLFWwindow as GLFWwindow

    import platform, glm
except ImportError:
    import requirements
    
    from OpenGL.GL import *
    from glfw.GLFW import *

    from glfw import _GLFWwindow as GLFWwindow

    import platform, glm

# settings
SCR_WIDTH = 800
SCR_HEIGHT = 600

vertexShaderSource = """#version 330 core
layout (location = 0) in vec3 aPos;
void main()
{
   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
"""

fragmentShaderSource = """#version 330 core
out vec4 FragColor;
void main()
{
   FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

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
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)

    # build and compile our shader program
    # ------------------------------------
    # vertex shader
    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShader, vertexShaderSource)
    glCompileShader(vertexShader)
    
    # check for shader compile errors
    success = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
    if (not success):

        infoLog = glGetShaderInfoLog(vertexShader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())

    # fragment shader
    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShader, fragmentShaderSource)
    glCompileShader(fragmentShader)
    
    # check for shader compile errors
    success = glGetShaderiv(fragmentShader, GL_COMPILE_STATUS)
    if (not success):

        infoLog = glGetShaderInfoLog(fragmentShader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    # link shaders
    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragmentShader)
    glLinkProgram(shaderProgram)
    
    # check for linking errors
    success = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
    if (not success):
        infoLog = glGetProgramInfoLog(shaderProgram)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())

    glDeleteShader(vertexShader)
    glDeleteShader(fragmentShader)

    # set up vertex data (and buffer(s)) and configure vertex attributes
    # ------------------------------------------------------------------
    firstTriangle = glm.array(glm.float32,
        -0.9, -0.5, 0.0,  # left 
        -0.0, -0.5, 0.0,  # right
        -0.45, 0.5, 0.0,  # top
    )

    secondTriangle = glm.array(glm.float32,
        0.0, -0.5, 0.0,  # left
        0.9, -0.5, 0.0,  # right
        0.45, 0.5, 0.0   # top
    )

    VAOs = glGenVertexArrays(2) # we can also generate multiple VAOs or buffers at the same time
    VBOs = glGenBuffers(2)
    # first triangle setup
    # --------------------
    glBindVertexArray(VAOs[0])
    glBindBuffer(GL_ARRAY_BUFFER, VBOs[0])
    glBufferData(GL_ARRAY_BUFFER, firstTriangle.nbytes, firstTriangle.ptr, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * glm.sizeof(glm.float32), None)	# Vertex attributes stay the same
    glEnableVertexAttribArray(0)
    # glBindVertexArray(0) # no need to unbind at all as we directly bind a different VAO the next few lines
    # second triangle setup
    # ---------------------
    glBindVertexArray(VAOs[1])	# note that we bind to a different VAO now
    glBindBuffer(GL_ARRAY_BUFFER, VBOs[1])	# and a different VBO
    glBufferData(GL_ARRAY_BUFFER, secondTriangle.nbytes, secondTriangle.ptr, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # because the vertex data is tightly packed we can also specify 0 as the vertex attribute's stride to let OpenGL figure it out
    glEnableVertexAttribArray(0)
    # glBindVertexArray(0) # not really necessary as well, but beware of calls that could affect VAOs while this one is bound (like binding element buffer objects, or enabling/disabling vertex attributes)


    # uncomment this call to draw in wireframe polygons.
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # render loop
    # -----------
    while (not glfwWindowShouldClose(window)):

        # input
        # -----
        processInput(window)

        # render
        # ------
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shaderProgram)
        # draw first triangle using the data from the first VAO
        glBindVertexArray(VAOs[0])
        glDrawArrays(GL_TRIANGLES, 0, 3)
        # then we draw the second triangle using the data from the second VAO
        glBindVertexArray(VAOs[1])
        glDrawArrays(GL_TRIANGLES, 0, 3)
 
        # glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
        # -------------------------------------------------------------------------------
        glfwSwapBuffers(window)
        glfwPollEvents()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    glDeleteVertexArrays(2, VAOs)
    glDeleteBuffers(2, VBOs)
    glDeleteProgram(shaderProgram)

    # glfw: terminate, clearing all previously allocated GLFW resources.
    # ------------------------------------------------------------------
    glfwTerminate()
    return 0

# process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
# ---------------------------------------------------------------------------------------------------------
def processInput(window: GLFWwindow) -> None:

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS):
        glfwSetWindowShouldClose(window, True)

# glfw: whenever the window size changed (by OS or user resize) this callback function executes
# ---------------------------------------------------------------------------------------------
def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:

    # make sure the viewport matches the new window dimensions note that width and 
    # height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height)

main()
