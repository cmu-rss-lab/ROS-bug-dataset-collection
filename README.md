# ROS Bug Dataset Collection

Tools for collecting a bug dataset focused on behavioral architecture miscomposition bugs in ROS (Robot Operating System).

## Getting Started

### Prerequisites
- Docker installed on your machine.
- GPU support for running machine learning models (optional, but recommended).
- Python 3.8.10 installed.

### Setting Up the Llama Model
The Llama model is used for bug verification and filtering. To set up and run the Llama model:

1. **Run the Docker container**: Pull and start the Ollama Docker image to serve the Llama model.
   ```sh
   docker pull ollama/ollama:0.4.7
   docker run --gpus all -d --name ollama -p 11434:11434 -v /home/siyanwu/ollama_verify_bug/ollama_models:/root/.ollama ollama/ollama
   ```

2. **Start the Llama model**:
   ```sh
   docker exec -it ollama ollama run llama3
   ```

### Running the Commit Difference Script
The `commit_diff.py` script processes commit differences for a given repository and helps identify behavioral bugs.

To run the script:

1. Ensure the Docker container is running, as described above.
2. Run the `commit_diff.py` script with the desired repository as an argument:
   ```sh
   python3 commit_diff.py <Owner/repo>
   ```
   Replace `<Owner/repo>` with the GitHub repository name in the format `Owner/repo`, e.g., `autowarefoundation/autoware`.

### Example
```sh
python3 commit_diff.py autowarefoundation/autoware
```

## Arguments
- `repo_name`: The GitHub repository name in the format `'Owner/repo'` (e.g., `autowarefoundation/autoware`).
