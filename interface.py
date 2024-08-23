import tkinter as tk
from PIL import Image, ImageTk
import sqlite3

from terminal import fetch_all, user_exists
from User_class import User, Gender, Interest, Location, db_name

curr_user = None


def load_frame1():
    frame1.pack_propagate(False)

    logo_img = ImageTk.PhotoImage(file="logo.png")
    logo_widget = tk.Label(frame1, image=logo_img, bg="#EEA9B8")
    logo_widget.image = logo_img
    logo_widget.pack()
    ###############logo finished here
    ## label?
    # button :
    button1 = tk.Button(frame1,
                        text="Login",
                        font=("TkHeadingFont", 20),
                        bg="black",
                        fg="#DB7093",
                        cursor="hand2",
                        activebackground="#EE799F",
                        activeforeground="#EE799F",
                        command=lambda: open_login_interface()
                        )
    button1.pack(side="top", pady=10)
    # button1.grid(row=1, column=1, padx=10, pady=10)
    # button1.eval("tk::PlaceWindow . left")

    button2 = tk.Button(frame1,
                        text="Sign Up",
                        font=("TkHeadingFont", 20),
                        bg="#EE799F",
                        fg="#DB7093",
                        cursor="hand2",
                        activebackground="#EE799F",
                        activeforeground="#EE799F",
                        command=lambda: open_signup_interface()
                        )
    button2.pack(side="top", pady=10)


# open login window
def open_login_interface():
    # Create a new top-level window for the login interface
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("300x200")  # Adjust size as needed
    login_window.configure(bg="#EEA9B8")

    # Add login form elements (example)
    userid_label = tk.Label(login_window, text="Userid:")
    userid_label.pack(side="top", pady=10)
    userid_entry = tk.Entry(login_window)
    userid_entry.pack(side="top", pady=10)

    # Set current user

    login_button = tk.Button(login_window, text="Login", command=lambda: login(userid_entry.get()),
                             font=("TkHeadingFont", 20),
                             bg="#EE799F",
                             fg="#DB7093",
                             cursor="hand2",
                             activebackground="#EE799F",
                             activeforeground="#EE799F")
    login_button.pack(side="top", pady=10)


def login(user_id):
    global curr_user
    if user_exists(user_id) == True:
        curr_user = User.fetch_user(user_id)
        print('Login successful')
        after_login_interface()

    else:
        print('User not exist, Please create an account')
    return


# open sign up window
def open_signup_interface():
    signup_window = tk.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("400x500")  # Adjust size as needed
    signup_window.configure(bg="#EEA9B8")

    # Name
    tk.Label(signup_window, text="Name:", bg="#EEA9B8").pack(pady=5)
    name_entry = tk.Entry(signup_window)
    name_entry.pack()

    # Date of Birth
    tk.Label(signup_window, text="Date of Birth (YYYY-MM-DD):", bg="#EEA9B8").pack(pady=5)
    dob_entry = tk.Entry(signup_window)
    dob_entry.pack()

    # Location
    tk.Label(signup_window, text="Location:", bg="#EEA9B8").pack(pady=5)
    location_entry = tk.Entry(signup_window)
    location_entry.pack()

    # Gender
    tk.Label(signup_window, text="Gender:", bg="#EEA9B8").pack(pady=5)
    gender_var = tk.StringVar(value="Other")
    tk.Radiobutton(signup_window, text="Male", variable=gender_var, value="Male", bg="#EEA9B8").pack()
    tk.Radiobutton(signup_window, text="Female", variable=gender_var, value="Female", bg="#EEA9B8").pack()
    tk.Radiobutton(signup_window, text="Other", variable=gender_var, value="Other", bg="#EEA9B8").pack()

    # Interests
    tk.Label(signup_window, text="Interests (comma-separated):", bg="#EEA9B8").pack(pady=5)
    interests_entry = tk.Entry(signup_window)
    interests_entry.pack()

    # Sign Up Button
    signup_button = tk.Button(signup_window, text="Sign Up",
                              command=lambda: process_signup(name_entry.get(), dob_entry.get(),
                                                             location_entry.get(), gender_var.get(),
                                                             interests_entry.get()),
                              font=("TkHeadingFont", 20),
                              bg="#EE799F",
                              fg="#DB7093",
                              cursor="hand2",
                              activebackground="#EE799F",
                              activeforeground="#EE799F")
    signup_button.pack(pady=20)


def process_signup(name, dob, location, gender, interests):
    try:
        # Convert gender to integer as per your application's logic
        gender_int = 1 if gender == 'Male' else 2 if gender == 'Female' else 3

        # For location, you may need to convert to an integer or directly use the string,
        # depending on how your database or application logic is set up
        location_int = {
            "Toronto": 1,
            "New York": 2,
            "Los Angeles": 3,
            "San Francisco": 4,
            "Vancouver": 5,
            "Calgary": 6,
            "Edmonton": 7,
            "Seattle": 8
        }.get(location, 9)  # Default to 9 if location not found

        # Convert interests from a comma-separated string to a list of integers
        interest_map = {
            "Hiking": 1,
            "Biking": 2,
            "Swimming": 3,
            "Reading": 4,
            "Cooking": 5,
            "Travelling": 6,
            "Dancing": 7,
            "Singing": 8,
            "Yoga": 9,
            "Programming": 10,
            "Gaming": 11,
            "Playing an Instrument": 12
        }
        interests_int = [interest_map[interest.strip()] for interest in interests.split(",")]

        # Create a new user
        new_user = User.create_user(name, dob, gender_int, location_int, interests_int)

        # Display the user ID in a new window
        user_id_window = tk.Toplevel()
        user_id_window.title("User ID")
        user_id_window.geometry("300x150")
        user_id_window.configure(bg="#EEA9B8")

        tk.Label(user_id_window, text="Sign-Up Successful!", bg="#EEA9B8", font=("TkHeadingFont", 16)).pack(pady=10)
        tk.Label(user_id_window, text=f"Your User ID: {new_user.user_id}", bg="#EEA9B8",
                 font=("TkHeadingFont", 12)).pack(pady=5)
        tk.Label(user_id_window, text="Please save this User ID for future logins.", bg="#EEA9B8").pack(pady=10)

        # Automatically login the user
        login(new_user.user_id)

    except Exception as e:
        tk.messagebox.showerror("Sign-Up Error", str(e))

    print(
        f"Sign-up attempt with:\nName: {name}\nDOB: {dob}\nLocation: {location}\nGender: {gender}\nInterests: {interests}")

    print(f"Sign-up attempt with:\nName: {name}\nDOB: {dob}\nLocation: {location}\nGender: {gender}\nInterests: {interests}")

# Create a new top-level window for the login interface
def after_login_interface():
    after_login_window = tk.Toplevel()
    after_login_window.title("Login Successfully")
    after_login_window.geometry("300x200")  # Adjust size as needed
    after_login_window.configure(bg="#EEA9B8")

    profile_button = tk.Button(after_login_window, text="View Profile",
                               font=("TkHeadingFont", 20), bg="#EE799F", fg="#DB7093",
                               cursor="hand2", activebackground="#EE799F", activeforeground="#EE799F",
                               command=lambda: view())
    profile_button.pack(side="top", pady=10)

    logout_button = tk.Button(after_login_window, text="Log Out",
                              font=("TkHeadingFont", 20), bg="#EE799F", fg="#DB7093",
                              cursor="hand2", activebackground="#EE799F", activeforeground="#EE799F",
                              command=lambda: logout())
    logout_button.pack(side="top", pady=10)


# create "view profile interface":
def view_profile_interface():
    view_profile = tk.Toplevel()
    view_profile.title("Profile")
    view_profile.geometry("400x300")
    view_profile.configure(bg="#EEA9B8")
    global curr_user
    if curr_user:
        profile_info = curr_user.view_own_profile()

        # Display the profile information in the new window
        tk.Label(view_profile, text=f"Name: {profile_info['name']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Age: {profile_info['age']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Gender: {profile_info['gender']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Location: {profile_info['location']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Interests: {profile_info['interests']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Liked Users: {profile_info['liked_users']}", bg="#EEA9B8").pack(anchor='w', pady=5)
        tk.Label(view_profile, text=f"Matched Users: {profile_info['matches']}", bg="#EEA9B8").pack(anchor='w', pady=5)
    else:
        error_label = tk.Label(view_profile, text="No user logged in.", bg="#EEA9B8")
        error_label.pack(pady=20)


def view():
    # command here
    view_profile_interface()


def logout():
    global curr_user
    curr_user = None
    print("Logged out successfully")
    after_login_interface().destroy()


# initialize app
root = tk.Tk()
root.title("Matchi")
# root.eval("tk::PlaceWindow . center")

x = root.winfo_screenwidth() // 2
y = int(root.winfo_screenheight() * 0.1)
root.geometry('300x400+' + str(x) + "+" + str(y))

frame1 = tk.Frame(root, width=300, height=400, bg="#EEA9B8")
frame2 = tk.Frame(root, bg="#EEA9B8")
frame1.grid(row=0, column=0)
frame2.grid(row=0, column=0)

for frame in (frame1, frame2):
    frame.grid(row=0, column=0)

load_frame1()

# run app
root.mainloop()
