import os, re

f = open("master_requirements.dat", "r")
master_requirements = eval(f.read())
f.close()

def find_requirements(path):
    f = open(path, "r")
    content = f.read()
    f.close()

    requirements_out = "wheel\n"

    added_something = False

    for pattern in master_requirements:
        if re.search(pattern, content):
            requirements_out += f"{master_requirements[pattern]}\n"
            added_something = True

    if not added_something:
        return None

    return requirements_out

for chapter in os.listdir("src"):
    path = f"src/{chapter}"
    if not os.path.isdir(path):
        continue
    for exercise in os.listdir(f"src/{chapter}"):
        basedir = os.path.join("src", chapter, exercise)
        if not os.path.isdir(basedir):
            continue
        
        _, ext = os.path.splitext(exercise)
        python_file = f"{ext[1:]}.py"

        python_file_path = os.path.join(basedir, python_file)

        if os.path.exists(python_file_path):
            requirements = find_requirements(python_file_path)
            if requirements:
                f = open(os.path.join(basedir, "requirements.txt"), "w")
                f.write(requirements)
                f.close()
        
