import sys

from Repository import repo
from Orders import Orders


# Gather our code in a main() function
def main(argv):
    repo.create_tables()
    orders = Orders(sys.argv[1], sys.argv[3])  # argv[1]: config & argv[3]:output
    orders.parse(sys.argv[2])  # order_path


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main(sys.argv)
