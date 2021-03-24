from collections import OrderedDict
import datetime
from datetime import date

# import csv to read csv file
import csv

# import all Peewee modules per requirements
from peewee import *

# import regular expressions for regex match in add_item function below
import re

# initialize a Sqlite database per requirements
db = SqliteDatabase("inventory.db")

# create Product model that uses Peewee ORM with specified fields per requirements
class Product(Model):

    # initialize product_id, set as unique, using peewee primary_key function per requirements
    # https://stackoverflow.com/questions/25105188/python-peewee-how-to-create-a-foreign-key
    product_id = PrimaryKeyField()

    # initialize product_name using CharField, as name should be combination of characters and possibly numbers, set as unique
    product_name = CharField(max_length=255, unique=True)

    # initialize product_quantity using Integer
    product_quantity = IntegerField(default=0)

    # initialize product price
    product_price = IntegerField(default=0)

    # initialize date with DateField
    date_updated = DateField()

    class Meta:
        database = db

        
# function that converts all given items; this will be called in read_csv_file function to format data
def convert_csv_items(product_name=" ", product_price="", product_quantity="", date_updated="03/31/21"):

    # remove spaces from beginning and end of name string
    product_name = product_name.strip()

    # convert quantity to integer
    product_quantity = int(product_quantity)

    # remove dollar symbol, create list for dollar amount and cent value, then convert dollar amount to cents and add
    price_conversion_list = product_price.replace("$", "").split(".")

    dollar_amount = price_conversion_list[0]
    dollar_amount = int(dollar_amount)

    cent_amount = price_conversion_list[1]
    cent_amount = int(cent_amount)

    converted_price_in_cents = (dollar_amount * 100) + cent_amount

    # create list for month, day and year values with slashes removed from date
    date_updated_list = date_updated.split("/")

    #convert date values in list into integers, then store in product_date variable with order of Year, Month, then Day
    updated_month = date_updated_list[0]
    updated_month = int(updated_month)

    updated_day = date_updated_list[1]
    updated_day = int(updated_day)

    updated_year = date_updated_list[2]
    updated_year = int(updated_year)

    product_date = date(updated_year, updated_month, updated_day)

    # create a dictionary that will store the converted values
    converted_list = {"product_name": product_name, "product_price": converted_price_in_cents, "product_quantity": product_quantity, "product_date": product_date}

    return converted_list

            
# function for populating empty inventory database/adding new items to inventory database; this will be called in read_csv_file function to populate database
def populate_inventory(populate_name="", populate_price=0, populate_quantity=0, populate_date_updated="03/31/21"):
    try:
        Product.create(product_name = populate_name, product_price = populate_price, product_quantity = populate_quantity, date_updated = populate_date_updated)

        # additional check to see before product is added if duplicate name is found. saves most recent update for existing record
    except IntegrityError:

        # run Sql to locate current date of duplicate product name in Product
        current_date = Product.select().where(Product.product_name == populate_name).get().date_updated

        # verify if date in current date in Product is prior to new date
        if current_date <= populate_date_updated:

            # run Sql to locate name of duplicate product
            duplicate_product = Product.select().where(Product.product_name == populate_name).get().product_name

            print("\nA duplicate entry for {} has been detected. Saving most-recent update.".format(duplicate_product))

            # update duplicate product in Product with newest Price, Quantity, and Date; set as SQL query
            # execute query to update entries
            update = Product.update(product_price = populate_price, product_quantity = populate_quantity, date_updated = populate_date_updated).where(Product.product_name == populate_name)
            update.execute()

            
# function for reading inventory csv file, converting all items using convert_csv_items function, then populating inventory database
def read_csv_file():
    with open("inventory.csv", newline="") as csvfile:
        all_products = csv.DictReader(csvfile)
        for product in all_products:
            converted_items = convert_csv_items(product["product_name"], product["product_price"], product["product_quantity"], product["date_updated"])
            populate_inventory(converted_items["product_name"], converted_items["product_price"], converted_items["product_quantity"], converted_items["product_date"])

# function for displaying a product entry by its ID
def view_product():

    valid_id = False

    # begin while loop to ensure valid ID is entered
    while valid_id == False:

        submitted_id = input("\nPlease enter the ID of the Product you'd like to view, or enter 'R' to return to the menu: ")

        # verify if submitted ID is populated, otherwise continue loop
        
        if submitted_id.upper() == "R":
            return
        
        if submitted_id == "":
            print("\nNo ID was entered")
            continue

        # verify that submitted ID is valid
        try:
            submitted_id = int(submitted_id)
            
        except ValueError:
            print("\nThat is not a valid ID Number. Please try again")
            continue

        # if submitted ID is not blank and is valid, try locating ID in current Inventory database. if id matches an entry, break loop. otherwise, re-prompt user for ID
        try:
            given_id = Product.select().where(Product.product_id == int(submitted_id)).get()
            
            print("\nName: {}".format(given_id.product_name))
            formatted_price = (given_id.product_price/100)
            print("Price: {}".format(formatted_price))
            print("Quantity: {}".format(given_id.product_quantity))
            print("Last Updated: {}".format(given_id.date_updated))

        # if ID was not matched/does not exist, display human readable error message and prompt user for input again
        # https://django.readthedocs.io/en/1.6.x/ref/exceptions.html
        except DoesNotExist:
            print("\nThat ID does not correspond to an ID in the current Inventory. Please Try Again.")

            
# function for adding new item to database
def add_item():

    # prompt user for new product name
    new_product_name = input("\nEnter name of new product: ")

    # begin verification loop for price of new product. if error is encountered with given price, continue loop
    new_price_pass = False

    while new_price_pass == False:

        new_price_pass = False
        
        while new_price_pass == False:

        	# prompt user to enter price with dollar sign and decimal to match below regex
        	# https://stackoverflow.com/questions/43570848/regex-to-match-dollar-sign-money-decimals-only/43570891
        	# https://stackoverflow.com/questions/12596824/regular-expression-the-dollar-sign-work-with-re-match-or-re-search
            new_price = re.match(r'^[$]{1}\d+[.]+\d{2}$', input("\nPlease enter a price, with dollar sign (in format $1.00): "))

            # validate if entered price does not match regex format
            if new_price is None:
                print("\nPlease enter the price in the above specified format.")

            else:
            	# https://www.tutorialspoint.com/What-is-the-groups-method-in-regular-expressions-in-Python
                new_price = new_price.group()
                new_price_pass = True
        

    # begin verification loop for quantity of new product. if error is encountered with given quantity, continue loop
    new_quantity_pass = False

    while new_quantity_pass == False:

        new_quantity = input("\nPlease enter the quantity of {}: ".format(new_product_name))

        # verify that entered quantity is integer value
        try:
            new_quantity = int(new_quantity)

            # verify that entered quantity is not a negative number
            if new_quantity < 0:
                print("\nPlease do not enter a negative quantity")
                continue

            new_quantity_pass = True

        # if ValueError is encountered, re-prompt user for price
        except ValueError:
            print("\nThat is not a valid quantity. Please enter the quantity as a number.")

    # if new name, price, and quantity have all been successfully entered, proceed to store today's date
    update_date = datetime.datetime.now().date()

    # convert all new variables to proper format using convert_csv_items function
    new_data = convert_csv_items(new_product_name, new_price, new_quantity)

    # append new formatted data, along with today's date, to inventory database 
    populate_inventory(new_data["product_name"], new_data["product_price"], new_data["product_quantity"], update_date)
    
    print("\nProduct Added")

    
# function for creating backup of inventory database, exporting as csv
def create_backup():

    with open("backup.csv", "w") as back:
        
        # write out header names for backup file
        fields = ["product_name", "product_price", "product_quantity", "date_updated"]

        # use DictWriter to write dictionary into CSV file
        # https://zetcode.com/python/csv/
        writer = csv.DictWriter(back, fieldnames = fields)
        
        # write out single header row with all appropriate field titles per above DictWriter 
        writer.writeheader()

        # select all Product items/data
        items = Product.select()
        
        # use for loop to iterate through all entries in Product, then use writerow to write out the name, price, quantity, and last updated date of each entry
        for entry in items:

            writer.writerow({"product_name": entry.product_name, "product_price": entry.product_price, "product_quantity": entry.product_quantity, "date_updated": entry.date_updated})

        print("\nBackup Created")


# function for app menu
def main_menu():

    menu_selection = None

    # start menu loop
    while menu_selection != 'e':

        print("\nv) View Product by ID\n")
        print("a) Add a new Product to Inventory\n")
        print("b) Backup current Inventory\n")
        print("e) Exit Inventory App\n")

        # prompt user for menu selection
        menu_selection = input("Please select one of the options above: ")
        menu_selection = menu_selection.lower()

        # view a single product in the database
        if menu_selection == 'v':
            view_product()
        
        # add a new product to the database
        elif menu_selection == 'a':
            add_item()
            
        # make a backup of the entire contents of the database
        elif menu_selection == 'b':
            create_backup()
        
        # exit the app
        elif menu_selection == 'e':
            print("\nThank you for using the Store Inventory App\n")
        
        # notify user of error if any other character besides v, a, b, or e is entered, and re-prompt for menu input
        else:
            print("\nThat is not a valid option, please try again\n")


# dunder main method: connect to database, create tables, populate table with initial CSV products data from inventory.csv, then display menu
if __name__ == '__main__':

    # connect to previously initalized Sqlitedatabse
    db.connect()

    # create tables, safe=True for pre-existing entries
    db.create_tables([Product], safe=True)

    # populate inventory with initial inventory.csv file entries
    read_csv_file()

    # run menu
    main_menu()

