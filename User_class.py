import sqlite3
import uuid
from datetime import datetime
from enum import Enum

db_name = 'big_sample_db.db'

def setup_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user(
                   user_id VARCHAR(36) PRIMARY KEY,
                   name TEXT NOT NULL,
                   birthdate TEXT NOT NULL,
                   gender INT NOT NULL,
                   location INT NOT NULL
                   )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS liked_users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id VARCHAR(36) NOT NULL,
                   liked_user_id VARCHAR(36),
                   FOREIGN KEY (user_id) REFERENCES users(user_id)
                   )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disliked_users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(36) NOT NULL,
                    disliked_user_id VARCHAR(36),
                    FOREIGN KEY (user_id) REFERENCES users(user_id))
                   ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(36) NOT NULL,
                    matched_user_id VARCHAR(36),
                    FOREIGN KEY (user_id) REFERENCES users(user_id))
                   ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_interests(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(36) NOT NULL,
                    interest_id INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id))
                   ''')
    conn.commit()
    conn.close()

setup_db()

class Gender(Enum):
    MALE = 1
    FEMALE = 2
    GENDERFLUID = 3

class Interest(Enum):
    HIKING = 1
    BIKING = 2
    SWIMMING = 3
    READING = 4
    COOKING = 5
    TRAVELLING = 6
    DANCING = 7
    SINGING = 8
    YOGA = 9
    PROGRAMMING = 10
    GAMING = 11
    PLAYING_AN_INSTRUMENT = 12

class Location(Enum):
    TORONTO = 1
    NEW_YORK = 2
    LOS_ANGELES = 3
    SAN_FRANCISCO = 4
    VANCOUVER = 5
    MONTREAL = 6
    CALGARY = 7
    EDMONTON = 8
    SEATTLE = 9

class User:
    def __init__(self,name,birthdate,gender_int,location_int,interests_int,liked_users = None,disliked_users = None,matches = None):
        self.user_id = str(uuid.uuid4())
        #use uuid for security reasons, stored as varchar(36) in database
        self.name = name
        self.birthdate = str(datetime.strptime(birthdate, "%Y-%m-%d").date())
        self.age = self.get_age()
        self.gender_int = gender_int
        self.location_int = location_int
        self.interests_int = interests_int
        self.liked_users = liked_users if liked_users is not None else []
        self.disliked_users = disliked_users if disliked_users is not None else []
        self.matches = matches if matches is not None else []

    def get_age(self):
        today = datetime.today()
        birthdate_dt = datetime.strptime(self.birthdate, "%Y-%m-%d")
        age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))
        return age

    #this method both creates and inserts a user
    def create_user(name,birthdate,gender_int,location_int,interests_int):
        user = User(name,birthdate,gender_int,location_int,interests_int)
        if user.age < 18:
            raise ValueError("You must be over 18 to use this app")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
            
        cursor.execute('''
        INSERT INTO user(user_id,name,birthdate,gender,location) VALUES(?,?,?,?,?)''',
        (user.user_id,user.name,user.birthdate,user.gender_int,user.location_int))
        
        for interest in user.interests_int:
            cursor.execute('''
            INSERT INTO user_interests(user_id, interest_id) VALUES(?, ?)''',
            (user.user_id, interest))
        conn.commit()
        conn.close()

        return user

    def fetch_user(user_id):
    # it is faster to fetch from individual tables rather than merging tables into a big table first then querying
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM user WHERE user_id = ?''', (user_id,))
            user_info = cursor.fetchone()

            cursor.execute('''SELECT interest_id FROM user_interests WHERE user_id = ?''', (user_id,))
            user_interests = [row[0] for row in cursor.fetchall()]

            cursor.execute('''SELECT liked_user_id FROM liked_users WHERE user_id = ?''', (user_id,))
            liked_users = [row[0] for row in cursor.fetchall()]

            cursor.execute('''SELECT disliked_user_id FROM disliked_users WHERE user_id = ?''', (user_id,))
            disliked_users = [row[0] for row in cursor.fetchall()]

            cursor.execute('''SELECT matched_user_id FROM matches WHERE user_id = ?''', (user_id,))
            matches = [row[0] for row in cursor.fetchall()]

            user = User(user_info[1], user_info[2], user_info[3], user_info[4], user_interests,liked_users,disliked_users,matches)

            user.user_id = user_info[0]
            user.age = user.get_age()

            conn.commit()
            conn.close()

            return user
        
        except Exception as e:
            print(f"An error has occured: {e}")

    def view_own_profile(self):
        #this function should ONLY be used to view profiles, querying should be done with the fetch_user method since it returns a User object

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT name FROM user WHERE user_id IN ({})'''.format(','.join(['?']*(len(self.liked_users)))), self.liked_users,) 
        liked_users_names = [row[0] for row in cursor.fetchall()]
        cursor.execute('''
        SELECT name FROM user WHERE user_id IN ({})'''.format(','.join(['?']*(len(self.matches)))), self.matches,)
        matched_users_names = [row[0] for row in cursor.fetchall()]
        conn.commit()
        conn.close()


        profile = {
            "name": self.name,
            "age": self.age,
            "birthdate": self.birthdate,
            "gender": self.gender(),
            "location": self.location(),
            "interests": self.interests(),
            "liked_users": liked_users_names,
            "matches": matched_users_names,
        }
        
        return profile
    
    def view_other_profile(self):
        profile = {
            "name": self.name,
            "age": self.age,
            "birthdate": self.birthdate,
            "gender": self.gender(),
            "location": self.location(),
            "interests": self.interests()
        }
        return profile
    
    def gender(self):
        return Gender(self.gender_int).name
    
    def interests(self):
        return [Interest(interest).name for interest in self.interests_int]
    
    def location(self):
        return Location(self.location_int).name
    
    def check_interation(self,other_user):
        if other_user.user_id in self.liked_users or other_user.user_id in self.disliked_users or other_user.user_id in self.matches:
            return True
        else:
            return False

    def like_user(self,other_user):
        if self.check_interation(other_user):
            return None
        else:
            self.liked_users.append(other_user.user_id)
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO liked_users(user_id, liked_user_id) VALUES(?, ?)''', (self.user_id, other_user.user_id))
            if self.user_id in other_user.liked_users:
                self.matches.append(other_user.user_id)
                other_user.matches.append(self.user_id)
                cursor.execute('''INSERT INTO matches(user_id, matched_user_id) VALUES(?, ?)''', (self.user_id, other_user.user_id))
                cursor.execute('''INSERT INTO matches(user_id, matched_user_id) VALUES(?, ?)''', (other_user.user_id, self.user_id))
                conn.commit()
                print("You have a match!")
            conn.commit()
            conn.close()


    def dislike_user(self,other_user):
        if self.check_interation(other_user):
            return None
        else:
            self.disliked_users.append(other_user.user_id)
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO disliked_users(user_id, disliked_user_id) VALUES(?, ?)''', (self.user_id, other_user.user_id))
            conn.commit()
            conn.close()

    def delete_user(self):
        #this doesn't delete the user from another user's liked_users, disliked_users, or matches if they are stored in memory, but it does delete them from the database. So when a user logs back in the deleted user will be removed when the fetch_user method is called.
        conn = sqlite3.connect(db_name)
        # conn.execute('BEGIN EXCLUSIVE')
        cursor = conn.cursor()
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        try:
            conn.execute('BEGIN TRANSACTION') #if one query fails everything gets rolled back.

            cursor.execute('''
            DELETE FROM user WHERE user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM user_interests WHERE user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM liked_users WHERE liked_user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM liked_users WHERE user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM disliked_users WHERE disliked_user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM disliked_users WHERE user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM matches WHERE matched_user_id = ?''', (self.user_id,))
            cursor.execute('''
            DELETE FROM matches WHERE user_id = ?''', (self.user_id,))

            conn.commit()
            print("User deleted successfully")

        except Exception as e:
            conn.rollback()
            print(f"An error has occurred: {e}")

        finally:
            conn.close()

    def update_user(self, name, birthdate, gender_int, location_int, interests_int):
        if not name or not birthdate or not gender_int or not location_int or not interests_int:
            return "Error: Profile update missing fields"
        
        conn = sqlite3.connect(db_name)
        # conn.execute('BEGIN EXCLUSIVE')
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE user SET name = ?, birthdate = ?, gender = ?, location = ? WHERE user_id = ?''', (name, birthdate, gender_int, location_int, self.user_id))

        cursor.execute('''
        DELETE FROM user_interests WHERE user_id = ?''', (self.user_id,))
        for interest in interests_int:
            cursor.execute('''
            INSERT INTO user_interests(user_id, interest_id) VALUES(?, ?)''', (self.user_id, interest))
        
        conn.commit()
        conn.close()

        self = User.fetch_user(self.user_id)
        #this returns a fresh user object with the updated info directly from the DB.
        return self
        

    def remove_liked_users(self,user_position):
        # when a user sees their profile and their list of likes, they will only see names. We want them to type in 0, 1, 2 etc. to remove a like from the list
        # for example, if jenny wants to remove the first person she liked, she will type in 0. The will looik like jenny.remove_liked_users(0). This will give us the id of the person she wants to remove from her liked list. 
        self.liked_users.sort()

        user_id_to_remove = self.liked_users[user_position]
        self.liked_users.remove(user_id_to_remove)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN TRANSACTION')
            
            cursor.execute('''
            DELETE FROM liked_users WHERE user_id = ? AND liked_user_id = ?''', (self.user_id,user_id_to_remove,))
            if user_id_to_remove in self.matches:
                cursor.execute('''
                DELETE FROM matches WHERE user_id = ? AND matched_user_id = ?''', (self.user_id, user_id_to_remove,))
                cursor.execute('''
                DELETE FROM matches WHERE user_id = ? AND matched_user_id = ?''', ( user_id_to_remove,self.user_id,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"An error has occurred: {e}")
            
        finally:
            conn.close()

    def remove_matched_users(self,user_position):
        user_id_to_remove = self.matches[user_position]
        self.matches.remove(user_id_to_remove)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN TRANSACTION')
            
            cursor.execute('''
            DELETE FROM liked_users WHERE user_id = ? AND liked_user_id = ?''', (self.user_id,user_id_to_remove,))
            cursor.execute('''
            DELETE FROM matches WHERE user_id = ? AND matched_user_id = ?''', (self.user_id, user_id_to_remove,))
            cursor.execute('''
            DELETE FROM matches WHERE user_id = ? AND matched_user_id = ?''', ( user_id_to_remove,self.user_id,))
            
            conn.commit()
            print("Deletion successful")
            
        except Exception as e:
            conn.rollback()
            print(f"An error has occurred: {e}")
            
        finally:
            conn.close()






        
