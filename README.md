# Complete Git Pipeline - User Guide

**File:** `pipeline_git.py`

## Description

I created this complete procedure that automates the entire Git initialization of a project, from configuration to the first push, including access token creation.

## Features

### `pipeline_git_complete(project_name, repository_url, username, user_email, access_token=None)`

This procedure automatically executes all the following steps:

## Pipeline Steps

### 1. Global Git Configuration
- I configure the global username
- I configure the global email

### 2. Local Repository Initialization
- I initialize Git (`git init`) if not already done
- I check if `.git` already exists

### 3. .gitignore Creation
- I create a complete `.gitignore` for Python
- I include exclusions for:
  - Python files (`__pycache__/`, `*.pyc`)
  - Virtual environments (`venv/`, `env/`)
  - IDE (`.vscode/`, `.idea/`)
  - OS (`.DS_Store`, `Thumbs.db`)
  - Temporary files (`*.tmp`, `*.log`)

### 4. Adding Files
- I add all files to staging (`git add .`)

### 5. First Commit
- I check if there are changes to commit
- I create the initial commit with the message "Initial commit - Project configuration"

### 6. Remote Repository Configuration
- I check if origin already exists
- I add the origin with the provided URL
- I handle token authentication if provided

### 7. Main Branch Configuration
- I check the current branch
- I rename it to "main" if necessary

### 8. Upstream Stream Setup
- I execute `git push -u origin main`
- I configure branch tracking

### 9. Instructions for Creating an Access Token

#### For GitLab:
1. I go to: `https://gitlab.com/-/user_settings/personal_access_tokens`
2. I click on "Add new token"
3. I fill in:
   - **Token name:** My project token
   - **Expiration date:** (optional)
   - **Scopes:** api, read_repository, write_repository
4. I click "Create personal access token"
5. **I COPY THE TOKEN** (it won't be displayed again)

#### For GitHub:
1. I go to: `https://github.com/settings/tokens`
2. I click "Generate new token" > "Generate new token (classic)"
3. I fill in:
   - **Note:** My project token
   - **Scopes:** repo (full control)
4. I click "Generate token"
5. **I COPY THE TOKEN**

### 10. Configuration with Token

To use the token, I have two options:

**Option 1 - URL with token:**
```bash
git remote set-url origin https://USERNAME:TOKEN@gitlab.com/user/repo.git
```

**Option 2 - Credential helper:**
```bash
git config --global credential.helper store
```
Then on the next push, I use the token as the password.

## Usage

### Interactive Mode
```bash
python3 pipeline_git.py
```
The script will ask me for:
- Project name
- Repository URL
- Git username
- Git email
- Access token (optional)

### Programming Mode
```python
from pipeline_git import pipeline_git_complete

# I execute the pipeline
result = pipeline_git_complete(
    project_name="MyProject",
    repository_url="gitlab.com/username/myproject.git",
    username="john doe",
    user_email="johndoe@example.com",
    access_token="my_secret_token"  # Optional
)

if result:
    print("Pipeline successful!")
else:
    print("Error in pipeline")
```

## Parameters

- **project_name** (str): The project/repository name
- **repository_url** (str): The remote repository URL (without https://)
- **username** (str): The Git username
- **user_email** (str): The Git user email
- **access_token** (str, optional): Access token if available

## Return Value

- **True**: If the entire pipeline completed successfully
- **False**: If an error occurred

## Error Handling

I implemented robust error handling:
- Checking element existence before modification
- Handling cases where Git is already configured
- Explicit error messages
- Continuation even in case of non-critical errors

## Use Cases

This pipeline is perfect when:
- I start a new Python project
- I want to automate Git configuration
- I need to configure multiple projects quickly
- I teach Git to other developers
- I want to standardize my Git configurations

## Security

**Important for tokens:**
- I never commit a token in the code
- I use environment variables for tokens
- I revoke unused tokens
- I use minimal required scopes

## Technologies Used

- **subprocess**: To execute Git commands
- **os**: To check file existence
- **Git**: Version control system
