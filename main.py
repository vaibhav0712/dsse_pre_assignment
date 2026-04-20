from pydriller import Repository, ModificationType

REPO_LINK = "https://github.com/apache/jclouds"
ISSUE_IDS = ["JCLOUDS-27", "JCLOUDS-43", "JCLOUDS-276", "JCLOUDS-435", "JCLOUDS-1548"]

# Aggregators for the entire set of issues
total_unique_commits = set()
total_unique_files = set()
global_unit_size = 0
global_complexity = 0
global_interfacing = 0

print(f"Starting analysis of {REPO_LINK}...")

# Single pass through the repository
for commit in Repository(REPO_LINK).traverse_commits():
    msg_lower = commit.msg.lower()

    # Check if this commit belongs to any of our target issues
    if any(issue.lower() in msg_lower for issue in ISSUE_IDS):

        # 1. Track Total Commits (Unique by Hash)
        total_unique_commits.add(commit.hash)

        # 2. Track Unique Files and DMM components
        for m in commit.modified_files:
            # Filter for Added, Modified, or Deleted
            if m.change_type in [
                ModificationType.ADD,
                ModificationType.MODIFY,
                ModificationType.DELETE,
            ]:
                path = m.new_path if m.new_path else m.old_path
                total_unique_files.add(path)

            # Aggregate DMM data from methods
            for method in m.changed_methods:
                global_unit_size += method.nloc
                global_complexity += method.complexity
                global_interfacing += len(method.parameters)

# Final Calculations
num_commits = len(total_unique_commits)
num_files = len(total_unique_files)

avg_files_per_commit = num_files / num_commits if num_commits > 0 else 0
total_dmm_sum = global_unit_size + global_complexity + global_interfacing
avg_dmm_metric = total_dmm_sum / num_commits if num_commits > 0 else 0

# Output Final Answers
print("\n" + "=" * 40)
print("FINAL ANALYSIS SUMMARY")
print("=" * 40)
print(f"1. Total commits analyzed:          {num_commits}")
print(f"2. Average number of files changed: {avg_files_per_commit:.2f}")
print(f"3. Average DMM metrics score:       {avg_dmm_metric:.2f}")
print("=" * 40)
