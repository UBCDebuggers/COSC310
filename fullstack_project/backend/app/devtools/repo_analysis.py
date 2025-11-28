from pydriller import RepositoryMining
from datetime import datetime

def analyze_repo(path='.'):
    commit_data = []
    file_change_count = {}

    for commit in RepositoryMining(path).traverse_commits():
        commit_info = {
            "hash": commit.hash,
            "author": commit.author.name,
            "date": commit.author_date,
            "msg": commit.msg,
            "modified_files": []
        }

        for m in commit.modifications:
            # Count file frequency
            file_change_count[m.filename] = file_change_count.get(m.filename, 0) + 1
            
            commit_info["modified_files"].append({
                "file": m.filename,
                "added": m.added,
                "removed": m.removed
            })

        commit_data.append(commit_info)

    return commit_data, file_change_count


if __name__ == "__main__":
    commits, file_freq = analyze_repo("..")  # Analyze entire backend repo

    print("\n=== TOP 5 MOST CHANGED FILES ===")
    for f, c in sorted(file_freq.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{f} → {c} commits")

    print("\n=== SAMPLE OF COMMITS ===")
    for c in commits[:5]:
        print(f"{c['hash']} | {c['author']} | {c['msg']}")
