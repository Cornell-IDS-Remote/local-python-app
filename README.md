# Local Python App for Experiment Management

This repository contains work related to the local Python application used for running uploaded code from the database as an experiment in the lab. The application facilitates the following:

1. **Experiment Selection**  
   Displays available experiments uploaded to the database, allowing the lab assistant to choose the desired one.

2. **Car ID Assignment**  
   Simplifies assigning car IDs based on which cars are operational or charged (checked manually).

3. **Car Placement Visualization**  
   Provides a visual representation of where to place the cars based on the uploader's design.

4. **Experiment Execution**  
   Includes a button to execute and run the selected experiment.

## Example Image

![Simple App](app_simple.png)

## Running the App

To run the app, the libraries listed in the `requirements.txt` file must be installed. Use the following commands:

### On Windows:

pip install -r requirements.txt

### On macOS:

pip3 install -r requirements.txt


### Recommendation:
It is recommended to use a virtual environment to install the required libraries. This avoids conflicts with other libraries on your computer. To create and activate a virtual environment:

#### On Windows:
python -m venv env env\Scripts\activate pip install -r requirements.txt

shell
Copy code

#### On macOS/Linux:
python3 -m venv env source env/bin/activate pip install -r requirements.txt

sql
Copy code

### Running the App:
Once the required libraries are installed, you can run the app using the following command:

python run_experiment.py
