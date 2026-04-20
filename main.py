from pydriller import Repository, ModificationType

REPO_LINK = "https://github.com/apache/jclouds"
ISSUE_IDS = ["JCLOUDS-27", "JCLOUDS-43", "JCLOUDS-276", "JCLOUDS-435", "JCLOUDS-1548"]

total_unique_commits = set()
total_unique_files = set()

dmm_unit_size = {"low": 0, "total": 0}
dmm_complexity = {"low": 0, "total": 0}
dmm_interfacing = {"low": 0, "total": 0}

UNIT_SIZE_THRESHOLD = 15  # methods <= 15 LOC are low-risk
COMPLEXITY_THRESHOLD = 5  # cyclomatic complexity <= 5 is low-risk
INTERFACING_THRESHOLD = 2  # <= 2 parameters is low-risk


def matches_issue(commit_msg: str, issue_ids: list[str]) -> bool:
    """Strict case-insensitive match: checks both uppercase and lowercase of the ID."""
    for issue in issue_ids:
        if issue.upper() in commit_msg or issue.lower() in commit_msg:
            return True
    return False


print(f"Starting analysis of {REPO_LINK}...")

for commit in Repository(REPO_LINK).traverse_commits():
    if not matches_issue(commit.msg, ISSUE_IDS):
        continue

    total_unique_commits.add(commit.hash)

    for m in commit.modified_files:
        try:
            if m.change_type in (
                ModificationType.ADD,
                ModificationType.MODIFY,
                ModificationType.DELETE,
            ):
                path = m.new_path if m.new_path else m.old_path
                total_unique_files.add(path)

            for method in m.changed_methods:
                nloc = method.nloc or 0
                complexity = method.complexity or 0
                params = len(method.parameters)

                dmm_unit_size["total"] += nloc
                dmm_complexity["total"] += complexity
                dmm_interfacing["total"] += params

                if nloc <= UNIT_SIZE_THRESHOLD:
                    dmm_unit_size["low"] += nloc

                if complexity <= COMPLEXITY_THRESHOLD:
                    dmm_complexity["low"] += complexity

                if params <= INTERFACING_THRESHOLD:
                    dmm_interfacing["low"] += params

        except Exception as e:
            print(f"  [warn] skipping file in commit {commit.hash[:7]}: {e}")

num_commits = len(total_unique_commits)
num_files = len(total_unique_files)

avg_files_per_commit = num_files / num_commits if num_commits > 0 else 0


def dmm_ratio(bucket: dict) -> float:
    return bucket["low"] / bucket["total"] if bucket["total"] > 0 else 0.0


dmm_us = dmm_ratio(dmm_unit_size)
dmm_cc = dmm_ratio(dmm_complexity)
dmm_if = dmm_ratio(dmm_interfacing)
avg_dmm = (dmm_us + dmm_cc + dmm_if) / 3

print("\n" + "=" * 50)
print("FINAL ANALYSIS SUMMARY")
print("=" * 50)
print(f"1. Total commits analyzed:          {num_commits}")
print(f"2. Unique files changed:            {num_files}")
print(f"3. Avg files changed per commit:    {avg_files_per_commit:.2f}")
print(f"4. DMM Unit Size score:             {dmm_us:.3f}")
print(f"5. DMM Cyclomatic Complexity score: {dmm_cc:.3f}")
print(f"6. DMM Interfacing score:           {dmm_if:.3f}")
print(f"7. Average DMM score:               {avg_dmm:.3f}  (0=worst, 1=best)")
print("=" * 50)
