import os
import base64
import json
import http.client

# 🔹 Set your GitHub credentials
GITHUB_TOKEN = "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"
REPO = "isaac-einstein36/final_project"
FILE_PATH = "/Users/sierrabasic/Library/CloudStorage/OneDrive-TheOhioStateUniversity/Ohio State/Classes/SP2025/5194 - Smart Products/Design Projects/Final Project/MasterBookings.csv"  # Update this path to your local file
GITHUB_FILE_PATH = "MasterBookings.csv"
BRANCH = "main"

# 🔹 Read and encode file content
with open(FILE_PATH, "rb") as file:
    content = base64.b64encode(file.read()).decode()

# 🔹 GitHub API endpoint for the file
url = f"/repos/{REPO}/contents/{GITHUB_FILE_PATH}"

# 🔹 Headers for authentication and content type
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "User-Agent": "GitHub-File-Updater",
    "Accept": "application/vnd.github.v3+json"
}

# 🔹 Step 1: Get file's SHA to delete it (if it exists)
conn = http.client.HTTPSConnection("api.github.com")
conn.request("GET", url, headers=headers)
response = conn.getresponse()
response_data = response.read().decode()

if response.status == 200:
    # File exists, we need to delete it first
    file_data = json.loads(response_data)
    sha = file_data['sha']

    # 🔹 Step 2: Delete the file from the repository using the SHA
    delete_data = {
        "message": "Delete existing file before re-uploading",
        "sha": sha,
        "branch": BRANCH
    }

    conn.request("DELETE", url, body=json.dumps(delete_data), headers=headers)
    delete_response = conn.getresponse()
    delete_response_data = delete_response.read().decode()

    if delete_response.status == 200:
        print("File deleted successfully.")
    else:
        print(f"Error deleting file: {delete_response.status}, {delete_response_data}")
else:
    # If file doesn't exist, skip deletion
    print("File doesn't exist. Proceeding with upload...")

# 🔹 Step 3: Upload the new file to GitHub
conn = http.client.HTTPSConnection("api.github.com")
data = json.dumps({
    "message": "Automated update",
    "content": content,
    "branch": BRANCH
})

conn.request("PUT", url, body=data, headers=headers)

# 🔹 Get response
response = conn.getresponse()
response_data = response.read().decode()

# 🔹 Print response (for debugging)
print(response.status, response.reason)
print(response_data)

# 🔹 Close the connection
conn.close()
