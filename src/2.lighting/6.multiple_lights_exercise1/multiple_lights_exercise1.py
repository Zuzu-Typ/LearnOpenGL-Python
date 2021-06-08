# == ==============================================================================================
#       DESERT
# == ==============================================================================================
glClearColor(0.75, 0.52, 0.3, 1.0)
[...]
pointLightColors = [
    glm.vec3(1.0, 0.6, 0.0),
    glm.vec3(1.0, 0.0, 0.0),
    glm.vec3(1.0, 1.0, 0.0),
    glm.vec3(0.2, 0.2, 1.0)
]

[...]
# Directional light
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.direction"), -0.2, -1.0, -0.3)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.ambient"), 0.3, 0.24, 0.14)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.diffuse"), 0.7, 0.42, 0.26) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.specular"), 0.5, 0.5, 0.5)
# Point light 1
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].position"), pointLightPositions[0].x, pointLightPositions[0].y, pointLightPositions[0].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].ambient"), pointLightColors[0].x * 0.1,  pointLightColors[0].y * 0.1,  pointLightColors[0].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].diffuse"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].specular"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].quadratic"), 0.032)		
# Point light 2
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].position"), pointLightPositions[1].x, pointLightPositions[1].y, pointLightPositions[1].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].ambient"), pointLightColors[1].x * 0.1,  pointLightColors[1].y * 0.1,  pointLightColors[1].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].diffuse"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].specular"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].quadratic"), 0.032)		
# Point light 3
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].position"), pointLightPositions[2].x, pointLightPositions[2].y, pointLightPositions[2].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].ambient"), pointLightColors[2].x * 0.1,  pointLightColors[2].y * 0.1,  pointLightColors[2].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].diffuse"), pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].specular") ,pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].quadratic"), 0.032)		
# Point light 4
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].position"), pointLightPositions[3].x, pointLightPositions[3].y, pointLightPositions[3].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].ambient"), pointLightColors[3].x * 0.1,  pointLightColors[3].y * 0.1,  pointLightColors[3].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].diffuse"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].specular"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].quadratic"), 0.032)		
# SpotLight
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.position"), camera.Position.x, camera.Position.y, camera.Position.z)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.direction"), camera.Front.x, camera.Front.y, camera.Front.z)
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.ambient"), 0.0, 0.0, 0.0)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.diffuse"), 0.8, 0.8, 0.0) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.specular"), 0.8, 0.8, 0.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.quadratic"), 0.032)			
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.cutOff"), glm.cos(glm.radians(12.5)))
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.outerCutOff"), glm.cos(glm.radians(13.0)))	
# == ==============================================================================================
#       FACTORY
# == ==============================================================================================
glClearColor(0.1, 0.1, 0.1, 1.0)
[...]
pointLightColors = [
    glm.vec3(0.2, 0.2, 0.6),
    glm.vec3(0.3, 0.3, 0.7),
    glm.vec3(0.0, 0.0, 0.3),
    glm.vec3(0.4, 0.4, 0.4)
]

[...]
# Directional light
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.direction"), -0.2, -1.0, -0.3)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.ambient"), 0.05, 0.05, 0.1)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.diffuse"), 0.2, 0.2, 0.7) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.specular"), 0.7, 0.7, 0.7)
# Point light 1
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].position"), pointLightPositions[0].x, pointLightPositions[0].y, pointLightPositions[0].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].ambient"), pointLightColors[0].x * 0.1,  pointLightColors[0].y * 0.1,  pointLightColors[0].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].diffuse"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].specular"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].quadratic"), 0.032)		
# Point light 2
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].position"), pointLightPositions[1].x, pointLightPositions[1].y, pointLightPositions[1].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].ambient"), pointLightColors[1].x * 0.1,  pointLightColors[1].y * 0.1,  pointLightColors[1].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].diffuse"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].specular"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].quadratic"), 0.032)		
# Point light 3
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].position"), pointLightPositions[2].x, pointLightPositions[2].y, pointLightPositions[2].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].ambient"), pointLightColors[2].x * 0.1,  pointLightColors[2].y * 0.1,  pointLightColors[2].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].diffuse"), pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].specular") ,pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].quadratic"), 0.032)		
# Point light 4
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].position"), pointLightPositions[3].x, pointLightPositions[3].y, pointLightPositions[3].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].ambient"), pointLightColors[3].x * 0.1,  pointLightColors[3].y * 0.1,  pointLightColors[3].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].diffuse"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].specular"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].quadratic"), 0.032)		
# SpotLight
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.position"), camera.Position.x, camera.Position.y, camera.Position.z)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.direction"), camera.Front.x, camera.Front.y, camera.Front.z)
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.ambient"), 0.0, 0.0, 0.0)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.diffuse"), 1.0, 1.0, 1.0) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.specular"), 1.0, 1.0, 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.linear"), 0.009)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.quadratic"), 0.0032)			
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.cutOff"), glm.cos(glm.radians(10.0)))
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.outerCutOff"), glm.cos(glm.radians(12.5)))	
# == ==============================================================================================
#       HORROR
# == ==============================================================================================
glClearColor(0.0, 0.0, 0.0, 1.0)
[...]
pointLightColors = [
    glm.vec3(0.1, 0.1, 0.1),
    glm.vec3(0.1, 0.1, 0.1),
    glm.vec3(0.1, 0.1, 0.1),
    glm.vec3(0.3, 0.1, 0.1)
]

[...]
# Directional light
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.direction"), -0.2, -1.0, -0.3)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.ambient"), 0.0, 0.0, 0.0)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.diffuse"), 0.05, 0.05, 0.05) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.specular"), 0.2, 0.2, 0.2)
# Point light 1
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].position"), pointLightPositions[0].x, pointLightPositions[0].y, pointLightPositions[0].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].ambient"), pointLightColors[0].x * 0.1,  pointLightColors[0].y * 0.1,  pointLightColors[0].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].diffuse"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].specular"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].linear"), 0.14)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].quadratic"), 0.07)		
# Point light 2
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].position"), pointLightPositions[1].x, pointLightPositions[1].y, pointLightPositions[1].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].ambient"), pointLightColors[1].x * 0.1,  pointLightColors[1].y * 0.1,  pointLightColors[1].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].diffuse"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].specular"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].linear"), 0.14)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].quadratic"), 0.07)		
# Point light 3
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].position"), pointLightPositions[2].x, pointLightPositions[2].y, pointLightPositions[2].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].ambient"), pointLightColors[2].x * 0.1,  pointLightColors[2].y * 0.1,  pointLightColors[2].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].diffuse"), pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].specular") ,pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].linear"), 0.22)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].quadratic"), 0.20)		
# Point light 4
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].position"), pointLightPositions[3].x, pointLightPositions[3].y, pointLightPositions[3].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].ambient"), pointLightColors[3].x * 0.1,  pointLightColors[3].y * 0.1,  pointLightColors[3].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].diffuse"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].specular"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].linear"), 0.14)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].quadratic"), 0.07)		
# SpotLight
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.position"), camera.Position.x, camera.Position.y, camera.Position.z)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.direction"), camera.Front.x, camera.Front.y, camera.Front.z)
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.ambient"), 0.0, 0.0, 0.0)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.diffuse"), 1.0, 1.0, 1.0) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.specular"), 1.0, 1.0, 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.linear"), 0.09)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.quadratic"), 0.032)			
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.cutOff"), glm.cos(glm.radians(10.0)))
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.outerCutOff"), glm.cos(glm.radians(15.0)))
# == ==============================================================================================
#       BIOCHEMICAL LAB
# == ==============================================================================================
glClearColor(0.9, 0.9, 0.9, 1.0)
[...]
pointLightColors = [
    glm.vec3(0.4, 0.7, 0.1),
    glm.vec3(0.4, 0.7, 0.1),
    glm.vec3(0.4, 0.7, 0.1),
    glm.vec3(0.4, 0.7, 0.1)
]

[...]
# Directional light
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.direction"), -0.2, -1.0, -0.3)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.ambient"), 0.5, 0.5, 0.5)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.diffuse"), 1.0, 1.0, 1.0) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "dirLight.specular"), 1.0, 1.0, 1.0)
# Point light 1
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].position"), pointLightPositions[0].x, pointLightPositions[0].y, pointLightPositions[0].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].ambient"), pointLightColors[0].x * 0.1,  pointLightColors[0].y * 0.1,  pointLightColors[0].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].diffuse"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[0].specular"), pointLightColors[0].x,  pointLightColors[0].y,  pointLightColors[0].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].linear"), 0.07)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[0].quadratic"), 0.017)		
# Point light 2
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].position"), pointLightPositions[1].x, pointLightPositions[1].y, pointLightPositions[1].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].ambient"), pointLightColors[1].x * 0.1,  pointLightColors[1].y * 0.1,  pointLightColors[1].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].diffuse"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[1].specular"), pointLightColors[1].x,  pointLightColors[1].y,  pointLightColors[1].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].linear"), 0.07)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[1].quadratic"), 0.017)		
# Point light 3
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].position"), pointLightPositions[2].x, pointLightPositions[2].y, pointLightPositions[2].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].ambient"), pointLightColors[2].x * 0.1,  pointLightColors[2].y * 0.1,  pointLightColors[2].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].diffuse"), pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[2].specular") ,pointLightColors[2].x,  pointLightColors[2].y,  pointLightColors[2].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].linear"), 0.07)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[2].quadratic"), 0.017)		
# Point light 4
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].position"), pointLightPositions[3].x, pointLightPositions[3].y, pointLightPositions[3].z)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].ambient"), pointLightColors[3].x * 0.1,  pointLightColors[3].y * 0.1,  pointLightColors[3].z * 0.1)		
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].diffuse"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "pointLights[3].specular"), pointLightColors[3].x,  pointLightColors[3].y,  pointLightColors[3].z)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].linear"), 0.07)
glUniform1f(glGetUniformLocation(lightingShader.Program, "pointLights[3].quadratic"), 0.017)		
# SpotLight
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.position"), camera.Position.x, camera.Position.y, camera.Position.z)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.direction"), camera.Front.x, camera.Front.y, camera.Front.z)
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.ambient"), 0.0, 0.0, 0.0)	
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.diffuse"), 0.0, 1.0, 0.0) 
glUniform3f(glGetUniformLocation(lightingShader.Program, "spotLight.specular"), 0.0, 1.0, 0.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.constant"), 1.0)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.linear"), 0.07)
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.quadratic"), 0.017)	
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.cutOff"), glm.cos(glm.radians(7.0)))
glUniform1f(glGetUniformLocation(lightingShader.Program, "spotLight.outerCutOff"), glm.cos(glm.radians(10.0)))	

main()
