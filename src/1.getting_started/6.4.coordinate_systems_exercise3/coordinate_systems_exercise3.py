...


glBindVertexArray(VAO)
for i in range(10):
    # calculate the model matrix for each object and pass it to shader before drawing
    model = glm.mat4(1.0)
    model = glm.translate(model, cubePositions[i])
    angle = 20.0 * i
    if (i % 3 == 0):  // every 3rd iteration (including the first) we set the angle using GLFW's time function.
        angle = glfwGetTime() * 25.0
    model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))
    ourShader.setMat4("model", model)
    
    glDrawArrays(GL_TRIANGLES, 0, 36)

...