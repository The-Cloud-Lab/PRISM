import os
import sys
import json
import openai

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_pr_description(diff_content, pr_number):
    
    prompt=""" Using the given code changes,

1.Analyze and give an overall score for the updated code based on Readability, Maintainability, and Clarity. 

The return format should be in the below json format:
{{
    "readability_score": “<score>”,
    "output": "<text explanation of the reason for the scoring and suggested improvements>”
}}

Be careful while analyzing the code. Make sure to identify all the code changes and double-check the answer. Use the checkboxes and scoring criteria below while assigning the score.

—

Checkboxes:
1. Clear Naming Conventions (Function and variable names are meaningful, self-explanatory and easy to understand.)
2. Documentation (Code includes meaningful inline comments explaining logic and purpose.)
3. Formatting & Styling (Code follows consistent indentation and spacing.)
4. Maintainability (Code is easy to extend or modify.)
5. Code Length (Logic is broken down into simpler parts.)

Scoring Criteria:
readability_score: 1 (Excellent) Code meets all readability, maintainability, and clarity standards. Naming is clear, documentation is informative, formatting is consistent, code structure is easy to modify, and functions are not excessively long.  
readability_score: 0 (Moderate) Code is largely readable and maintainable but has a scope for improvement.  
readability_score: -1 (Poor) Code is highly unreadable.

"""
    prompt+="""
    
2. Analyze and give an overall score for the updated code based on Robustness and Error handling. 

The return format should be in the below json format:
{{
    "robustness_score": “<score>”,
    "output": "<text explanation of the reason for the scoring and suggested improvements>”
}}

Be careful while analyzing the code. Make sure to identify all the code changes and double-check the answer. Use the checkboxes and scoring criteria below while assigning the score.

—

Checkboxes:
1. Error Finding (No syntax, runtime and logical errors in the code.)
2. Error Handling (Code uses `try-except` for handling exceptions properly if applicable)
3. Edge Cases (Correctly handles edge cases like extreme, unusual, or unexpected inputs)
4. Input Validation (Code checks for invalid inputs)
5. No Infinite Loops (Code ensures that loops have a proper termination condition to avoid endless execution if found)

Scoring Criteria:
	robustness_score: 1 (Excellent) No errors found and follows all the checkboxes.
	robustness_score: 0 (Moderate) No errors found and does not follow all the checkboxes. 
	robustness_score: - 1 (Poor) A lot of errors found and does not follow all the checkboxes.
 """
    prompt+="""

3. Analyze and give an overall score for the updated code based on Security and Vulnerability. 
The return format should be in the below json format:
{{
    "security_score": “<score>”,
    "output": "<text explanation of the reason for the scoring and suggested improvements>”
}}

Be careful while analyzing the code. Make sure to identify all the code changes and double-check the answer. Use the checkboxes and scoring criteria below while assigning the score.

—

Checkboxes:
1. No Security Threats Code does not have injection flaws like SQL injection, Code injection, Command injection, XSS and other injections, buffer overflows, insecure data storage, improper input validation, race conditions, logic flaws, authorization issues, information leakage, denial-of-service (DoS) vulnerabilities, unpatched software, misconfigurations, and hardcoded credentials)
2. No Authentication & Authorization issues
3. No Hard Coded Secrets (There is not  any hardcoded credentials, API keys, or sensitive information)
4. No Secure Dependencies (There is not outdated and insecure third-party libraries)
5. Proper Session Management (Session expiration is perfect and handle token handling securely)

Scoring Criteria:
	security_score: 1 (Excellent) No security or vulnerability issues and follows all the checkboxes.
	security_score: 0 (Moderate) A few security or vulnerability issues and mostly follows checkboxes.
	security_score: -1 (Poor) A lot of security and vulnerability issues and does not follows all checkboxes.
"""
    
    prompt+="""
    
4. And Give an overall score for the updated based on Performance and Efficiency. 

The return format should be in the below json format:
{{
    "performance_score": “<score>”,
    "output": "<text explanation of the reason for the scoring and suggested improvements>”
}}

Be careful while analyzing the code. Make sure to identify all the code changes and double-check the answer. Use the checkboxes and scoring criteria below while assigning the score.

—

Checkboxes:
1. Improved Time Complexity (Code runs more efficiently than before.)
2. Improved Space Complexity (Code uses less memory than before.)
3. No Redundant Computation (No unnecessary and unused loops, recalculations, or duplicate operations, methods, and variables)


Scoring Criteria:
performance_score: 1 (Excellent) The code has improved either time complexity or space complexity and there are no unnecessary computations. 
performance_score: 0 (Moderate) The code has not improved time or space complexity and slightly follows checkboxes.
performance_score: -1 (Poor) The code reduces the time or space complexity and does not follow any of the checkboxes.
"""    	
    prompt+=f""" code changes for the Pull Request ID {pr_number}:### Code Changes (Diff):{diff_content}"""
	
    return prompt
    
def analyze_with_llm(pr_number, prompt):
    try:
        message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2048,
        system="Respond only in JSON format with keys: efficiency_score and output.",
        messages=[{"role": "user", "content": prompt}]

   ) 
        print(f"\n===== Raw Response from LLM (PR_ID {pr_id}) =====\n")
        print(message.content[0].text)

        return message.content[0].text
    
    except Exception as e:
        print(f"Error processing prompt for {repo_name} PR_ID {pr_id}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    diff_file_path = sys.argv[1]
    pr_number = sys.argv[2]

    try:
        with open(diff_file_path, "r") as f:
            diff_content = f.read().strip()
        
        if not diff_content:
            print("Warning: Diff file empty.")
            pr_body = "No changes detected."
        else:
            prompt = generate_pr_description(diff_content, pr_number)
	    pr_body = analyze_with_llm(pr_number, prompt)

        with open("pr_description.txt", "w") as f:
            f.write(pr_body)

        print("PR description saved successfully.")

    except FileNotFoundError:
        print(f"Error: Diff file '{diff_file_path}' not found.")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)
