import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
from enum import Enum

#
from User_class import User, Gender, Interest, Location, db_name

curr_user = None
# Set current user

def login(user_id):
    global curr_user
    if curr_user is None and user_exists(user_id):
        curr_user = User.fetch_user(user_id)
        print('Login successful')
    else:
        print('User not exist, Please create an account')
    return


# Set Current user back to None
def logout():
    global curr_user
    if curr_user is None:
        print('You have not logged in!')
    else:
        curr_user = None
        print('You have logged out')
    return


# Check whether user exist in the database
def user_exists(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT user_id from user
    Where user_id = ?
    ''', (user_id,))
    res = cursor.fetchone()

    conn.close()
    return res is not None


# Get all user data store in a pandas df
def fetch_all():

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT user_id from user''')
    all_id = cursor.fetchall()
    user_ids = [id[0] for id in all_id]
    res_1 = [User.fetch_user(i) for i in user_ids] # Dorothy
    res = [{
        'id': user.user_id,
        'age': user.age,
        'location': user.location_int,
        'interests': user.interests_int
    }for user in res_1]
    users_df = pd.DataFrame(res)
    conn.close()
    return users_df

# Match Algorithm
# Same Location +10 points
# Age close greater/less than 5 years +5 points
# Number of Same interest + 2points each
# Not in like/dislike
def interest_score(curr_data, interests):
    # Find the intersection of interests between the current user and the user in the DataFrame
    same_interests = set(curr_data['interests']) & set(interests)

    # Calculate the score based on the number of shared interests
    return len(same_interests) * 2

def top_matching():
    curr_user_data={
        'id':curr_user.user_id,
        'age':curr_user.age,
        'location': curr_user.location_int,
        'interests': curr_user.interests_int
    }
    all_user_data = fetch_all()

    all_user_data['location_points'] = np.where(all_user_data['location'] == curr_user_data['location'], 10, 0)
    all_user_data['age_points'] = np.where(abs(all_user_data['age'] - curr_user_data['age']) <= 5, 5, 0)
    all_user_data['interest_points'] = all_user_data['interests'].apply(lambda i: interest_score(curr_user_data, i))
    all_user_data['total_score'] = all_user_data['location_points'] +all_user_data['age_points'] +all_user_data['interest_points']

    remove_like_dislike= all_user_data[~all_user_data['id'].isin(curr_user.liked_users + curr_user.disliked_users)]
    top_matches = remove_like_dislike.sort_values(by='total_score', ascending=False)
    top_10_matches = top_matches.head(10)['id'].tolist()
    return top_10_matches

# Check whether user exist in the database
def user_exists(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT user_id from user
    Where user_id = ?
    ''', (user_id,))
    res = cursor.fetchone()

    conn.close()
    return res is not None
# browse through the list of user_ids and return a user which is not in the user's liked/dislied list
# def browsing(user, lists_users):
#     like_set = set(user.liked_users)
#     dislike_set = set(user.disliked_users)
#     inter_like = set(lists_users).intersection(like_set)
#     inter_dislike = set(lists_users).intersection(dislike_set)
#     for id in lists_users:
#         if id not in (inter_like or inter_dislike):
#             return User.fetch_user(id)
#     return print('Come back tomorrow')


def input_validate(input_p, valid_range):
    while True:
        try:
            value = int(input(input_p))
            if value in valid_range:
                return value
            else:
                print(f'Invalid input. You should enter a number within the range {valid_range}.')
        except ValueError:
            print('Invalid input. Please enter a number.')


# Ask user to input all new information
def get_new_user_info():
    name = input('Please enter your name: ')

    while True:
        birthdate = input('Please enter your birthday (YYYY-MM-DD): ')
        try:

            birthdate_che = datetime.strptime(birthdate, "%Y-%m-%d")
            if datetime(1900, 1, 1) <= birthdate_che <= datetime(2024, 12, 31):
                break
            else:
                print('Date out of range. Please enter a date between Jan 1900 and Dec 2024.')
        except ValueError:
            print('Invalid date format. Please enter the date in YYYY-MM-DD format.')

    print('Please Select your gender:')
    for g in Gender:
        print(f'{g.name}: {g.value}')
    gender = input_validate('Please enter the number corresponding to your gender: ', [g.value for g in Gender])

    print('Please Select your location:')
    for loca in Location:
        print(f'{loca.name}:{loca.value}')
    location = input_validate('Please enter the number corresponding to your location: ', [loca.value for loca in Location])

    print('Please Select your interest:')
    for inter in Interest:
        print(f'{inter.name}: {inter.value}')
    while True:
        inter_input = input('Please enter the numbers of your interests, separated by space: ')
        interests = inter_input.split(' ')
        try:
            interests = [int(i) for i in interests]
            if all(i in [inter.value for inter in Interest] for i in interests):
                break
            else:
                print('Invalid input. Please enter valid numbers')
        except ValueError:
            print('Invalid input. Please enter numbers only.')

    result = [name, birthdate, gender, location, interests]
    return result


def main():
    global curr_user
    try:
        while True:
            print('\n Please select following options ')
            print('Login: (1)')
            print('Create new user: (2)')
            print('Edit user profile: (3)')
            print('Edit your liked user list (4)')
            print('Browse user profiles: (5)')  # Like or dislike after browsing
            print('View your profile (6)')
            print('Logout: (7)')
            print('Delete your account (8)')
            print('Close the program (9)')

            comd = input('Please enter the digit corresponding to the choice: ')

            if comd == '1' and curr_user is None:
                curr_id = input('Please enter your user id: ')
                if user_exists(curr_id):
                    login(curr_id)
                else:
                    print('\nUser not exist, Please create an account')

            elif comd == '2':
                if curr_user is None:
                    info = get_new_user_info()
                    new_user = User.create_user(info[0], info[1], info[2], info[3], info[4])
                    print(f'New user created, your user_id is: {new_user.user_id}')
                    curr_user = new_user
                    login(new_user.user_id) 
                # else:
                #     print('\nYou need to logout') DL: I don't think we need this since user will alwasy be created unless they exist the cli

            # upadte like lists
            elif comd == '3':
                if curr_user is not None:
                    new_res = get_new_user_info()
                    curr_user = curr_user.update_user(new_res[0], new_res[1], new_res[2], new_res[3], new_res[4])
                    # Update user liked list
                    print("\nProfile updated")
                else:
                    print('\nPlease Login')

            elif comd == '4':
                if curr_user is not None:
                    if len(curr_user.liked_users) > 0:
                        print(curr_user.view_other_profile()['liked_users'])
                        remove_index = int(input('Please Enter the index of the user you want to remove'))
                        curr_user.remove_liked_users(remove_index)
                        print("\nLiked user updated")
                    else:
                        print('You have not liked anyone')
                else:
                    print('\nPlease Login')

            elif comd == '5':
                if curr_user is not None:
                    top_users = ["efa8abbe-323e-4960-984b-30adec2f2335", "511e90a4-a1f1-4558-a37c-50a58fcc1b66", "b8bd979d-f827-4ffc-9af8-8fbabcadbd04"]
                    # find_best_matches(curr_user.user_id)  # Meghu - this should be debugged and refined, for now use a preset list of users

                    top_users = top_matching()
                    for user in top_users:
                        matched_user = User.fetch_user(user)
                        print(matched_user.view_other_profile())
                        if matched_user:
                            sub_comd = input_validate(
                                'Enter 1 if you like the profile, or 2 if you dislike the profile:', [1, 2])
                            print(f"sub_comd = {sub_comd}")
                            if sub_comd == 1:
                                print(f"Liking user: {matched_user.name}")
                                curr_user.like_user(matched_user)
                                print('liked')
                            elif sub_comd == 2:
                                curr_user.dislike_user(matched_user)
                                print('disliked')
                        else:
                            print('No Matched user')

                    # for i in range (len(top_users)):
                    #     user_shown = User.fetch_user(top_users[i])
                    #     print(User.view_other_profile(user_shown)) # -> Lily
                    #     sub_comd = input('Enter 1 if you like the profile, or 2 if you dislike the profile:')
                    #     if sub_comd == '1':
                    #         curr_user.like_user(user_shown)
                    #     if sub_comd == '2':
                    #         curr_user.dislike_user(user_shown)
                    #     else:
                    #         print('\nInvalid input')
                    #     i+=1


                    # for user in top_users:
                    #     matched_user = User.fetch_user(user)
                    #     print(matched_user.view_other_profile())

                    # if matched_user:
                    #     sub_comd = input('Enter 1 if you like the profile, or 2 if you dislike the profile:')
                    #     if sub_comd == '1':
                    #         curr_user.like(listed_user)  
                    #     if sub_comd == '2':
                    #         curr_user.dislike(listed_user) 
                    #     else:
                    #         print('\nInvalid input')

                else:
                    print('\nPlease Login')

            elif comd == '6':
                if curr_user is not None:
                    print(curr_user.view_own_profile())
                else:
                    print('\nPlease Login')

            elif comd == '7':
                logout()

            elif comd == '8':
                if curr_user:
                    curr_user.delete_user() 
                    logout()
                else:
                    print('\nPlease Login')

            elif comd == '9':
                return

            else:
                print('\nWrong input, try again')

    except Exception as e:
        print(f'{e}: Wrong input, try again')
        print('Program restarted, please login again')
    finally:
        print(f'Program restarts')

#
if __name__ == '__main__':
    main()

# a = User.fetch_user('4e785559-c2b7-481d-aecd-6f7dea332dea')
# b=User.fetch_user('a3d35860-f4c5-4a99-b960-3690182ef994')
