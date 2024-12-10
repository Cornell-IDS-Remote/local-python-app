import tkinter as tk
from tkinter import messagebox
import os
import yaml
from pymongo import MongoClient
import re
from bson.objectid import ObjectId
import yaml
from show_where_cars_go import show


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import subprocess

# Global state
num_cars = 0  # Placeholder for global state
entries_list = []  # To keep track of entry widgets for car inputs
segments_to_highlight = []

# MongoDB connection details
MONGO_URI = "mongodb+srv://admin:smartCityPassword@robocity.moph9.mongodb.net/?retryWrites=true&w=majority&appName=robocity"
DATABASE_NAME = "robocity"
COLLECTION_NAME = "uploads"

# Database connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
uploads_collection = db[COLLECTION_NAME]

def execute_commands():
    """Run two commands in separate command line interfaces."""
    try:
        subprocess.Popen(["echo", "ros2 launch vicon_receiver client.launch.py"]) 
        subprocess.Popen(["echo", "ros2 run ids3c_control main temp"]) 

        messagebox.showinfo("Success", "Commands executed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute commands: {e}")

username_collection = db['users']

def objectIDtoName(userid):

    try:
        # Query the database for the user with the given ObjectId
        user = username_collection.find_one({"_id": ObjectId(userid)})
        
        if user:
            # Return the concatenated firstName and lastName
            return f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        else:
            return "User not found."
    except Exception as e:
        # Handle errors, such as invalid ObjectId format
        return f"Error: {str(e)}"

def fetch_uploads():
    """Fetch entries from the 'uploads' collection."""
    return list(uploads_collection.find({}, {"_id": 1, "userId": 1, "carsFile": 1, "experimentFile": 1}))

def getNumberVehicles():
        
    yaml_file_path = "temp/Cars.yaml"

    # Look for pattern
    pattern = re.compile(r"""
    Vehicle\d+\s*:\s*\d+\s*
    """, re.VERBOSE)

    match_count = 0

    with open(yaml_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        match_count = len(pattern.findall(content))

    return match_count

def download_files(entry_id, cars_file, experiment_file):
    """Download files and save them in a new directory named 'temp'."""
    temp_dir = "temp"

    os.makedirs(temp_dir, exist_ok=True)

    cars_file_path = os.path.join(temp_dir, "Cars.yaml")
    experiment_file_path = os.path.join(temp_dir, "Experiment.yaml")

    try:
        with open(cars_file_path, "w", encoding="utf-8") as f:
            f.write(cars_file['data'])

        with open(experiment_file_path, "w", encoding="utf-8") as f:
            f.write(experiment_file['data'])

        messagebox.showinfo("Download Complete", f"Files for entry ID {entry_id} have been downloaded to '{temp_dir}'.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download files: {e}")

def create_car_inputs(plot, canvas_plot):
    """Populate the bottom-left frame with editable text slots based on num_cars."""
    for widget in car_input_frame.winfo_children():
        widget.destroy()

    global entries_list
    entries_list = []

    for i in range(num_cars):
        tk.Label(car_input_frame, text=f"Car {i + 1} ID:").pack(anchor="w", padx=10)
        entry = tk.Entry(car_input_frame)
        entry.pack(anchor="w", padx=10, pady=5)
        entries_list.append(entry)

    submit_button = tk.Button(car_input_frame, text="Submit", command=lambda: submit_car_inputs(plot, canvas_plot))

    submit_button.pack(pady=10)

def handle_upload_file(car_ids):
    print(car_ids)

    yaml_file = "temp/Cars.yaml"

    with open(yaml_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Match Vehicle entries (e.g., Vehicle1 : <integer>)
    pattern = re.compile(r"(Vehicle\d+\s*:\s*)\d+")
    
    matches = pattern.findall(content)
    if len(matches) != len(car_ids):
        raise ValueError("Number of Vehicle* entries does not match the number of provided integers.")

    def replace_with_new_id(match, replacement_iter=iter(car_ids)):
        return f"{match.group(1)}{next(replacement_iter)}"

    updated_content = pattern.sub(replace_with_new_id, content)

    with open(yaml_file, "w", encoding="utf-8") as file:
        file.write(updated_content)

def updateGlobalCarLocactions(num_cars, plot, canvas_plot):
    
    global segments_to_highlight
    segments_to_highlight = []

    with open("temp/Cars.yaml", "r") as file:
        content = file.read().replace('\t', '  ')
        content = re.sub(r"(Vehicle\d+\s*:\s*)\d+", r"\1", content)
        
        # need to handle all controllers since yamml file format uploaded is not ideal
        content = re.sub(r"(IDMFast\s*:\s*)IDM", r"\1", content)
        content = re.sub(r"(IDMSlow\s*:\s*)IDM", r"\1", content)

    data = yaml.safe_load(content)


    for i in range(num_cars):
        vehicle1_path_ref = data.get(f"Vehicle{i+1}", {}).get("Path")
        print(vehicle1_path_ref)

        if vehicle1_path_ref:
            path_segments = vehicle1_path_ref.get("Segments", None)
            if path_segments:
                segments_to_highlight.append(path_segments.split(',')[0]) 
            else:
                print("Route Error for {path_key}.")
        else:
            print("Vehicle path reference not found.")

    plot.clear()
    show(plot, segments_to_highlight) 
    canvas_plot.draw() 


init_state = True

def submit_car_inputs(plot, canvas_plot):
    """Handle car input submission."""
    car_ids = [entry.get() for entry in entries_list]
    print(f"Submitted car IDs: {car_ids}")
    messagebox.showinfo("Car IDs Submitted", f"Car IDs: {', '.join(car_ids)}")
    updateGlobalCarLocactions(num_cars, plot, canvas_plot)
    handle_upload_file(car_ids)

def set_num_cars_and_update_inputs(plot, canvas_plot):
    global num_cars
    num_cars = getNumberVehicles()
    create_car_inputs(plot, canvas_plot)


def display_main_screen():
    """Display the main GUI screen with database entries."""

    root = tk.Tk()
    root.title("Database Entries")
    root.geometry("1500x600")

    # Top-right frame: Matplotlib plot
    top_right_frame = tk.Frame(root)
    top_right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tk.Label(top_right_frame, text="Matplotlib Plot").pack()
    fig = Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(111)
    show(plot, segments_to_highlight)
    canvas_plot = FigureCanvasTkAgg(fig, master=top_right_frame)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    def refresh_entries():
        entries = fetch_uploads()
        for widget in frame.winfo_children():
            widget.destroy()

        if entries:
            for entry in entries:
                row_frame = tk.Frame(frame)
                row_frame.pack(fill="x", padx=5, pady=2)

                data1 = entry.get('carsFile')
                data2 = entry.get('experimentFile')

                entry_label = tk.Label(
                    row_frame,
                    justify="left",
                    text=f"User: {objectIDtoName(entry['userId'])} \n\t File 1: {data1.get('name', 'Unnamed Entry')} \n\t File 2: {data2.get('name', 'Unnamed Entry')}",
                )
                entry_label.pack(side="left", fill="x", expand=True, padx=5)

                begin_button = tk.Button(
                    row_frame,
                    text="Download Files",
                    command=lambda e=entry: [download_files(
                        e["_id"], e["carsFile"], e["experimentFile"]
                    ),
                    set_num_cars_and_update_inputs(plot, canvas_plot)],
                )
                begin_button.pack(side="right", padx=5)
        else:
            tk.Label(frame, text="No entries found in the database.").pack()

  

    # Top-left frame: List entries
    top_left_frame = tk.Frame(root)
    top_left_frame.pack(side="left", fill="both", expand=True)

    tk.Label(top_left_frame, text="Uploads Entries").pack(pady=10)

    canvas = tk.Canvas(top_left_frame)
    scroll_y = tk.Scrollbar(top_left_frame, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)

    frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    

    # Bottom-left frame: Car inputs
    global car_input_frame
    car_input_frame = tk.Frame(root, bg="white")
    car_input_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Bottom-right frame: Execute button
    bottom_right_frame = tk.Frame(root)
    bottom_right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    execute_button = tk.Button(bottom_right_frame, text="Execute", command=execute_commands)
    execute_button.pack(pady=20)

    # Populate the list of entries
    refresh_entries()

    root.mainloop()


if __name__ == "__main__":
    display_main_screen()