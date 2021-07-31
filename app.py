import tkinter as tk
from random import randrange
from api import API_KEY
import requests
import webbrowser

location = ''
radius = -1
term = ''
last_indx = -1

def get_restaurants():
    headers = {'Authorization': 'Bearer %s' % API_KEY}
    params = {'location': location, 'limit':10}
    if radius != -1:
        params['radius'] = radius
    if term != '':
        params['term'] = term
    else:
        # If no search term (like sushi, italian), just search for restaurants in general
        params['term'] = 'Restaurant'

    endpoint = 'https://api.yelp.com/v3/businesses/search'
    resp = requests.get(url=endpoint, headers=headers, params=params)
    data = resp.json()
    return data['businesses']

# Give general information about the program
def main_page(root):
    # Create a label widget and pack it onto the window
    title_label = tk.Label(root, text='Restaurant Picker')
    desc_msg = tk.Message(root, text='This executable will randomly choose a restaurant based on a certain radius around you. Choose your location and radius, and optionally choose what type of food you prefer.')
    desc_msg.config(width=400, pady=20)
    next_btn = tk.Button(root, text='Next', command= lambda: page_changer([], False), padx=30, pady=5)

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
        lambda: page_changer([input_box.get(), radius_input_box.get()], False), padx=30, pady=5)

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
    next_btn = tk.Button(root, text='Next', command=lambda: page_changer([input_box.get()], False), padx=30, pady=5)

    title_label.pack()
    desc_msg.pack()
    input_box.pack()
    next_btn.pack()

def results_page(root, results, result):
    title_label = tk.Label(root, text='Results')
    title_label.pack()

    # If no restaurant is available, state that and return
    if result == None:
        no_avail_label = tk.Label(root, text='No restaurants available')
        no_avail_label.pack()
        return

    # Create a list of categories that describes the restaurant
    categories_text = 'Categories: '
    all_categories = result['categories']
    for c_i in range(len(all_categories)):
        if c_i == len(all_categories) - 1:
            categories_text += all_categories[c_i]['title']
        else:
            categories_text += all_categories[c_i]['title'] + ', '

    result_label = tk.Label(root, text=result['name'] + ' (' + str(result['rating']) + ' stars)')
    phone_label = tk.Label(root, text=result['phone'])
    full_loc = result['location']
    dist_in_mi = round(result['distance'] / 1609, 1)
    addr_msg = tk.Message(root, text=full_loc['address1'] + ', ' + full_loc['city'] + ', ' 
        + full_loc['state'] + ' ' + full_loc['zip_code'] + ' (' + str(dist_in_mi) + ' miles away)')
    addr_msg.config(width=400)
    categories_msg = tk.Message(root, text=categories_text)
    categories_msg.config(width=400)
    open_url_btn = tk.Button(root, text='View Yelp', command=lambda: open_url(result['url']))

    redo_btn = tk.Button(root, text='New Choice', command=lambda: get_new_restaurant(root, results), padx=30, pady=5)
    restart_btn = tk.Button(root, text='Start Over', command=lambda: page_changer([], True), padx=30, pady=5)

    result_label.pack()
    phone_label.pack()
    addr_msg.pack()
    categories_msg.pack()
    open_url_btn.pack()
    redo_btn.pack()
    restart_btn.pack()

    '''
    for r in results:
        tk.Label(root, text=r['name']).pack()
    '''

def open_url(url):
    webbrowser.open_new(url)

def get_new_restaurant(root, restaurants):
    global last_indx
    rand_restaurant = None
    none_avail = False
    indx_set = set()

    clear_window(root)
    next_indx = randrange(len(restaurants))
    # Don't repeat the last shown restaurant, and make sure the restaurant is open
    while next_indx == last_indx and not restaurants[next_indx]['is_closed']:
        indx_set.add(next_indx)
        # If we have gone through all restaurants, and all are closed, then return empty
        if len(indx_set) == len(restaurants):
            none_avail = True
            break
        next_indx = randrange(len(restaurants))

    if not none_avail:
        rand_restaurant = restaurants[next_indx]
        last_indx = next_indx
    results_page(root, restaurants, rand_restaurant)

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

def page_changer(values, restart):
    global curr_page, root, error, location, radius, term

    handle_errors(values)

    # If restarting, want to set curr_page to 0
    if restart:
        curr_page = 0

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
        # Have all search queries, so find restaurants then render results page with it
        restaurants = get_restaurants()
        get_new_restaurant(root, restaurants)
        # results_page(root, rand_result)

# Create the GUI root widget
root = tk.Tk()
root.title("Restaurant Picker")
root.geometry('450x400')

# Start the program with the main page
main_page(root)
curr_page = 0
error = False

root.mainloop()