"""
Once the grocery receipt is turned into text, items and their prices are found using regular expressions. Each item is
then split among all of its buyers, and in the end the total for each buyer is calculated.
"""
import argparse
import re


class Item:
    """
    Represents a grocery item
    """

    def __init__(self, name, price):
        self.name = name
        self.price = price
        # A list of the people who are sharing the grocery item
        self.buyerNames = []

    def add_buyer_names(self, buyerNames):
        self.buyerNames.append(buyerNames)


class Buyer:
    """
    Represents a buyer
    """

    def __init__(self, name):
        self.name = name
        # List of items bought
        self.items = []
        # Split price is the portion of the item's price that the buyer is responsible for
        # Ex: If an item is shared among two people, the split price for that item is 1/2 the price of the item
        self.splitprice = []

    def add_items(self, items):
        self.items.append(items)


def split_receipt(filein, fileout, buyerNames):
    """
    Splits the price of the items on the receipt up according to who bought which items
    :param filein: text form of the receipt
    :param fileout: text file that displays the total spent by each person, and on what items
    :param buyerNames: the people who are splitting this receipt
    :return:
    """
    file = open(filein, 'r')
    filetext = file.read()
    file.close()

    # Using regular expressions to find the names of all the items on the receipt
    names = re.findall('\n[A-Z][A-Z-/%&\d\. ]+|\n\d{2}%[A-Z-/\d\. ]+', filetext)
    # Finding all the prices of the items on the receipt
    prices = re.findall('\$\d+.\d{2} [FT]', filetext)
    # Remove the names of categories of items
    remove_categories(names)
    # Remove the dollar sign on the prices for easier calculations
    clean_prices(prices)

    # Program stops if you don't have the same number of item names as item prices
    # Print statements will allow you to see what went wrong
    if (len(names) != len(prices)):
        print(names)
        print(len(names))
        print(prices)
        print(len(prices))
        raise ValueError("The number of prices doesn't match number of names")

    # Create an Item class for each name and price pair
    items = []
    for i in range(len(names)):
        items.append(Item(names[i], prices[i]))

    # Obtain the names of all the buyers and create Buyer classes for each of them
    buyerNames = list(buyerNames)
    buyers = []
    for i in range(len(buyerNames)):
        buyers.append(Buyer(buyerNames[i]))

    # Asking the user to input the buyers of each item. Multiple people can share the same item
    for item in items:
        print(item.name)
        print(item.price)
        buyerName = input("Who bought this item?")
        item.buyerNames = list(buyerName)
        # Adding each item to the list of items a buyer bought
        # Adds the corresponding price after accounting for the sharing of items
        for buyer in buyers:
            if (buyer.name in list(buyerName)):
                buyer.items.append(item)
                buyer.splitprice.append(float(item.price) / len(list(buyerName)))

    # Dumps the total for each buyer in a text file, along with all the items they bought
    file = open(fileout, 'w')
    total = 0
    for buyer in buyers:
        file.write(buyer.name + "\n")
        file.write(str(sum(buyer.splitprice)) + "\n\n")
        total += sum(buyer.splitprice)
    file.write("Total: " + str(total) + "\n")
    file.write("Item count: " + str(len(items)) + "\n")
    for buyer in buyers:
        file.write("\n" + buyer.name + "\n")
        for i in range(len(buyer.items)):
            file.write(buyer.items[i].name + "\n")
            file.write(str(buyer.splitprice[i]) + "\n")
    file.close()


def remove_categories(names):
    """
    Removes the names of categories of items
    """
    removedTaxableCategory = False
    for name in names:
        if (name == "\nGROCERY" or name == "\nMEAT" or name == "\nPRODUCE" or name == "\nFROZEN" or name == "\nDAIRY"
                or name == "\nH.B.A." or name == "\nBAKERY" or name == "\nGROUP 20" or name == "\nTOTAL"
                or name == "\nSAVING GRAND TOTAL"):
            names.remove(name)
        if (name == "\nTAXABLE GROCERY" and removedTaxableCategory == False):
            names.remove(name)
            removedTaxableCategory = True


def clean_prices(prices):
    """
    Removes the dollar sign from prices for easier calculations
    """
    for i in range(len(prices)):
        prices[i] = prices[i][1:-2]


parser = argparse.ArgumentParser()
parser.add_argument('in_file', help='The image for splitting.')
parser.add_argument('buyerNames', help='The first initials of the people who are splitting the groceries')
parser.add_argument('-out_file', help='Optional output file', default=parser.parse_args().in_file + "split")
args = parser.parse_args()

split_receipt(args.in_file, args.out_file, args.buyerNames)
