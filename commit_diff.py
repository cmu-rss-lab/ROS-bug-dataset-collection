import argparse
import requests
import os
import json, pandas as pd
import dotenv

dotenv.load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if GITHUB_TOKEN is None:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

base_endpoint = "http://localhost:11434/api"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_commits(repo_name):
    
    REPO_OWNER = repo_name.split("/")[0]
    REPO_NAME = repo_name.split("/")[1]
    
    base_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    params = {"per_page": 100}  # Number of commits per page (max 100)
    
    # List to store commit links
    commits = []
    
    # Paginate through all the commits
    while base_api_url:
        response = requests.get(base_api_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for commit in data:
                sha = commit["sha"]
                commits.append({
                    "owner": REPO_OWNER,
                    "repo": REPO_NAME,
                    "sha": sha
                })
            
            # Handle pagination by looking for 'next' link in the headers
            if "link" in response.headers:
                links = response.headers["link"].split(", ")
                next_link = None
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link[link.find("<") + 1:link.find(">")]
                        break
                base_api_url = next_link  # Continue to the next page if available
            else:
                base_api_url = None  # No more pages to fetch
        else:
            print(f"Failed to fetch commits. Status code: {response.status_code}")
            break
    return commits
    
    
def fetch_prompts(commits):
    # os.makedirs(f"prompts", exist_ok=True)
    prompts = []
    # Loop through the commits to extract the diff and generate prompts
    for commit in commits:
        owner = commit["owner"]
        repo = commit["repo"]
        sha = commit["sha"]
    
        # Construct the API URL for the specific commit
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        link = f"https://github.com/{owner}/{repo}/commit/{sha}"
    
        # Make the request to GitHub API to get detailed information about the commit
        response = requests.get(api_url, headers=headers)
    
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            commit_message = data.get("commit", {}).get("message", "No commit message provided.")
            files = data.get("files", [])
            
            # Write the prompt for each file
            file_changes = ""
            for file_info in files:
                file_name = file_info["filename"]
                patch = file_info.get("patch", "")
                file_changes += f"File Name: {file_name}\nCode Changes:\n{patch}\n\n"
    
            # Prepare the prompt
            prompt = (
                f"Commit link: {link}\n"
                f"Commit Message: {commit_message}\n"
                f"Changes:\n{file_changes}"
            )
            prompts.append({
                "link": link,
                "commit_message": commit_message,
                "combined_patch": file_changes
            })
    
            # Save the prompt to a file
            # output_file = f"prompts/{sha}.txt"
            # with open(output_file, "w") as f:
            #     f.write(prompt)
            print(f"Saved prompt for commit {sha}")
    
        else:
            print(f"Failed to fetch commit {sha} from {owner}/{repo}. Status code: {response.status_code}")
    return prompts
    

def post_chat(commit_message, code_changes):
    try:
        # Construct the description in the desired format
        description = (
            f"Commit Message: {commit_message}\n"
            f"Code Changes:\n{code_changes}\n\n"
        )

        # Send the request to the chat model
        res = requests.post(
            f"{base_endpoint}/chat",
            json={
                "model": "llama3.1",
                "stream": False,
                "format": "json",
                "messages": [
                    {
                        "role": "system",
                        "content": """
                            You are a senior robotics software engineer specializing in advanced bug finding. You are checking whether a commit falls into the following description:
                                1. It describes or fixes a bug. This means it does not ONLY add new functionality and features, but deals with unexpected or incorrect behavior of the system.
                                2. The bug is a behavior architecture composition bug specifically related to inconsistent topic names, which manifests as incorrect or mismatched communication between components in a ROS-based system.
                                
                            The key characteristics of an inconsistent topic name bug are as follows:
                                - The commit message contains certain keywords that indicate potential topic inconsistency, such as:
                                    ["topic rename", "fix topic", "correct topic", "topic inconsistency", "incorrect topic name", "change topic", "topic mismatch", "change publisher", "update subscriber", "topic name typo fix", "change subscriber topic", "change publisher topic", "update topic"]
                                - The commit affects files related to ROS topics, such as:
                                    - If `.cpp` or `.yaml` files are changed together, this could indicate both a code change and a parameter change, potentially related to a topic renaming.
                                    - Changes involve files related to `ros::Publisher` or `ros::Subscriber` code. Check if variable names related to topics have been altered.
                                    - The changes involve only topic-related files or contain strings that match the format of ROS topics (e.g., `/topic_name`).

                            Note: The provided code changes follow the standard Git diff format. In the diff format:
                                - Lines starting with `+` indicate code that has been **added**.
                                - Lines starting with `-` indicate code that has been **removed**.

                            Your answer should be in the following format:
                            
                            {
                                "answer": True/False,
                                "reason": {{ Short description of the reason for your judgement. }}
                            }
                        """,
                    },
                    {"role": "user", "content": description},
                ],
            },
        )
        # Parse response from the API
        res_obj = res.json()
        content = res_obj.get("message").get("content")
        if len(json.loads(content).values()) != 2:
            answer, reason = "Need manual verification", "Response with wrong format"
        else:
            answer, reason = json.loads(content).values()
        return answer, reason
    except Exception as e:
        print(f"Error: {e}")
        return "Need manual verification", f"Error: {e}"
    
    
def main(repo_name):
    commits = fetch_commits(repo_name) 
    prompts = fetch_prompts(commits)

    verified_results = {}
    for prompt in prompts:
        link = prompt["link"]
        print("start verifying", link)
        answer, reason = post_chat(prompt['commit_message'], prompt['combined_patch'])
        result = {"answer": answer, "reason": reason}
        verified_results[link] = result
        print("finish verifying", answer, reason)
    
    
    df = pd.DataFrame.from_dict(verified_results, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['link', 'answer', 'reason']
    
    # Save DataFrame to a CSV file
    name = repo_name.split('/')[1]
    csv_filename = f"{name}_verified_commits.csv"
    df.to_csv(csv_filename, index=False)
    
    print(f"Results saved to {csv_filename}")
    
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process commit differences.")
    parser.add_argument("repo_name", type=str, help="Repository name in the format 'Owner/repo'")
    args = parser.parse_args()
    main(args.repo_name)
