from OpenGL.GL import * 
    
import glm

from PIL import Image

import assimp_py

from mesh import Mesh, Texture
from shader import Shader

import platform, ctypes, os

from typing import List

# function that loads and automatically flips an image vertically
LOAD_IMAGE = lambda name: Image.open(name).transpose(Image.FLIP_TOP_BOTTOM)

class Model:

    # constructor, expects a filepath to a 3D model.
    def __init__(self, path: str, gamma : bool = False):
        self.gammaCorrection = gamma
        self.loadModel(path)

    # draws the model, and thus all its meshes
    def Draw(self, shader : Shader):
        for mesh in self.meshes:
            mesh.Draw(shader)
            
    # loads a model with supported ASSIMP extensions from file and stores the resulting meshes in the meshes vector.
    def loadModel(self, path : str):


        # read file via ASSIMP
        assimp_flags = assimp_py.Process_Triangulate | assimp_py.Process_GenSmoothNormals | assimp_py.Process_FlipUVs | assimp_py.Process_CalcTangentSpace
        scene = assimp_py.ImportFile(path, assimp_flags)

        # retrieve the directory path of the filepath
        self.directory = os.path.dirname(path)

        self.meshes = []
        self.textures_loaded = []

        # process ASSIMP's root node recursively
        self.processMeshes(scene)

    # processes a node in a recursive fashion. Processes each individual mesh located at the node and repeats this process on its children nodes (if any).
    def processMeshes(self, scene : assimp_py.Scene):

        # process each mesh located at the current node
        for mesh in scene.meshes:

            # the node object only contains indices to index the actual objects in the scene. 
            # the scene contains all the data, node is just to keep stuff organized (like relations between nodes).
            self.meshes.append(self.processMesh(mesh, scene))

    def processMesh(self, mesh : assimp_py.Mesh, scene : assimp_py.Scene) -> Mesh:

        # data to fill
        vertices = []
        indices = []
        textures = []

        # walk through each of the mesh's vertices
        for i in range(mesh.num_vertices):

            vertices += list(mesh.vertices[i])
            
            # normals
            if (mesh.normals):

                vertices += list(mesh.normals[i][:3])
                
            else:
                vertices += [0] * 3

            # texture coordinates
            if(mesh.texcoords and mesh.texcoords[0] and mesh.tangents and mesh.bitangents): # does the mesh contain texture coordinates?
                
                # a vertex can contain up to 8 different texture coordinates. We thus make the assumption that we won't 
                # use models where a vertex can have multiple texture coordinates so we always take the first set (0).
                vertices += list(mesh.texcoords[0][i][:2]) + list(mesh.tangents[i][:3]) + list(mesh.bitangents[i][:3])

            else:
                vertices += [0] * (2 + 3 + 3)

        # now wak through each of the mesh's faces (a face is a mesh its triangle) and retrieve the corresponding vertex indices.
        for i in range(mesh.num_faces):

            face = mesh.faces[i]
            # retrieve all indices of the face and store them in the indices vector
            indices += list(face)     

        # process materials
        material = scene.materials[mesh.material_index]    
        # we assume a convention for sampler names in the shaders. Each diffuse texture should be named
        # as 'texture_diffuseN' where N is a sequential number ranging from 1 to MAX_SAMPLER_NUMBER. 
        # Same applies to other texture as the following list summarizes:
        # diffuse: texture_diffuseN
        # specular: texture_specularN
        # normal: texture_normalN

        # 1. diffuse maps
        diffuseMaps = self.loadMaterialTextures(material, assimp_py.TextureType_DIFFUSE, "texture_diffuse")
        textures += diffuseMaps
        # 2. specular maps
        specularMaps = self.loadMaterialTextures(material, assimp_py.TextureType_SPECULAR, "texture_specular")
        textures += specularMaps
        # 3. normal maps
        normalMaps = self.loadMaterialTextures(material, assimp_py.TextureType_HEIGHT, "texture_normal")
        textures += normalMaps
        # 4. height maps
        heightMaps = self.loadMaterialTextures(material, assimp_py.TextureType_AMBIENT, "texture_height")
        textures += heightMaps
        
        # return a mesh object created from the extracted mesh data
        return Mesh(glm.array.from_numbers(glm.float32, *vertices), indices, textures)

    # checks all material textures of a given type and loads the textures if they're not loaded yet.
    # the required info is returned as a Texture struct.
    def loadMaterialTextures(self, mat : dict, type : int, typeName : str) -> List[Texture]:

        textures = []
        for i in range(list(mat["TEXTURES"].keys()).count(type)):
            texStr = mat["TEXTURES"][type][i]
            # check if texture was loaded before and if so, continue to next iteration: skip loading a new texture
            if not list(filter(lambda texture: texture.path == texStr, self.textures_loaded)):
                # if texture hasn't been loaded already, load it
                
                id = TextureFromFile(texStr, self.directory)
                type = typeName
                path = texStr

                texture = Texture(id, type, path)
                textures.append(texture)
                self.textures_loaded.append(texture) # store it as texture loaded for entire model, to ensure we won't unnecesery load duplicate textures.


        return textures


def TextureFromFile(path : str, directory : str, gamma : bool = False) -> int:

    filename = os.path.join(directory, path)
    
    textureID = glGenTextures(1)

    try:
        img = LOAD_IMAGE(filename)
        
        nrComponents = len(img.getbands())

        format = GL_RED if nrComponents == 1 else \
                 GL_RGB if nrComponents == 3 else \
                 GL_RGBA 

        glBindTexture(GL_TEXTURE_2D, textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, format, img.width, img.height, 0, format, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        img.close()

    except:

        print("Texture failed to load at path: " + path)

    return textureID

