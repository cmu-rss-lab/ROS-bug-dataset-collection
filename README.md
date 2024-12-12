# ROS Bug Dataset Collection

Tools for collecting a bug dataset focused on behavioral architecture miscomposition bugs in ROS (Robot Operating System).

## Prerequisites

- Docker installed on your machine
- Python 3.8.10
- Pipenv
- GPU support for running machine learning models (optional, but recommended)

## Setup

### 1. Clone the Repository
```sh
git clone <your-repository-url>
cd <repository-name>
```

### 2. Install Dependencies
```sh
pipenv install
```

### 3. Set Up GitHub Token

1. **Create a GitHub Personal Access Token**:
   - Visit [GitHub Token Settings](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
   - Generate a token with appropriate repository access permissions

2. **Run the Setup Script**:
   ```sh
   bash setup.sh
   ```
   - The script will prompt you to enter your GitHub Personal Access Token
   - It creates a `.env` file with secure, restricted permissions

### 4. Set Up Llama Model

1. **Start Ollama Docker Container**:
   ```sh
   docker compose up -d
   ```
   Note: If your machine does not have a GPU, you need to adjust the compose.yml file by uncommenting the following lines to remove GPU requirements:
   # deploy:
   #   resources:
   #     reservations:
   #       devices:
   #         - driver: nvidia
   #           count: 1
   #           capabilities: [gpu]

2. **Initialize Llama Model**:
   ```sh
   docker exec -it ollama_service ollama run llama3
   ```

## Usage

### Running Commit Difference Analysis

To analyze commit differences for a specific repository:

```sh
pipenv run python commit_diff.py <Owner/repo>
```

#### Example
```sh
pipenv run python commit_diff.py autowarefoundation/autoware
```

### Output

After running the script, a CSV file will be generated with the following format:

**Filename**: `autoware_verified_commits.csv`

**Columns**:
- `link`: Direct link to the GitHub commit
- `answer`: Binary classification (True/False) indicating whether the commit represents a Behavioral Architecture Miscomposition Bug (BABC)
- `reason`: Detailed explanation of why the commit was classified as a BABC or not

**Example CSV Contents**:
```
link,answer,reason
https://github.com/autowarefoundation/autoware/commit/abc123,True,"Significant changes in node communication pattern indicating potential behavioral architecture miscomposition"
https://github.com/autowarefoundation/autoware/commit/def456,False,"Minor refactoring without substantial behavioral changes"
```

## Configuration

### Arguments
- `repo_name`: GitHub repository name in the format `'Owner/repo'`
  - Example: `autowarefoundation/autoware`

## Troubleshooting

- Ensure Docker is running before executing scripts
- Verify your GitHub token has the necessary permissions
- Check that Pipenv environment is activated
