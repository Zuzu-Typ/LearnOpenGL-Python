from OpenGL.GL import * # holds all OpenGL type declarations
    
import glm

from shader import Shader

import ctypes

from typing import List

class Vertex:
    PositionOffset = ctypes.c_void_p(0)
    NormalOffset = ctypes.c_void_p(glm.sizeof(glm.vec3))
    TexCoordsOffset = ctypes.c_void_p(NormalOffset.value + glm.sizeof(glm.vec3))
    TangentOffset = ctypes.c_void_p(TexCoordsOffset.value + glm.sizeof(glm.vec2))
    BitangentOffset = ctypes.c_void_p(TangentOffset.value + glm.sizeof(glm.vec3))
    size = BitangentOffset.value + glm.sizeof(glm.vec3)
    
class Texture:
    def __init__(self, id : int, type : str, path : str):
        self.id = id
        self.type = type
        self.path = path

class Mesh:

    # constructor
    def __init__(self, vertices : glm.array, indices : List[int], textures : List[Texture]):
        self.vertices = vertices
        self.indices = glm.array.from_numbers(glm.uint32, *indices)
        self.textures = textures

        # now that we have all the required data, set the vertex buffers and its attribute pointers.
        self.setupMesh()

    # render the mesh
    def Draw(self, shader : Shader): 

        # bind appropriate textures
        diffuseNr  = 1
        specularNr = 1
        normalNr   = 1
        heightNr   = 1
        for i in range(len(self.textures)):

            glActiveTexture(GL_TEXTURE0 + i) # active proper texture unit before binding
            # retrieve texture number (the N in diffuse_textureN)
            number = None
            name = self.textures[i].type
            
            if(name == "texture_diffuse"):
                number = str(diffuseNr)
                diffuseNr += 1
            elif(name == "texture_specular"):
                number = str(specularNr)
                specularNr += 1
            elif(name == "texture_normal"):
                number = str(normalNr)
                normalNr += 1
            elif(name == "texture_height"):
                number = str(heightNr)
                heightNr += 1

            # now set the sampler to the correct texture unit
            glUniform1i(glGetUniformLocation(shader.ID, (name + number)), i)
            # and finally bind the texture
            glBindTexture(GL_TEXTURE_2D, self.textures[i].id)

        # draw mesh
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # always good practice to set everything back to defaults once configured.
        glActiveTexture(GL_TEXTURE0)


    # initializes all the buffer objects/arrays
    def setupMesh(self):

        # create buffers/arrays
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)
        # load data into vertex buffers
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        # A great thing about structs is that their memory layout is sequential for all its items.
        # The effect is that we can simply pass a pointer to the struct and it translates perfectly to a glm.vec3/2 array which
        # again translates to 3/2 floats which translates to a byte array.
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices.ptr, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices.ptr, GL_STATIC_DRAW)

        # set the vertex attribute pointers
        # vertex Positions
        glEnableVertexAttribArray(0)	
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, Vertex.size, None)
        # vertex normals
        glEnableVertexAttribArray(1)	
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, Vertex.size, Vertex.NormalOffset)
        # vertex texture coords
        glEnableVertexAttribArray(2)	
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, Vertex.size, Vertex.TexCoordsOffset)
        # vertex tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, Vertex.size, Vertex.TangentOffset)
        # vertex bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, Vertex.size, Vertex.BitangentOffset)

        glBindVertexArray(0)

