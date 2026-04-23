import json

roles = ["finance", "engineering", "marketing", "employee"]
types = [
    {"type": "factoid", "count": 5},
    {"type": "multi-hop", "count": 3},
    {"type": "comparative", "count": 2}
]

data = []
counter = 1
for role in roles:
    for t in types:
        for i in range(t["count"]):
            data.append({
                "id": f"{role[:3]}_{counter:03d}",
                "collection": role,
                "question": f"Sample {t['type']} question {i+1} for {role}?",
                "ground_truth": f"This is the ground truth answer for {role} {t['type']} question {i+1}.",
                "context_chunks": [f"Sample context chunk for {role}."]
            })
            counter += 1

with open("d:/CodeBasics_Bootcamp/python/python-basics-practice/LiveSessions/Assignments/assignment1_vibecoding/backend/evaluation/ground_truth_40qa.json", "w") as f:
    json.dump(data, f, indent=2)
