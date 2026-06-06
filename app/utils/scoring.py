def _same_player(left, right):
    return (left or "").strip().casefold() == (right or "").strip().casefold()


def build_leaderboard(users, match_points, potm_points):
    rows = []

    for user in users:
        winner_correct = 0
        potm_correct = 0
        total = 0

        for prediction in user.predictions:
            if prediction.match.winner:
                total += 1
                if prediction.prediction == prediction.match.winner:
                    winner_correct += 1
            if prediction.match.potm_winner and _same_player(prediction.potm_prediction, prediction.match.potm_winner):
                potm_correct += 1

        rows.append(
            {
                "username": user.username,
                "favorite_team": user.favorite_team or "-",
                "points": (winner_correct * match_points) + (potm_correct * potm_points),
                "correct": winner_correct,
                "potm_correct": potm_correct,
                "scored_matches": total,
            }
        )

    rows.sort(key=lambda row: (-row["points"], -row["correct"], -row["potm_correct"], row["username"].lower()))
    return rows
