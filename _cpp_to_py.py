import sys

import re, time

INCLUDE_PATTERN = "#include <([^>]*)>"

ARGUMENT_PATTERN = "(^[A-Za-z0-9_ ]+?)\\s*\\*?\\s*(\\w+)$"

VOID_FUNCTION_PATTERN = "^void (.+?)\\((.*?)\\)$"

INT_FUNCTION_PATTERN = "^int (.+?)\\((.*?)\\)$"

CURLY_BRACKETS_PATTERN = "^\\s*(?:{|})\\s*$"

COUT_PATTERN = "std::cout << (.+) << std::endl"

VARIABLE_PATTERN = "^(\\s*)[A-Za-z0-9_: *]*?(\\w+\\s*=\\s*.+)$"

IF_ELSE_WHILE_PATTERN = "if\\s*\\(.*\\)|else|while\\s*\\(.*\\)"

FOR_PATTERN = "for \\(unsigned int i = 0 i < ([a-zA-Z0-9_.:\\(\\)]+) i\\+\\+\\)"

LEN_PATTERN = "(\\w+)\\.size\\(\\)"

FLOAT_PATTERN = "([0-9]+\\.[0-9]+)f"

INFO_LOG_PATTERN = "(glGet(?:Shader|Program)InfoLog)\\((\\w+),\\s*[0-9]+,\\s*None,\\s*(\\w+)\\)"

FILESYSTEM_PATTERN = "FileSystem::getPath\\(\"resources\\/textures\\/(.+?)\"\\).c_str\\(\\)"

SHADER_SOURCE_PATTERN = "glShaderSource\\((\\w+),\\s*[0-9]*,\\s*&(\\w+),\\s*None\\)"

COMPILE_STATUS_PATTERN = "(glGet(?:Program|Shader)iv)\\((\\w+),\\s*(\\w+),\\s*&(\\w+)\\)"

GL_GEN_PATTERN = "(glGen\\w+)\\(([0-9]+),\\s*&?(\\w+)\\)"

GL_DELETE_PATTERN = "(glDelete(?:VertexArrays|Buffers))\\(1,\\s*&(\\w+)\\)"

ARRAY_SIZEOF_PATTERN = "sizeof\\((\\w+)\\), &?(\\w+)"

ARRAY_PATTERN = "float (\\w+)\\[\\] = {(.+?),? ?(\\s*#[^\\n]+)?\\n\\n"

APPLE_PATTERN = "#ifdef __APPLE__\\s*\\n(\\s*)glfwWindowHint\\(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE\\)\\s*#endif"

TRUE_PATTERN = "([^\\w\\d_])true([^\\w\\d_])"
FALSE_PATTERN = "([^\\w\\d_])false([^\\w\\d_])"

DOUBLE_PATTERN = "([^\\w\\d_])double([^\\w\\d_])"

CAMERA_MOVEMENT_PATTERN = "([^\\w\\d_])(FORWARD|BACKWARD|LEFT|RIGHT)([^\\w\\d_])"

CLASS_INIT_PATTERN = "(^ *)([a-zA-Z0-9_:]+) ([a-zA-Z0-9_]+)(\\([^=\\n]*\\));\\s*$"

FIRST_IMPORTS_PATTERN = "^.*import glm"

IMPORTS_ONLY_TEXT = "import platform, ctypes"

IMPORTS_LOAD_IMAGE_TEXT = """import platform, ctypes, os

# the relative path where the textures are located
IMAGE_RESOURCE_PATH = "../../../resources/textures/"

# function that loads and automatically flips an image vertically
LOAD_IMAGE = lambda name: Image.open(os.path.join(IMAGE_RESOURCE_PATH, name)).transpose(Image.FLIP_TOP_BOTTOM)
"""

pil_imported = False

glm_imported = False

def replace_with_func(content, pattern, func, flags = 0):
    match = re.search(pattern, content, flags = flags)
    if match:
        replacement = func(match)
        return content[:match.start()] + replacement + replace_with_func(content[match.end():], pattern, func, flags=flags)
    return content

def format_arguments_with_typing(content):
    arguments = re.split("\\s*,\\s*", content)

    replaced = map(lambda arg: replace_with_func(arg, ARGUMENT_PATTERN, lambda m: f"{m.group(2)}: {m.group(1)}"), arguments)

    return ", ".join(replaced)

def include_replacer(matcher):
    global glm_imported, pil_imported
    original_content = matcher.group(1)
    if original_content == "glad/glad.h":
        return "from OpenGL.GL import *"
    elif original_content == "GLFW/glfw3.h":
        return "from glfw.GLFW import *\n\nfrom glfw import _GLFWwindow as GLFWwindow"
    elif original_content == "stb_image.h":
        pil_imported = True
        return "from PIL import Image"
    elif original_content == "learnopengl/shader_s.h":
        return "from shader_s import Shader"
    elif original_content == "learnopengl/shader_m.h":
        return "from shader_m import Shader"
    elif original_content == "learnopengl/shader.h":
        return "from shader import Shader"
    elif original_content == "learnopengl/model.h":
        return "from model import Model"
    elif original_content == "learnopengl/camera.h":
        return "from camera import Camera, Camera_Movement"
    elif original_content in ("learnopengl/filesystem.h",):
        return ""
    elif original_content.startswith("glm"):
        if not glm_imported:
            glm_imported = True
            return "import glm"
        return ""
    elif original_content == "iostream":
        return IMPORTS_LOAD_IMAGE_TEXT if pil_imported else IMPORTS_ONLY_TEXT
    else:
        print(f"Unknown include {original_content}")
        return original_content

def try_import_replacer(matcher):
    imports = matcher.group()
    imports_indented = " " * 4 + imports.replace("\n", "\n" + " " * 4)

    return f"try:\n{imports_indented}\n\nexcept ImportError:\n    import requirements\n\n{imports_indented}"

for file_path in sys.argv[1:]:
    file_ = open(file_path)
    file_content = file_.read()
    file_.close()

    file_content = replace_with_func(file_content, CLASS_INIT_PATTERN, lambda m: f"{m.group(1)}{m.group(3)} = {m.group(2)}{m.group(4)}", flags = re.MULTILINE)

    file_content = file_content \
        .replace("//", "#") \
        .replace("&&", "and") \
        .replace(";", "") \
        .replace("!", "not ") \
        .replace("not =", "!=") \
        .replace("not \"", "!\"") \
        .replace("push_back", "append") \
        .replace("std::to_string", "str") \
        .replace("NULL", "None") \
        .replace("(void*)0", "None") \
        .replace("(void*)", "ctypes.c_void_p") \
        .replace("sizeof(float)", "glm.sizeof(glm.float32)")

    file_content = re.sub(CURLY_BRACKETS_PATTERN, "", file_content, flags = re.MULTILINE)

    file_content = replace_with_func(file_content, FLOAT_PATTERN, lambda m: f"{m.group(1)}")

    file_content = replace_with_func(file_content, TRUE_PATTERN, lambda m: f"{m.group(1)}True{m.group(2)}")

    file_content = replace_with_func(file_content, FALSE_PATTERN, lambda m: f"{m.group(1)}False{m.group(2)}")

    file_content = replace_with_func(file_content, DOUBLE_PATTERN, lambda m: f"{m.group(1)}float{m.group(2)}")

    file_content = replace_with_func(file_content, CAMERA_MOVEMENT_PATTERN, lambda m: f"{m.group(1)}Camera_Movement.{m.group(2)}{m.group(3)}")

    file_content = replace_with_func(file_content, VARIABLE_PATTERN, lambda m: f"{m.group(1)}{m.group(2)}", flags = re.MULTILINE)

    file_content = replace_with_func(file_content, INFO_LOG_PATTERN, lambda m: f"{m.group(3)} = {m.group(1)}({m.group(2)})")

    file_content = replace_with_func(file_content, GL_GEN_PATTERN, lambda m: f"{m.group(3)} = {m.group(1)}({m.group(2)})")

    file_content = replace_with_func(file_content, GL_DELETE_PATTERN, lambda m: f"{m.group(1)}(1, ({m.group(2)},))")

    file_content = replace_with_func(file_content, COMPILE_STATUS_PATTERN, lambda m: f"{m.group(4)} = {m.group(1)}({m.group(2)}, {m.group(3)})")

    file_content = replace_with_func(file_content, SHADER_SOURCE_PATTERN, lambda m: f"glShaderSource({m.group(1)}, {m.group(2)})")

    file_content = replace_with_func(file_content, VOID_FUNCTION_PATTERN, lambda m: f"def {m.group(1)}({format_arguments_with_typing(m.group(2))}) -> None:", flags = re.MULTILINE)

    file_content = replace_with_func(file_content, INT_FUNCTION_PATTERN, lambda m: f"def {m.group(1)}({format_arguments_with_typing(m.group(2))}) -> int:", flags = re.MULTILINE)

    file_content = replace_with_func(file_content, COUT_PATTERN, lambda m: f"print({m.group(1).replace('<<', '+')})")

    file_content = replace_with_func(file_content, FILESYSTEM_PATTERN, lambda m: f"\"{m.group(1)}\"")

    file_content = replace_with_func(file_content, ARRAY_SIZEOF_PATTERN, lambda m: f"{m.group(1)}.nbytes, {m.group(2)}.ptr")

    file_content = replace_with_func(file_content, ARRAY_PATTERN, lambda m: f"{m.group(1)} = glm.array(glm.float32, {m.group(2)}){m.group(3) if m.group(3) else ''}\n\n", flags = re.DOTALL)

    file_content = replace_with_func(file_content, IF_ELSE_WHILE_PATTERN, lambda m: f"{m.group()}:").replace("else: if", "elif")

    file_content = replace_with_func(file_content, LEN_PATTERN, lambda m: f"len({m.group(1)})")

    file_content = replace_with_func(file_content, FOR_PATTERN, lambda m: f"for i in range({m.group(1)}):")

    file_content = replace_with_func(file_content, INCLUDE_PATTERN, include_replacer)

    file_content = replace_with_func(file_content, APPLE_PATTERN, lambda m: f"{m.group(1)}if (platform.system() == \"Darwin\"): # APPLE\n{m.group(1)}    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)")

    file_content = file_content.replace("::", ".")

    file_content = replace_with_func(file_content, FIRST_IMPORTS_PATTERN, try_import_replacer, flags = re.DOTALL)

    file_content += "\n\nmain()\n"
    
    file_ = open(file_path.replace(".cpp", ".py"), "w")
    file_.write(file_content)
    file_.close()

print("DONE!")
time.sleep(1)
