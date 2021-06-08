def main() -> int:

    [...]
    # render loop
    while(not glfwWindowShouldClose(window)):

        # per-frame time logic
        currentFrame = glfwGetTime()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        # input
        processInput(window)

        # clear the colorbuffer
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # change the light's position values over time (can be done anywhere in the render loop actually, but try to do it at least before using the light source positions)
        lightPos.x = 1.0 + glm.sin(glfwGetTime()) * 2.0
        lightPos.y = glm.sin(glfwGetTime() / 2.0) * 1.0
        
        # set uniforms, draw objects
        [...]
        
        # glfw: swap buffers and poll IO events
        glfwSwapBuffers(window)
        glfwPollEvents()



main()
