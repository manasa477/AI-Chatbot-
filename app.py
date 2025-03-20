import tkinter as tk
from tkinter import messagebox
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
import csv
from sklearn.model_selection import train_test_split
from sklearn import preprocessing

# Load data
training = pd.read_csv('Data/Training.csv')
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
clf = DecisionTreeClassifier().fit(x_train, y_train)

# Global variables
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

# GUI Initialization
def start_gui():
    root = tk.Tk()
    root.title("Healthcare ChatBot")
    root.geometry("500x500")

    # User input form
    tk.Label(root, text="Enter Your Name:").pack(pady=5)
    name_entry = tk.Entry(root, width=40)
    name_entry.pack(pady=5)

    tk.Label(root, text="Enter Symptoms (comma-separated):").pack(pady=5)
    symptoms_entry = tk.Entry(root, width=40)
    symptoms_entry.pack(pady=5)

    tk.Label(root, text="Duration of Symptoms (in days):").pack(pady=5)
    days_entry = tk.Entry(root, width=40)
    days_entry.pack(pady=5)

    # Diagnosis button
    def on_diagnose():
        name = name_entry.get().strip()
        symptoms = symptoms_entry.get().strip().split(',')
        days = days_entry.get().strip()

        if not name or not symptoms or not days.isdigit():
            messagebox.showerror("Error", "Please provide valid inputs!")
            return
        
        days = int(days)
        diagnose(symptoms, days)

    tk.Button(root, text="Diagnose", command=on_diagnose, bg="green", fg="white").pack(pady=20)

    root.mainloop()

# Load data
getDescription()
getSeverityDict()
getPrecautionDict()

# Start GUI
start_gui()
