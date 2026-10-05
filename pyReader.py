from urllib.parse import urlparse
import requests

# STEP 1
def parse_pr_url(url):
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    return {
        "owner": parts[0],
        "repo": parts[1],
        "pr_number": parts[3]
    }


# STEP 2
def fetch_diff(url):
    diff_url = url + ".diff"
    response = requests.get(diff_url)

    return response.text


# STEP 3
def fetch_pull_request(owner, repo, pr_number):

    headers = {
        "User-Agent": "AIP444-Lab-03",
        "Accept": "application/vnd.github+json"
    }

    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    response = requests.get(api_url, headers=headers)

    return response.json()


# STEP 4
def fetch_comments(owner, repo, pr_number):

    headers = {
        "User-Agent": "AIP444-Lab-03",
        "Accept": "application/vnd.github+json"
    }

    api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/issues/{pr_number}/comments?per_page=100"
    )

    response = requests.get(api_url, headers=headers)

    return response.json()
   
# MAIN PROGRAM

url = input("Enter GitHub PR URL: ")

# Step 1
info = parse_pr_url(url)

print("\nOWNER:", info["owner"])
print("REPO:", info["repo"])
print("PR NUMBER:", info["pr_number"])

# Step 2
diff = fetch_diff(url)

print("\nFIRST 500 CHARACTERS OF DIFF:\n")
print(diff[:500])

# Step 3
pr_info = fetch_pull_request(
    info["owner"],
    info["repo"],
    info["pr_number"]
)

print("\nPR DETAILS")
print("Title:", pr_info["title"])
print("Author:", pr_info["user"]["login"])

# Step 4
comments = fetch_comments(
    info["owner"],
    info["repo"],
    info["pr_number"]
)

print("\nCOMMENTS")

for comment in comments[:3]:
    print("\nUser:", comment["user"]["login"])

    if comment["body"]:
        print("Comment:", comment["body"][:100])

# Step 5
interpretation = input(
    "\nWhat do you think this PR is changing, and why?\n> "
)

question = input(
    "\nWhat is one thing you don't understand yet?\n> "
)

# Step 6
student_understanding = f"""
<student-understanding>
    <interpretation>
        {interpretation}
    </interpretation>

    <question>
        {question}
    </question>
</student-understanding>
"""

print("\nSTUDENT UNDERSTANDING")
print(student_understanding)


# STEP 7

SYSTEM_PROMPT = """
You are a code-reading mentor.

Analyze the PR description, diff,
comments, and student understanding.

Output:

1. tl;dr
2. Your Understanding
3. Changes
4. Discussion
5. Learning
"""

# STEP 8

USER_PROMPT = f"""
<pull-request>
Title: {pr_info["title"]}
Author: {pr_info["user"]["login"]}
Description: {pr_info["body"]}
</pull-request>

<thread>
{comments}
</thread>

{student_understanding}

DIFF:
{diff[:5000]}
"""

# STEP 9

OPENROUTER_API_KEY = "PASTE_API_KEY_HERE"

response = requests.post("https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "google/gemini-3.5-flash-lite",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": USER_PROMPT
            }
        ]
    }
)

result = response.json()

print("\nAI REPORT\n")
print(result["choices"][0]["message"]["content"])

