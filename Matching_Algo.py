import sqlite3
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
# Euclidean Distance for Age
def euclidean_distance(age1, age2):
    return np.sqrt((int(age1) - int(age2)) ** 2)

# Jaccard Similarity for Location and Interests
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Normalize Euclidean Distance (min-max normalization)
def normalize_euclidean(distance, min_value, max_value):
    return (distance - min_value) / (max_value - min_value)

# Final Matching Score (Weighted Combination)
def match_score(age1, age2, location1, location2, interests1, interests2, weight_age=0.3, weight_location_interests=0.7):
    # Step 1: Calculate Euclidean distance for age
    age_distance = euclidean_distance(age1, age2)

    # Normalize the age distance (assuming age range 18 to 100)
    normalized_age_distance = normalize_euclidean(age_distance, min_value=0, max_value=82)  # max_value is 100-18

    # Step 2: Calculate Jaccard similarity for location and interests
    jaccard_location = jaccard_similarity(location1, location2)
    jaccard_interests = jaccard_similarity(interests1, interests2)

    # Combine the two Jaccard similarities (you can also weight them differently if needed)
    jaccard_total = (jaccard_location + jaccard_interests) / 2

    # Step 3: Combine Euclidean distance and Jaccard similarity into a final score
    final_score = (weight_age * (1 - normalized_age_distance)) + (weight_location_interests * jaccard_total)

    return final_score

# Function to find top 10 matches
def find_top_matches(user_id):

    # Fetch the target user's details
    conn = sqlite3.connect('big_sample_db.db')
    cursor = conn.cursor()
    cursor.execute('''
         SELECT A.birthdate, A.location, GROUP_CONCAT(B.interest_id)
    FROM user A
    LEFT JOIN user_interests B ON A.user_id = B.user_id
    WHERE A.user_id = ?
    GROUP BY A.user_id
        ''', (user_id,))
    target_user = cursor.fetchone()

    if not target_user:
        return f"User with ID {user_id} not found."

    target_age, target_location, target_interests = target_user

    today = datetime.today()
    birthdate_dt = datetime.strptime(target_age, "%Y-%m-%d")
    target_age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))

    target_location_set = set(str(target_location).split(','))  # Convert to set
    target_interests_set = set(str(target_interests).split(','))  # Convert to set

    # Fetch all other users' details
    cursor.execute('''SELECT A.user_id, A.birthdate, A.location, GROUP_CONCAT(B.interest_id)
    FROM user A
    LEFT JOIN user_interests B ON A.user_id = B.user_id
    WHERE A.user_id != ?
    GROUP BY A.user_id''', (user_id,))
    all_users = cursor.fetchall()

    match_scores = []

    # Calculate match score for each user
    for user in all_users:
        other_id, other_age, other_location, other_interests = user

        # Calculate age and modify the list element directly
        birthdate_dt = datetime.strptime(str(other_age), "%Y-%m-%d")
        other_age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))


        other_location_set = set(str(other_location).split(','))
        other_interests_set = set(str(other_interests).split(','))

        # Calculate the match score using the previous logic
        score = match_score(
            target_age, other_age,
            target_location_set, other_location_set,
            target_interests_set, other_interests_set
        )

        # Append user and their score to the list
        match_scores.append((other_id, score))

    # Sort by match score in descending order and get the top 10 matches
    match_scores.sort(key=lambda x: x[1], reverse=True)
    top_matches = match_scores[:10]

    # Close the connection
    conn.close()

    return top_matches



print(find_top_matches("9e35fff0-7402-4e09-9089-4d542e9f70ea"))
