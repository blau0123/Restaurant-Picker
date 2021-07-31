import tkinter as tk
from api import API_KEY
import requests

location = ''
radius = -1
term = ''
restaurants = []

def get_restaurants():
    headers = {'Authorization': 'Bearer %s' % API_KEY}
    params = {'location': location, 'limit':10}
    if radius != -1:
        params['radius'] = radius
    if term != '':
        params['term'] = term
    endpoint = 'https://api.yelp.com/v3/businesses/search'
    resp = requests.get(url=endpoint, headers=headers, params=params)
    data = resp.json()
    restaurants = data['businesses']

# Give general information about the program
def main_page(root):
    # Create a label widget and pack it onto the window
    title_label = tk.Label(root, text='Restaurant Picker')
    desc_msg = tk.Message(root, text='This executable will randomly choose a restaurant based on a certain radius around you. Choose your location and radius, and optionally choose what type of food you prefer.')
    desc_msg.config(width=400, pady=20)
    next_btn = tk.Button(root, text='Next', command= lambda: page_changer(['']), padx=30, pady=5)

    title_label.pack()
    desc_msg.pack()
    next_btn.pack()

# Allow the user to select their location and radius
def location_sel_page(root):
    title_label = tk.Label(root, text='Choose your location and radius')
    desc_msg = tk.Message(root, text='Your last location chosen is Tokyo. Would you like to change it? If no, leave the input box empty and press next.')
    desc_msg.config(width=400, pady=20)
    input_box = tk.Entry(root, width=50)

    radius_msg = tk.Message(root, text='What radius do you want around your location (in miles)? Max is 25 miles.')
    radius_msg.config(width=400, pady=20)
    radius_input_box = tk.Entry(root, width=50)

    next_btn = tk.Button(root, text='Next', command= 
        lambda: page_changer([input_box.get(), radius_input_box.get()]), padx=30, pady=5)

    title_label.pack()
    desc_msg.pack()
    input_box.pack()
    radius_msg.pack()
    radius_input_box.pack()
    next_btn.pack()

# Allow the user to select food choices (Italian, etc.) comma separated
def choices_page(root):
    title_label = tk.Label(root, text='Food Choices')
    desc_msg = tk.Message(root, text='Choose any specific type of food you want (Italian, sushi, etc.). You can only make one choice. If there is no preference, leave the input box empty and press next.')
    desc_msg.config(width=400, pady=20)
    input_box = tk.Entry(root, width=50)
    next_btn = tk.Button(root, text='Next', command=lambda: page_changer([input_box.get()]), padx=30, pady=5)

    title_label.pack()
    desc_msg.pack()
    input_box.pack()
    next_btn.pack()

def results_page(root):
    title_label = tk.Label(root, text='Results')
    title_label.pack()

    restaurants = get_restaurants()
    for r in restaurants:
        tk.Label(root, text=r['name']).pack()

def get_new_restaurant():
    global root

    clear_window(root)
    rand_restaurant = restaurants[0]
    results_page(root)

# Handles finding input errors, such as leaving required inputs blank
def handle_errors(values):
    global curr_page, root, error

    if curr_page == 1:
        # If the location was not specified on location page, do not let the user move onto the next page
        if values[0].replace(' ', '') == '':
            # If first time seeing error, show the error message
            if error == False:
                err_label = tk.Label(root, text='Location is mandatory')
                err_label.pack()

            error = True
            return
    
    # No input error was found
    error = False

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def page_changer(values):
    global curr_page, root, error, location, radius, term

    handle_errors(values)

    # Destroy all the current widgets on the root (current page)
    if error == False:
        clear_window(root)

    # Put the widgets for the new page onto the root
    if curr_page == 0:
        location_sel_page(root)
        curr_page = 1
    elif curr_page == 1:
        # If the location was not specified, do not let the user move onto the next page
        if error == False:
            # Set the mandatory location and optional radius (convert mi to m)
            location = values[0]
            if values[1] != '':
                radius = int(values[1]) * 1609
            choices_page(root)
            curr_page = 2
    elif curr_page == 2:
        term = values[0]
        results_page(root)

# Create the GUI root widget
root = tk.Tk()
root.title("Restaurant Picker")
root.geometry('450x400')

# Start the program with the main page
main_page(root)
curr_page = 0
error = False

root.mainloop()