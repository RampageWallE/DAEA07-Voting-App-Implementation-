def manhattan(rating1, rating2):
    distance = 0

    for key in rating1:
        if key in rating2:
            distance += abs(rating1[key]-rating2[key])
    return distance

def computeNearesNeighbor(userid, users):
    distances = {}
    try: 
        for user in users:
            if user != userid:
                distance = manhattan(users[user], users[userid])
                distances[user] = distance
        sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1]))
        if distance == {}:
            return {"error": "No data to compare"}, 404 
        return sorted_distances, 200
    except Exception as e: 
        return {"error": "No data to compare"}, 404  