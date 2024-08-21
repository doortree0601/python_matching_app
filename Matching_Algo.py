import sqlite3
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
#from geopy.geocoders import Nominatim  # get long and lat of a location

def normalize(value, min_val, max_val):
  return (value - min_val) / (max_val - min_val)

def get_user_data(user_id):
    conn = sqlite3.connect('big_sample_db.db')
    cursor = conn.cursor()
    cursor.execute('''
         SELECT A.birthdate, A.location, GROUP_CONCAT(B.interest_id)
    FROM user A
    LEFT JOIN user_interests B ON A.user_id = B.user_id
    WHERE A.user_id = ?
    GROUP BY A.user_id
        ''', (user_id,))
    data = cursor.fetchone()

    if data:
        age = data[0]
        today = datetime.today()
        birthdate_dt = datetime.strptime(age, "%Y-%m-%d")
        age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))

        location = data[1]
        interests = data[2].split(',')  # Assuming interests are stored as a comma-separated string
        return (age, location,interests)

    return None
    conn.commit()
    conn.close()

  # Convert interests into a binary vector.
def vectorize_interests(interests, all_interests):
    interests_set = set(str(interests).split(','))
    return np.array([1 if interest in interests_set else 0 for interest in all_interests])

    #Normalize and vectorize age.
def vectorize_age(age, min_age, max_age):
    norm_age = normalize(age, min_age, max_age)
    return np.array([norm_age])


#Convert city name into a one-hot encoded vector


def vectorize_location(city_name):
    conn = sqlite3.connect('big_sample_db.db')
    cursor = conn.cursor()
    cursor.execute('''
             SELECT location FROM user
            ''')
    location = cursor.fetchone()
    city_to_vector = {location: np.array([1 if city == c else 0 for c in location]) for city in location}
    return city_to_vector.get(city_name, np.zeros(len(location)))

    #Calculate cosine similarity across all attributes
def calculate_cosine_similarity(user1_id, user2_id, all_interests, min_age, max_age):
    user1_data = get_user_data(user1_id)
    user2_data = get_user_data(user2_id)

    if not user1_data or not user2_data:
        return 0

    age1, city1, interests1 = user1_data
    age2, city2, interests2 = user2_data

    # Vectorize each attribute
    interests_vec1 = vectorize_interests(interests1, all_interests)
    interests_vec2 = vectorize_interests(interests2, all_interests)

    location_vec1 = vectorize_location(city1)
    location_vec2 = vectorize_location(city2)

    age_vec1 = vectorize_age(age1, min_age, max_age)
    age_vec2 = vectorize_age(age2, min_age, max_age)

    # Combine vectors
    full_vec1 = np.concatenate([interests_vec1, location_vec1, age_vec1])
    full_vec2 = np.concatenate([interests_vec2, location_vec2, age_vec2])

    # Calculate cosine similarity
    similarity = cosine_similarity([full_vec1], [full_vec2])[0][0]
    return similarity

#Find top N users with the highest cosine similarity

def find_best_matches(target_user_id, top_n=10):
    conn = sqlite3.connect('big_sample_db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT interest_id FROM user_interests')
    all_interests_set = set()
    for row in cursor.fetchall():
        all_interests_set.update(str(row[0]).split(','))
        all_interests = list(all_interests_set)

        # Get min and max values for age to normalize
        cursor.execute('SELECT min(birthdate), max(birthdate) FROM user')
        min_birthdate, max_birthdate = cursor.fetchone()

        today = datetime.today()
        min_birthdate_dt = datetime.strptime(min_birthdate, "%Y-%m-%d")
        max_birthdate_dt = datetime.strptime(max_birthdate, "%Y-%m-%d")
        min_age = today.year - min_birthdate_dt.year - ((today.month, today.day) < (min_birthdate_dt.month, min_birthdate_dt.day))
        max_age = today.year - max_birthdate_dt.year - ((today.month, today.day) < (max_birthdate_dt.month, max_birthdate_dt.day))
        # Get all users
        cursor.execute('SELECT user_id FROM user')
        all_users = [row[0] for row in cursor.fetchall()]

        conn.commit()
        conn.close()
        scores = []

        for user_id in all_users:
            if user_id != target_user_id:
                score = calculate_cosine_similarity(target_user_id, user_id, all_interests, min_age, max_age)
                scores.append((user_id, score))

        # Sort by score in descending order
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_n]

print(find_best_matches("4da99187-4188-4c55-b6fd-268c125795d4"))