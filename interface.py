import tkinter as tk
from PIL import Image, ImageTk
import sqlite3

from User_class import User, Gender, Interest, Location, db_name
from termial import login

def load_frame1():
    frame1.pack_propagate(False)

    logo_img = ImageTk.PhotoImage(file = "logo.png")
    logo_widget = tk.Label(frame1, image = logo_img, bg="#EEA9B8")
    logo_widget.image = logo_img
    logo_widget.pack()
    ###############logo finished here
    ## label?
    #button :
    button1 = tk.Button(frame1, 
                text="Login",
                font = ("TkHeadingFont",20),
                bg = "black",
                fg = "#DB7093",
                cursor = "hand2",
                activebackground = "#EE799F",
                activeforeground = "#EE799F",
                command = lambda:open_login_interface()
                )
    button1.pack(side="top", pady=10)
    #button1.grid(row=1, column=1, padx=10, pady=10)
    #button1.eval("tk::PlaceWindow . left")

    button2 = tk.Button(frame1, 
            text="Sign Up",
            font = ("TkHeadingFont",20),
            bg = "#EE799F",
            fg = "#DB7093",
            cursor = "hand2",
            activebackground = "#EE799F",
            activeforeground = "#EE799F",
            command = lambda:open_signup_interface()
            )
    button2.pack(side="top", pady=10)

#open login window
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

    curr_user = None

    login_button = tk.Button(login_window, text="Login", command=lambda:login(userid_entry.get()),
            font = ("TkHeadingFont",20),
            bg = "#EE799F",
            fg = "#DB7093",
            cursor = "hand2",
            activebackground = "#EE799F",
            activeforeground = "#EE799F")
    login_button.pack(side="top", pady=10)


#open sign up window
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
                            font = ("TkHeadingFont",20),
                            bg = "#EE799F",
                            fg = "#DB7093",
                            cursor = "hand2",
                            activebackground = "#EE799F",
                            activeforeground = "#EE799F")
    signup_button.pack(pady=20)

def process_signup(name, dob, location, gender, interests):
    # Add your sign-up logic here
    print(f"Sign-up attempt with:\nName: {name}\nDOB: {dob}\nLocation: {location}\nGender: {gender}\nInterests: {interests}")


def after_login_interface():
    # Create a new top-level window for the login interface
    after_login_window = tk.Toplevel()
    after_login_window.title("Login Successfully")
    after_login_window.geometry("400x300")  # Adjust size as needed
    after_login_window.configure(bg="#EEA9B8") 


    browse_button = tk.Button(after_login_window, text="Browse Users",
            font = ("TkHeadingFont",20),bg = "#EE799F",fg = "#DB7093",
            cursor = "hand2",activebackground = "#EE799F",activeforeground = "#EE799F")
    browse_button.pack(side="top", pady=10)

    profile_button = tk.Button(after_login_window, text="View Profile",
            font = ("TkHeadingFont",20),bg = "#EE799F",fg = "#DB7093",
            cursor = "hand2",activebackground = "#EE799F",activeforeground = "#EE799F")
    profile_button.pack(side="top", pady=10)

    like_button = tk.Button(after_login_window, text="Liked Users",
            font = ("TkHeadingFont",20),bg = "#EE799F",fg = "#DB7093",
            cursor = "hand2",activebackground = "#EE799F",activeforeground = "#EE799F")
    like_button.pack(side="top", pady=10)

    match_button = tk.Button(after_login_window, text="Matches",
            font = ("TkHeadingFont",20),bg = "#EE799F",fg = "#DB7093",
            cursor = "hand2",activebackground = "#EE799F",activeforeground = "#EE799F")
    match_button.pack(side="top", pady=10)




#initialize app
root = tk.Tk()
root.title("Matchi")
#root.eval("tk::PlaceWindow . center")

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
after_login_interface()

#run app
root.mainloop()
