import json

def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as file:
            return json.load(file)
    except:
        return []


def save_score(username, score, coins, distance):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": username,
        "score": score,
        "coins": coins,
        "distance": int(distance)
    })

    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:10]

    with open("leaderboard.json", "w") as file:
        json.dump(leaderboard, file, indent=4)