vertices = glm.array(glm.float32,
    # back face
    -0.5, -0.5, -0.5,  0.0, 0.0, # bottom-left
     0.5, -0.5, -0.5,  1.0, 0.0, # bottom-right    
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right              
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right
    -0.5,  0.5, -0.5,  0.0, 1.0, # top-left
    -0.5, -0.5, -0.5,  0.0, 0.0, # bottom-left                
    # front face
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left
     0.5,  0.5,  0.5,  1.0, 1.0, # top-right
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-right        
     0.5,  0.5,  0.5,  1.0, 1.0, # top-right
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left
    -0.5,  0.5,  0.5,  0.0, 1.0, # top-left        
    # left face
    -0.5,  0.5,  0.5,  1.0, 0.0, # top-right
    -0.5, -0.5, -0.5,  0.0, 1.0, # bottom-left
    -0.5,  0.5, -0.5,  1.0, 1.0, # top-left       
    -0.5, -0.5, -0.5,  0.0, 1.0, # bottom-left
    -0.5,  0.5,  0.5,  1.0, 0.0, # top-right
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-right
    # right face
     0.5,  0.5,  0.5,  1.0, 0.0, # top-left
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right      
     0.5, -0.5, -0.5,  0.0, 1.0, # bottom-right          
     0.5, -0.5, -0.5,  0.0, 1.0, # bottom-right
     0.5, -0.5,  0.5,  0.0, 0.0, # bottom-left
     0.5,  0.5,  0.5,  1.0, 0.0, # top-left
    # bottom face          
    -0.5, -0.5, -0.5,  0.0, 1.0, # top-right
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-left
     0.5, -0.5, -0.5,  1.0, 1.0, # top-left        
     0.5, -0.5,  0.5,  1.0, 0.0, # bottom-left
    -0.5, -0.5, -0.5,  0.0, 1.0, # top-right
    -0.5, -0.5,  0.5,  0.0, 0.0, # bottom-right
    # top face
    -0.5,  0.5, -0.5,  0.0, 1.0, # top-left
     0.5,  0.5, -0.5,  1.0, 1.0, # top-right
     0.5,  0.5,  0.5,  1.0, 0.0, # bottom-right                 
     0.5,  0.5,  0.5,  1.0, 0.0, # bottom-right
    -0.5,  0.5,  0.5,  0.0, 0.0, # bottom-left  
    -0.5,  0.5, -0.5,  0.0, 1.0) # top-left              

"""
   Also make sure to add a call to OpenGL to specify that triangles defined by a clockwise ordering 
   are now 'front-facing' triangles so the cube is rendered as normal:
   glFrontFace(GL_CW)
"""
