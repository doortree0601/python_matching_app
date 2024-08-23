import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
from enum import Enum

from User_class import User, Gender, Interest, Location, db_name
from Matching_Algo import euclidean_distance, jaccard_similarity, normalize_euclidean, match_score, find_top_matches

# Set global current user
curr_user = None

# Login the user belongs to the current user id
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


# Get all user data store in a pandas df
def fetch_all():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''SELECT user_id from user''')
    all_id = cursor.fetchall()
    user_ids = [id[0] for id in all_id]
    res_1 = [User.fetch_user(i) for i in user_ids]  # Dorothy
    res = [{
        'id': user.user_id,
        'age': user.age,
        'location': user.location_int,
        'interests': user.interests_int
    } for user in res_1]
    users_df = pd.DataFrame(res)
    conn.close()
    return users_df


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

# Varify whether the input from the user is in the designed range
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
    location = input_validate('Please enter the number corresponding to your location: ',
                              [loca.value for loca in Location])

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

# Terminal interface
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
                    print('Login successful')
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
                        print(curr_user.view_own_profile()['liked_users'])
                        remove_index = input_validate('Please Enter the index of the user you want to remove: ',
                                                      [i for i in range(0, len(curr_user.liked_users))])
                        curr_user.remove_liked_users(remove_index)
                        print("\nLiked user updated")
                    else:
                        print('You have not liked anyone')
                else:
                    print('\nPlease Login')

            elif comd == '5':
                if curr_user is not None:
                    top_users = find_top_matches(curr_user.user_id)
                    for user in top_users:
                        matched_user = User.fetch_user(user[0])
                        print(matched_user.view_other_profile())
                        if matched_user:
                            sub_comd = input_validate(
                                'Enter 1 if you like the profile, or 2 if you dislike the profile:', [1, 2])
                            if sub_comd == 1:
                                print(f"Liking user: {matched_user.name}")
                                curr_user.like_user(matched_user)
                                print('liked')
                            elif sub_comd == 2:
                                curr_user.dislike_user(matched_user)
                                print('disliked')
                        else:
                            print('No Matched user')
                    print(curr_user.matches)

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
        print(f'Program closed')


#
if __name__ == '__main__':
    main()
