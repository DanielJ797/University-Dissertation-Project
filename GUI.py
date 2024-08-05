import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import Text, Label 
import numpy as np
from PIL import Image, ImageTk
from data_collection_model import LocationData
from linear_regression_model import AgentTrainer
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from sqlalchemy import create_engine,text
from sqlalchemy.engine import reflection
from sqlalchemy.exc import SQLAlchemyError
from tkinter import font
import subprocess

print(tk.__file__)

# The command used to start Apache and MySQL through XAMPP
xampp_command = r"C:\xampp\xampp_start.exe"  # Starts both Apache and MySQL

# Executes XAMPP start command
try:
    subprocess.run(xampp_command, shell=True, check=True)
    print("XAMPP started successfully (Apache and MySQL)")
except subprocess.CalledProcessError as e:
    print("Error starting XAMPP:", e)


def createDatabase(db_name):
    connection_string = "mysql+pymysql://root@localhost/"
    engine = create_engine(connection_string, echo=True, future=True)

    sql_command = text(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    try:
        with engine.connect() as connection:
            connection.execute(sql_command)
            print(f"Database '{db_name}' created successfully.")
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        engine.dispose()

createDatabase('stations')


# Creates the GUI window
root = tk.Tk()
root.title("Weather Prediction Program")
root.resizable(width=False, height=False)

# Creates the canvas that the GUI will be placed on
canvas = tk.Canvas(root, height=600, width=1000, bg="#42bff5")
canvas.pack()

# Creates the frame which will contain all GUI elements
frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

# Loads the image using PIL
image1 = Image.open("location3.jpg")
image1 = image1.resize((25, 25),Image.Resampling.LANCZOS)
photo1 = ImageTk.PhotoImage(image1)

# Loads the image using PIL
image2 = Image.open("circle-with-i-1.png")
image2 = image2.resize((30, 30),Image.Resampling.LANCZOS)
photo2 = ImageTk.PhotoImage(image2)

# Positions latitude label and text box
latLabel = Label(frame, text="Latitude:", bg="white")
latLabel.place(relx=0.05, rely=0.05, relwidth=0.15)
latBox = Text(frame, bg="white", fg="black", width=10, height=1, pady=1)
latBox.place(relx=0.05, rely=0.1, relwidth=0.15)

# Positions longitude label and text box
longLabel = Label(frame, text="Longitude:", bg="white")
longLabel.place(relx=0.05, rely=0.2, relwidth=0.15)
longBox = Text(frame, bg="white", fg="black", width=10, height=1, pady=1)
longBox.place(relx=0.05, rely=0.25, relwidth=0.15)

# Positions the listbox for coordinate selection
listbox = tk.Listbox(frame, width=15, height=10)
listbox.place(relx=0.05, rely=0.35, relwidth=0.2, relheight=0.35)

# Creates a vertical scrollbar
scrollbar= ttk.Scrollbar(listbox, orient= 'vertical')
scrollbar.pack(side="right", fill="both")

listbox.config(yscrollcommand= scrollbar.set)
scrollbar.config(command= listbox.yview)

# Positions the tutorial text
tutorialLabel = Label(frame, text="Please enter some coordinates and confirm them using the “Choose Coordinates” button",
                 bg="white", justify=tk.LEFT, wraplength=450)
tutorialLabel.place(relx=0.3, rely=0.75, relwidth=0.6, relheight=0.2)


def getData():

    # Retrieves the text that has been entered into the coordinates boxes and converts them to floating points, then stored
    try:
        latV = float(latBox.get("1.0", "end-1c"))
        longV = float(longBox.get("1.0", "end-1c"))

        currentCoords = listbox.get(0, tk.END)
        test = "("+str(latV)+"),("+str(longV)+")"

        # Checks if the coordinates currently in the latiude/longitude text boxes are already in the coordinate list
        if test in currentCoords:
            print("This coordinate pair has already been chosen")
            return

        # If they arent, the listbox and advice text box are updated 
        updateListbox(latV,longV)        
        tutorialLabel.config(text="You can now make a prediction! Do this by selecting the coordinates you want in the list box and then pressing the “Make Predictions” button")

    except:
        print("An exception occurred")

    


def makePrediction():

    try:

        # Parses the string to get a usable pair of values 
        selected_value = listbox.get(listbox.curselection())
        coordList = selected_value.replace("(","").replace(")","").split(",")

        latV = float(coordList[0])
        longV = float(coordList[1])

        # Calculates the first date of the training set 
        currentD = datetime.now()
        newCurrentD = currentD.strftime('%Y-%m-%d')
        startD = currentD - relativedelta(months=5)
        newStartD = startD.strftime('%Y-%m-%d')

        # Retrieves the data that is needed to train the model
        location_instance = LocationData(latV,longV,str(newCurrentD),str(newStartD))
        forecastData = location_instance.getSunData(latV,longV,str(newCurrentD),str(newStartD))
        forecastData = forecastData.drop(columns='shortwave_radiation_instant')
        forecastData = forecastData.reset_index()

        # Calculates the new predicted test values using the training data
        agent_trainer = AgentTrainer(float(coordList[0]),float(coordList[1]))
        predY = agent_trainer.trainerFunction(forecastData)
        results = pd.DataFrame(np.zeros((8, 2)),columns=['Date','Solar Intensity'])

        # Creates an array containing dates and their corresponding predicted solar raditaion values
        for i in range(0,7):
    
            listDate = (currentD + relativedelta(days=i)).strftime('%Y-%m-%d')
            results.iloc[i,0] = listDate
            results.iloc[i,1] = predY[i]

        # Calls the funciton to display this array
        displayDataframe(results, tree)

        tutorialLabel.config(text="Here is the predicted amount of sunlight for the next 7 days! If you wish to do this for another location then select another coordinate pair in the list box and click the “Make Predictions” button")

    except Exception as e:
        print(f"An exception occurred")

def getTableNames():

    # Connects to the database to retrieve all the table names
    engine = create_engine("mysql+pymysql://root@localhost/stations")
    insp = reflection.Inspector.from_engine(engine)
    print(insp.get_table_names())

    return insp.get_table_names()


def locationButton():

    # Connects to a website that returns IP addresses and converts response into JSON
    response = requests.get('https://ipinfo.io')
    location_data = response.json()

    # Retrieves the latitude and longitude from this response
    location = location_data.get('loc', 'Location not found').split(',')
    latitude = location[0]
    longitude = location[1]

    # Clears the latitude text box so it can be used again
    latBox.delete("1.0","end")
    latBox.insert("1.0",latitude)

    # Clears the latitude text box so it can be used again
    longBox.delete("1.0","end")
    longBox.insert("1.0",longitude)

def tutorialButton():

    newFont = font.Font(weight="bold")

    # Creates the GUI window
    root2 = tk.Tk()
    root2.title("Weather Prediction Program")
    root2.resizable(width=False, height=False)

    # Creates the canvas that the GUI will be placed on
    canvas2 = tk.Canvas(root2, height=480, width=800)
    canvas2.pack()
    
    # Creates the frame which will contain all GUI elements
    frame2 = tk.Frame(root2, bg="white")
    frame2.place(relwidth=0.95, relheight=0.95, relx=0.025, rely=0.025)

    # Positioning step 1 label 
    latLabel = Label(frame2, text='Step 1)', bg="white", justify=tk.LEFT, font=newFont)
    latLabel.place(relx=0.05, rely=0.05)

    # Positioning step 1 instructions label 
    latLabel = Label(frame2, text='Enter the latitude and longitude of the location that you want to predict the amount of sunshine for.You can do this by either manually inputting the values or pressing the "Find my Location" button which will retrieve your current coordinates automatically!', 
                     bg="white", justify=tk.LEFT, wraplength=650)
    latLabel.place(relx=0.05, rely=0.125)

    # Positioning step 2 label 
    latLabel = Label(frame2, text='Step 2)', bg="white", justify=tk.LEFT, font=newFont)
    latLabel.place(relx=0.05, rely=0.275)
    
    # Positioning step 2 instructions label 
    latLabel = Label(frame2, text='Once the coordinates have been entered, press the "Choose Coordinates" button to save them in the list box below.', 
                     bg="white", justify=tk.LEFT, wraplength=650)
    latLabel.place(relx=0.05, rely=0.35)

    # Positioning step 3 label 
    latLabel = Label(frame2, text='Step 3)', bg="white", justify=tk.LEFT, font=newFont)
    latLabel.place(relx=0.05, rely=0.45)

    # Positioning step 3 instructions label 
    latLabel = Label(frame2, text='You will now be able to see your new coordinates in the list box, to make a prediction: click on the coordinates you eant to predict the amount of sunshine for and then press the "Make Prediction" button.', 
                     bg="white", justify=tk.LEFT, wraplength=650)
    latLabel.place(relx=0.05, rely=0.525)

    # Positioning step 3 label 
    latLabel = Label(frame2, text='Step 4)', bg="white", justify=tk.LEFT, font=newFont)
    latLabel.place(relx=0.05, rely=0.625)

    # Positioning step 3 instructions label 
    latLabel = Label(frame2, text='The results being shown in the table on the right are the predicted values for the next week in the chosen location!', 
                     bg="white", justify=tk.LEFT, wraplength=650)
    latLabel.place(relx=0.05, rely=0.7)
    
    # Positioning step 3 instructions label 
    latLabel = Label(frame2, text='You may now repeat from step 3 with another coordinate pair in the listbox or from step 1 and add a new location to make a prediction for.', 
                     bg="white", justify=tk.LEFT, font=('Helvetica', 10, 'bold'), wraplength=650)
    latLabel.place(relx=0.05, rely=0.85)
    

# Positioning the "get location" button
getCoords = tk.Button(frame,image=photo1, padx=10, pady=5, bg="white", command=locationButton)
getCoords.place(relx=0.23, rely=0.075, width=30, height=30)

# Positioning the tuorial button
getCoords = tk.Button(frame,image=photo2, padx=10, pady=5, bg="white", command=tutorialButton)
getCoords.place(relx=0.9, rely=0.775, width=40, height=40)

# Positioning the "choose coordinates" button
getCoords = tk.Button(frame, text="choose coordinates", padx=10, pady=5, fg="red", bg="white", command=getData)
getCoords.place(relx=0.05, rely=0.75, relwidth=0.2)

# Positioning the "make prediction" button
makePred = tk.Button(frame, text="make prediction", padx=10, pady=5, fg="red", bg="white", command=makePrediction)
makePred.place(relx=0.05, rely=0.85, relwidth=0.2)

# Positioning the Treeview for displaying results
tree = ttk.Treeview(frame, columns=("Date", "Solar Intensity"), show="headings")
tree.column("Date", width=150)
tree.column("Solar Intensity", width=150)
tree.place(relx=0.3, rely=0.05, relwidth=0.65, relheight=0.7)

def updateListbox(lat, long):

    # Converts the coordinates into a usable format and inserts them into the listbox
    entry = "("+str(lat)+"),("+str(long)+")"
    listbox.insert(tk.END, entry)


# Creates an engine which connects to our local database, we are using a local database to store 
engine = create_engine("mysql+mysqlconnector://root@localhost/stations")
connection = engine.connect()

previousCoords =  getTableNames()

# Loops through every coordinate pair in the local database and sends them to updateListbox to be added to the listbox
for i in range(len(previousCoords)):
    
    baseCoordList = previousCoords[i].replace("(","").replace(")","").split(",")

    baseLat = float(baseCoordList[0])
    baseLong = float(baseCoordList[1])

    updateListbox(baseLat,baseLong)


def displayDataframe(df, tree):
    
    # Clear the treeview
    for i in tree.get_children():
        tree.delete(i)
    
    # Set up new dataframe display
    tree["column"] = list(df.columns)
    tree["show"] = "headings"
    
    # Set the column headers
    for column in tree["column"]:
        tree.heading(column, text=column)
    
    df_rows = df.to_numpy().tolist()
    df_rows.pop()

    # Insert the data into the table
    for row in df_rows:
        tree.insert("", "end", values=row)

    tree.column("Date", width=150)
    tree.column("Solar Intensity", width=150)

# Clears the terminal so the user can see any error messages
print("\n" * 100)

root.mainloop()
