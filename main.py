import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

# Database setup
def create_db():
    conn = sqlite3.connect('healthcare.db')
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                    username TEXT, 
                    patient_name TEXT, 
                    father_name TEXT, 
                    address TEXT, 
                    mobile_number TEXT, 
                    age INTEGER, 
                    sex TEXT, 
                    FOREIGN KEY (username) REFERENCES users (username))''')

    conn.commit()
    conn.close()

# Load data for diagnosis
training = pd.read_csv('Data/Training.csv')
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
clf = DecisionTreeClassifier().fit(x_train, y_train)

description_list = {}
severityDictionary = {}
precautionDictionary = {}

# Functions to load dictionaries
def getDescription():
    global description_list
    with open('MasterData/symptom_Description.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            description_list[row[0]] = row[1]

def getSeverityDict():
    global severityDictionary
    with open('MasterData/symptom_severity.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) == 2:  # Check if the row has exactly two columns
                try:
                    severityDictionary[row[0]] = int(row[1])
                except ValueError:
                    print(f"Skipping row due to invalid severity value: {row}")
            else:
                print(f"Skipping invalid row: {row}")

def getPrecautionDict():
    global precautionDictionary
    with open('MasterData/symptom_precaution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            precautionDictionary[row[0]] = row[1:]

# Function for diagnosis
def diagnose(symptoms, days):
    symptoms_dict = {symptom: index for index, symptom in enumerate(cols)}
    input_vector = np.zeros(len(symptoms_dict))

    for symptom in symptoms:
        input_vector[symptoms_dict[symptom]] = 1
    disease = le.inverse_transform(clf.predict([input_vector]))[0]

    precautions = precautionDictionary.get(disease, ["No precautions available"])
    description = description_list.get(disease, "No description available")

    result_text = f"Possible Disease: {disease}\n\nDescription: {description}\n\nPrecautions:\n"
    result_text += "\n".join([f"- {p}" for p in precautions])
    messagebox.showinfo("Diagnosis Result", result_text)

def diagnose(symptoms, days):
    # Create an input vector from symptoms
    symptoms_dict = {symptom: index for index, symptom in enumerate(cols)}
    input_vector = np.zeros(len(symptoms_dict))
    
    # Mark symptoms that are present in the input
    for symptom in symptoms:
        if symptom in symptoms_dict:  # Check if symptom exists in the dictionary
            input_vector[symptoms_dict[symptom]] = 1
    
    # Predict the disease using the trained model
    disease = le.inverse_transform(clf.predict([input_vector]))[0]

    # Get the description of the disease
    description = description_list.get(disease, "No description available")

    # Get the precautions for the disease
    precautions = precautionDictionary.get(disease, ["No precautions available"])

    # Format the result text to display disease details, description, and precautions
    result_text = f"Possible Disease: {disease}\n\nDescription: {description}\n\nPrecautions:\n"
    result_text += "\n".join([f"- {p}" for p in precautions])

    # Display the result
    messagebox.showinfo("Diagnosis Result", result_text)

# Signup Functionality with additional details
def signup():
    def submit_signup():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        patient_name = patient_name_entry.get().strip()
        father_name = father_name_entry.get().strip()
        address = address_entry.get().strip()
        mobile_number = mobile_number_entry.get().strip()
        age = age_entry.get().strip()
        sex = sex_var.get().strip()

        if username and password and patient_name and father_name and address and mobile_number and age and sex:
            conn = sqlite3.connect('healthcare.db')
            c = conn.cursor()

            # Check if the username already exists
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                messagebox.showerror("Error", "Username already exists!")
            else:
                # Insert user and patient details into the database
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                c.execute("INSERT INTO patients (username, patient_name, father_name, address, mobile_number, age, sex) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (username, patient_name, father_name, address, mobile_number, age, sex))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                signup_window.destroy()  # Close signup window

            conn.close()
        else:
            messagebox.showerror("Error", "All fields are required!")

    signup_window = tk.Toplevel()
    signup_window.title("Signup")
    signup_window.geometry("500x600")

    frame = tk.Frame(signup_window, padx=20, pady=20)
    frame.pack(padx=20, pady=20)

    # Fields for username and password
    tk.Label(frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
    username_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    username_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(frame, width=40, font=("Arial", 12), show="*")
    password_entry.grid(row=1, column=1, pady=5)

    # Additional patient details
    tk.Label(frame, text="Patient Name:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    patient_name_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    patient_name_entry.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Father's Name:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
    father_name_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    father_name_entry.grid(row=3, column=1, pady=5)

    tk.Label(frame, text="Address:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
    address_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    address_entry.grid(row=4, column=1, pady=5)

    tk.Label(frame, text="Mobile Number:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5)
    mobile_number_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    mobile_number_entry.grid(row=5, column=1, pady=5)

    tk.Label(frame, text="Age:", font=("Arial", 12)).grid(row=6, column=0, sticky="w", pady=5)
    age_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    age_entry.grid(row=6, column=1, pady=5)

    tk.Label(frame, text="Sex (M/F):", font=("Arial", 12)).grid(row=7, column=0, sticky="w", pady=5)
    sex_var = tk.StringVar(value="M")
    sex_male = tk.Radiobutton(frame, text="Male", variable=sex_var, value="M", font=("Arial", 12))
    sex_female = tk.Radiobutton(frame, text="Female", variable=sex_var, value="F", font=("Arial", 12))
    sex_male.grid(row=7, column=1, sticky="w")
    sex_female.grid(row=7, column=2, sticky="w")

    tk.Button(frame, text="Submit", command=submit_signup, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=8, columnspan=2, pady=10)

# Signin Functionality with login
def signin():
    def submit_signin():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        conn = sqlite3.connect('healthcare.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()

        if user:
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            signin_window.destroy()  # Close signin window
            start_gui(username)  # Show the main application with the username
        else:
            messagebox.showerror("Error", "Invalid username or password")

        conn.close()

    signin_window = tk.Toplevel()
    signin_window.title("Signin")
    signin_window.geometry("400x300")

    frame = tk.Frame(signin_window, padx=20, pady=20)
    frame.pack(padx=20, pady=20)

    tk.Label(frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
    username_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    username_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(frame, width=40, font=("Arial", 12), show="*")
    password_entry.grid(row=1, column=1, pady=5)

    tk.Button(frame, text="Login", command=submit_signin, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=2, columnspan=2, pady=10)

def start_gui(username):
    # This will be the main application window after successful login
    main_window = tk.Tk()
    main_window.title("HealthCare Chatbot - Main Application")
    main_window.geometry("600x400")

    # Create a frame to hold the contents of the main window
    frame = tk.Frame(main_window, padx=20, pady=20)
    frame.pack(padx=20, pady=20)

    # Display a welcome message
    tk.Label(frame, text=f"Welcome, {username}!", font=("Arial", 14)).grid(row=0, columnspan=2, pady=20)

    # Option to diagnose symptoms
    tk.Label(frame, text="Enter Symptoms (comma separated):", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
    symptoms_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    symptoms_entry.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Enter number of days you have been sick:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    days_entry = tk.Entry(frame, width=40, font=("Arial", 12))
    days_entry.grid(row=2, column=1, pady=5)

    def diagnose_button_click():
        symptoms = symptoms_entry.get().strip().split(',')
        days = days_entry.get().strip()
        if symptoms and days.isdigit():
            diagnose(symptoms, days)
        else:
            messagebox.showerror("Error", "Please enter valid symptoms and days.")

    # Button to trigger diagnosis
    tk.Button(frame, text="Diagnose", command=diagnose_button_click, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=3, columnspan=2, pady=10)

    # Logout option
    tk.Button(frame, text="Logout", command=main_window.destroy, bg="#FF6347", fg="white", font=("Arial", 12), width=20).grid(row=4, columnspan=2, pady=10)

    main_window.mainloop()


# Main function to choose between Login and Signup
def login_signup_window():
    window = tk.Tk()
    window.title("Welcome to HealthCare Chatbot")
    window.geometry("400x300")

    frame = tk.Frame(window, padx=20, pady=20)
    frame.pack(padx=20, pady=20)

    tk.Label(frame, text="Welcome to HealthCare Chatbot", font=("Arial", 14)).grid(row=0, columnspan=2, pady=20)

    tk.Button(frame, text="Sign Up", command=signup, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=1, columnspan=2, pady=10)
    tk.Button(frame, text="Sign In", command=signin, bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=2, columnspan=2, pady=10)

    window.mainloop()

# Initialize the database
create_db()

# Start the login/signup window
login_signup_window()
