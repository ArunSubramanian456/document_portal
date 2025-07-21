## Create a new project folder on Windows


```
# Create a new project folder
mkdir <project_folder_name>

# Move into the project folder
cd <project_folder_name>

# Open VS Code
code .
```

## Conda Environment Setup

```
# Create a new Conda environment in project folder
conda create -p <env_name> python==3.10 -y

# Activate the environment
conda activate <path_of_the_env>

# Install dependencies
pip install -r requirements.txt
```

## Git Commands

```
# Intiliaze Git
git init

# Stage all files
git add .

# Commit Changes
git commit -m "<write your commit message>"

# Push to remote (after adding remote origin)
git push

# Cloning the repo
git clone https://github.com/ArunSubramanian456/document_portal
```
