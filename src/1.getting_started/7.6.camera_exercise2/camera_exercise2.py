# Custom implementation of the LookAt function
def calculate_lookAt_matrix(position: glm.vec3, target: glm.vec3, worldUp: glm.vec3) -> glm.mat4:

    # 1. Position = known
    # 2. Calculate cameraDirection
    zaxis = glm.normalize(position - target)
    # 3. Get positive right axis vector
    xaxis = glm.normalize(glm.cross(glm.normalize(worldUp), zaxis))
    # 4. Calculate camera up vector
    yaxis = glm.cross(zaxis, xaxis)

    # Create translation and rotation matrix
    # In glm we access elements as mat[col][row] due to column-major layout
    translation = glm.mat4(1.0) # Identity matrix by default
    translation[3][0] = -position.x # Fourth column, first row
    translation[3][1] = -position.y
    translation[3][2] = -position.z
    rotation = glm.mat4(1.0)
    rotation[0][0] = xaxis.x # First column, first row
    rotation[1][0] = xaxis.y
    rotation[2][0] = xaxis.z
    rotation[0][1] = yaxis.x # First column, second row
    rotation[1][1] = yaxis.y
    rotation[2][1] = yaxis.z
    rotation[0][2] = zaxis.x # First column, third row
    rotation[1][2] = zaxis.y
    rotation[2][2] = zaxis.z 

    # Return lookAt matrix as combination of translation and rotation matrix
    return rotation * translation # Remember to read from right to left (first translation then rotation)

# Don't forget to replace glm.lookAt with your own version
# view = glm.lookAt(glm.vec3(camX, 0.0, camZ), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
view = calculate_lookAt_matrix(glm.vec3(camX, 0.0, camZ), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

