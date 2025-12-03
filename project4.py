import datetime
import uuid
import sys
import json
import os

# --- Configuration ---
DATA_FILE = 'library_data.json'
# --- Global Authentication Data (Kept outside Manager for simplicity of multi-user access) ---
USERS = [
    # Initial Staff User
    {'id': str(uuid.uuid4()), 'username': 'admin', 'password': '123', 'role': 'staff'},
    # Initial Customer User
    {'id': str(uuid.uuid4()), 'username': 'jane_doe', 'password': '456', 'role': 'customer'}
]
CURRENT_USER = None

def find_user_by_username(username):
    """Searches USERS list for a user by username."""
    for user in USERS:
        if user['username'] == username:
            return user
    return None

def get_user_id():
    """Returns the ID of the current user, or None if not logged in."""
    global CURRENT_USER
    return CURRENT_USER['id'] if CURRENT_USER else None

# --- 1. OOP: Book Class ---

class Book:
    """Represents a book in the library with its details and copy count."""
    def __init__(self, title, author, copies, book_id=None):
        self.id = book_id if book_id is not None else str(uuid.uuid4())
        self.title = title
        self.author = author
        self.copies = copies

    def to_dict(self):
        """Converts Book object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'copies': self.copies
        }

    @staticmethod
    def from_dict(data):
        """Creates a Book object from a dictionary loaded from JSON."""
        return Book(data['title'], data['author'], data['copies'], data['id'])

# --- 2. OOP: LibraryManager Class (Handles Persistence, Logic, and Reports) ---

class LibraryManager:
    """Manages the book collection, borrowing records, persistence, and reports."""
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.books = {}         # Dictionary (HashMap) for quick book lookup: {id: Book_object}
        self.borrowed_records = []  # List of dicts: [{'user_id': uid, 'book_id': bid, 'due_date': date}]
        self.load_data()

    def load_data(self):
        """Loads book and record data from a JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # Recreate Book objects from dicts
                    for book_dict in data.get('books', {}).values():
                        book = Book.from_dict(book_dict)
                        self.books[book.id] = book

                    self.borrowed_records = data.get('borrowed_records', [])
                print(f"[INFO] Data loaded successfully from {self.data_file}.")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] Could not load data from file: {e}. Starting with empty data.")
        else:
            print("[INFO] No data file found. Starting with initial data (3 sample books).")
            # Initialize with initial data if file doesn't exist
            initial_books = [
                Book('The Great Gatsby', 'F. Scott Fitzgerald', 3, '1'),
                Book('1984', 'George Orwell', 5, '2'),
                Book('Moby Dick', 'Herman Melville', 1, '3')
            ]
            for book in initial_books:
                self.books[book.id] = book


    def save_data(self):
        """Persists book and record data to a JSON file."""
        data_to_save = {
            # Convert Book objects to dicts for JSON serialization
            'books': {book_id: book.to_dict() for book_id, book in self.books.items()},
            'borrowed_records': self.borrowed_records
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"[INFO] Data saved successfully to {self.data_file}.")
        except IOError as e:
            print(f"[ERROR] Could not save data to file: {e}.")

    # --- Book Management (Staff Functions) ---

    def display_book_database(self):
        """Displays the main list of books in the library."""
        if not self.books:
            print("\n[INFO] The main library catalog is empty.")
            return

        print("\n--- LIBRARY BOOK CATALOG ---")
        print(f"{'ID':<10} | {'Title':<40} | {'Author':<25} | {'Copies':<8} | {'Available':<10}")
        print("-" * 100)
        
        for book_id, book in self.books.items():
            borrowed_count = self.get_borrowed_count(book_id)
            available = book.copies - borrowed_count
            print(f"{book_id:<10} | {book.title:<40} | {book.author:<25} | {book.copies:<8} | {available:<10}")
        print("-" * 100)

    def add_book(self, title, author, copies):
        """Adds a new book instance to the library collection."""
        new_book = Book(title, author, copies)
        self.books[new_book.id] = new_book
        self.save_data()
        return new_book

    def delete_book(self, book_id):
        """Deletes a book from the library catalog by ID."""
        if book_id in self.books:
            book_to_delete = self.books[book_id]
            
            # Check if any copies are currently borrowed
            if self.get_borrowed_count(book_id) > 0:
                print(f"[ERROR] Cannot delete '{book_to_delete.title}'. Copies are currently borrowed.")
                return False

            del self.books[book_id]
            self.save_data()
            print(f"\n[SUCCESS] Book '{book_to_delete.title}' has been permanently removed.")
            return True
        else:
            print(f"\n[ERROR] Book with ID {book_id} not found.")
            return False

    def get_borrowed_count(self, book_id):
        """Calculates how many copies of a specific book are currently borrowed."""
        return sum(1 for record in self.borrowed_records if record['book_id'] == book_id)

    # --- Search and Report Functions (New Requirement) ---

    def search_books(self, query):
        """Searches books by title or author."""
        query = query.lower()
        results = []
        for book in self.books.values():
            if query in book.title.lower() or query in book.author.lower():
                borrowed_count = self.get_borrowed_count(book.id)
                available = book.copies - borrowed_count
                results.append((book, available))

        if not results:
            print(f"\n[INFO] No books found matching '{query}'.")
            return

        print(f"\n--- SEARCH RESULTS for '{query}' ---")
        print(f"{'ID':<10} | {'Title':<40} | {'Author':<25} | {'Available':<10}")
        print("-" * 90)
        for book, available in results:
            print(f"{book.id:<10} | {book.title:<40} | {book.author:<25} | {available:<10}")
        print("-" * 90)


    def generate_simple_report(self):
        """Prints total books, total copies, and total issued count."""
        total_unique_books = len(self.books)
        total_copies = sum(book.copies for book in self.books.values())
        total_issued = len(self.borrowed_records)
        
        print("\n--- LIBRARY REPORT ---")
        print(f"Total Unique Book Titles: {total_unique_books}")
        print(f"Total Physical Copies in Catalog: {total_copies}")
        print(f"Total Books Currently Issued: {total_issued}")
        print("-" * 30)
        
        # Optional: Overdue check
        today = datetime.date.today()
        overdue_count = 0
        for record in self.borrowed_records:
            due_date = datetime.date.fromisoformat(record['due_date'])
            if due_date < today:
                overdue_count += 1
        print(f"Total Overdue Books: {overdue_count}")
        print("-" * 30)

    # --- Customer Logic (Issue/Return) ---

    def view_available_books(self):
        """Displays books that have copies available to borrow."""
        available_books = []
        
        for book in self.books.values():
            borrowed_count = self.get_borrowed_count(book.id)
            available_copies = book.copies - borrowed_count
            
            if available_copies > 0:
                available_books.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'available_copies': available_copies
                })

        if not available_books:
            print("\n[INFO] No books are currently available to borrow.")
            return

        print("\n--- BOOKS AVAILABLE TO BORROW ---")
        print(f"{'ID':<10} | {'Title':<40} | {'Author':<25} | {'Available Copies':<18}")
        print("-" * 100)
        for book in available_books:
            print(f"{book['id']:<10} | {book['title']:<40} | {book['author']:<25} | {book['available_copies']:<18}")
        print("-" * 100)

    def borrow_book(self, book_id, user_id):
        """Handles the borrowing (issue) of a book."""
        if user_id is None: return

        # Limit to 3 borrowed books at a time
        if sum(1 for r in self.borrowed_records if r['user_id'] == user_id) >= 3:
            print("\n[ERROR] You have reached the maximum borrowing limit (3 books). Please return a book first.")
            return

        if book_id not in self.books:
            print(f"[ERROR] Book with ID {book_id} not found.")
            return

        book_to_borrow = self.books[book_id]
        available_copies = book_to_borrow.copies - self.get_borrowed_count(book_id)
        
        if available_copies > 0:
            due_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            
            new_record = {
                'user_id': user_id,
                'book_id': book_id,
                'due_date': due_date
            }
            self.borrowed_records.append(new_record)
            self.save_data()
            
            print(f"\n[SUCCESS] You have successfully borrowed '{book_to_borrow.title}'.")
            print(f"Please return it by {due_date}.")
        else:
            print(f"\n[ERROR] All copies of '{book_to_borrow.title}' are currently borrowed.")

    def return_book(self, book_id, user_id):
        """Handles the returning of a borrowed book."""
        if user_id is None: return

        # Find the specific record for the book being returned by the current user
        record_to_remove = next((r for r in self.borrowed_records 
                                 if r['user_id'] == user_id and r['book_id'] == book_id), None)

        if record_to_remove:
            self.borrowed_records.remove(record_to_remove)
            self.save_data()
            book = self.books.get(book_id)
            title = book.title if book else "Unknown Book"
            print(f"\n[SUCCESS] '{title}' has been successfully returned. Thank you!")
        else:
            print(f"\n[ERROR] You do not have a record for Book ID {book_id}.")


    def view_my_books(self, user_id):
        """Displays the list of books the current customer has borrowed."""
        if user_id is None: return
        
        my_borrowed_records = [r for r in self.borrowed_records if r['user_id'] == user_id]

        if not my_borrowed_records:
            print("\n[INFO] You currently have no books borrowed.")
            return

        print("\n--- YOUR BORROWED BOOKS ---")
        print(f"{'ID':<10} | {'Title':<40} | {'Due Date':<12}")
        print("-" * 65)
        for record in my_borrowed_records:
            book = self.books.get(record['book_id'])
            if book:
                print(f"{book.id:<10} | {book.title:<40} | {record['due_date']:<12}")
        print("-" * 65)

    def view_customers_books(self):
        """Displays all registered customers and the books they currently have borrowed."""
        customer_users = [user for user in USERS if user['role'] == 'customer']
        
        if not customer_users:
            print("\n[INFO] No registered customers found.")
            return

        print("\n--- REGISTERED CUSTOMERS AND BORROWED BOOKS ---")
        
        for customer in customer_users:
            print(f"\nCustomer: {customer['username']} (ID: {customer['id'][:8]}...)")
            
            borrowed = [r for r in self.borrowed_records if r['user_id'] == customer['id']]
            
            if not borrowed:
                print("  - No books currently borrowed.")
            else:
                print("  - Currently Borrowing:")
                for record in borrowed:
                    book = self.books.get(record['book_id'])
                    book_title = book.title if book else "Unknown Book (ID: {})".format(record['book_id'])
                    print(f"    -> '{book_title}' (Due: {record['due_date']})")
        
        print("-" * 50)


# --- 3. Authentication Functions (Using the global USERS list) ---

# Authentication and Registration functions (authenticate_staff, register_staff, customer_login, customer_register) 
# remain mostly the same as they only deal with the global USERS list.

def authenticate_staff():
    """Handles staff login (Returning Staff)."""
    print("\n--- STAFF LOGIN ---")
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    
    user = find_user_by_username(username)
    
    if user and user['password'] == password and user['role'] == 'staff':
        global CURRENT_USER
        CURRENT_USER = user
        print(f"\n[SUCCESS] Welcome back, {username}!")
        return True
    else:
        print("\n[ERROR] Invalid credentials or user is not a staff member.")
        return False

def register_staff():
    """Handles new staff member registration (New Staff)."""
    print("\n--- STAFF REGISTRATION ---")
    while True:
        username = input("Enter New Username: ")
        if find_user_by_username(username):
            print("[ERROR] Username already exists. Try again.")
        else:
            break

    password = input("Create Password: ")
    
    new_staff = {
        'id': str(uuid.uuid4()), 
        'username': username, 
        'password': password, 
        'role': 'staff'
    }
    USERS.append(new_staff)
    
    global CURRENT_USER
    CURRENT_USER = new_staff
    
    print(f"\n[SUCCESS] Staff member {username} registered and logged in successfully!")
    return True

def customer_login():
    """Handles customer login."""
    print("\n--- CUSTOMER LOGIN ---")
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    user = find_user_by_username(username)
    
    if user and user['password'] == password and user['role'] == 'customer':
        global CURRENT_USER
        CURRENT_USER = user
        print(f"\n[SUCCESS] Welcome, {username}!")
        return True
    else:
        print("\n[ERROR] Invalid credentials or user is not a customer.")
        return False

def customer_register():
    """Handles new customer registration."""
    print("\n--- CUSTOMER REGISTRATION ---")
    while True:
        username = input("Enter New Username: ")
        if find_user_by_username(username):
            print("[ERROR] Username already exists. Try again.")
        else:
            break

    password = input("Create Password: ")
    
    new_customer = {
        'id': str(uuid.uuid4()), 
        'username': username, 
        'password': password, 
        'role': 'customer'
    }
    USERS.append(new_customer)
    
    global CURRENT_USER
    CURRENT_USER = new_customer
    
    print(f"\n[SUCCESS] Customer {username} registered and logged in successfully!")
    return True

# --- 4. Menu Logic ---

def staff_search_menu(manager):
    """Staff Search Sub-menu"""
    print("\n--- BOOK SEARCH ---")
    query = input("Enter Title or Author to search (or 'q' to cancel): ")
    if query.lower() != 'q':
        manager.search_books(query)

def staff_add_book_menu(manager):
    """Staff Add Book Sub-menu"""
    print("\n--- ADD A NEW BOOK ---")
    title = input("Enter Book Title: ")
    author = input("Enter Author Name: ")
    while True:
        try:
            copies = int(input("Enter Number of Copies to Add: "))
            if copies <= 0:
                raise ValueError
            break
        except ValueError:
            print("[ERROR] Please enter a positive whole number for copies.")

    manager.add_book(title, author, copies)
    print(f"\n[SUCCESS] Book '{title}' by {author} added to the library.")

def staff_delete_book_menu(manager):
    """Staff Delete Book Sub-menu"""
    manager.display_book_database()
    
    if not manager.books:
        return

    while True:
        book_id_str = input("\nEnter ID of the book to delete (or 'q' to cancel): ")
        if book_id_str.lower() == 'q':
            return
        
        # Check if the entered ID exists
        if book_id_str in manager.books:
            manager.delete_book(book_id_str)
            return
        else:
            print("[ERROR] Invalid Book ID. Please enter a valid ID or 'q'.")

def staff_book_management_menu(manager):
    """The menu for staff to manage the book database."""
    while True:
        print("\n--- BOOK MANAGEMENT MENU ---")
        print("1. View Full Book Catalog")
        print("2. Add New Book")
        print("3. Delete Book")
        print("4. Search Books")
        print("5. Return to Staff Menu")
        print("6. Exit Application")
        
        try:
            choice = input("Enter choice: ")
            
            if choice == '1':
                manager.display_book_database()
            elif choice == '2':
                staff_add_book_menu(manager)
            elif choice == '3':
                staff_delete_book_menu(manager)
            elif choice == '4':
                staff_search_menu(manager)
            elif choice == '5':
                return # Go back to staff_main_menu
            elif choice == '6':
                manager.save_data()
                print("Exiting application. Goodbye!")
                sys.exit(0)
            else:
                print("[ERROR] Invalid choice. Please select 1-6.")
        except KeyboardInterrupt:
            print("\nReturning to Staff Menu...")
            return

def staff_main_menu(manager):
    """The main menu for the logged-in staff member."""
    global CURRENT_USER
    while CURRENT_USER and CURRENT_USER['role'] == 'staff':
        print("\n--- STAFF MAIN MENU ---")
        print(f"Logged in as: {CURRENT_USER['username']}")
        print("1. Check Customer List & Borrowing Records")
        print("2. Access Book Database (Add/Delete/Search)")
        print("3. Generate Library Report")
        print("4. Logout")
        print("5. Exit Application")
        
        try:
            choice = input("Enter choice: ")
            
            if choice == '1':
                manager.view_customers_books()
            elif choice == '2':
                staff_book_management_menu(manager)
            elif choice == '3':
                manager.generate_simple_report()
            elif choice == '4':
                manager.save_data()
                CURRENT_USER = None
                print("\n[INFO] Logged out successfully.")
                return
            elif choice == '5':
                manager.save_data()
                print("Exiting application. Goodbye!")
                sys.exit(0)
            else:
                print("[ERROR] Invalid choice. Please select 1-5.")
        except KeyboardInterrupt:
            print("\nLogging out for safety.")
            manager.save_data()
            CURRENT_USER = None
            return

def customer_borrow_menu(manager):
    """Customer Borrow Book Sub-menu"""
    manager.view_available_books()
    user_id = get_user_id()
    if not user_id: return

    while True:
        book_id_str = input("\nEnter ID of the book to borrow (or 'q' to cancel): ")
        if book_id_str.lower() == 'q':
            return
        
        if book_id_str in manager.books:
            manager.borrow_book(book_id_str, user_id)
            return
        else:
            print("[ERROR] Invalid Book ID. Please enter a valid ID or 'q'.")

def customer_return_menu(manager):
    """Customer Return Book Sub-menu"""
    user_id = get_user_id()
    manager.view_my_books(user_id)
    
    if not user_id: return
    if not [r for r in manager.borrowed_records if r['user_id'] == user_id]:
        return

    while True:
        book_id_str = input("\nEnter ID of the book to return (or 'q' to cancel): ")
        if book_id_str.lower() == 'q':
            return

        if book_id_str in manager.books:
            manager.return_book(book_id_str, user_id)
            return
        else:
            print("[ERROR] Invalid Book ID. Please enter a valid ID or 'q'.")

def customer_main_menu(manager):
    """The main menu for the logged-in customer."""
    global CURRENT_USER
    user_id = get_user_id()
    while CURRENT_USER and CURRENT_USER['role'] == 'customer':
        print("\n--- CUSTOMER MAIN MENU ---")
        print(f"Logged in as: {CURRENT_USER['username']}")
        print("1. View Available Books")
        print("2. Borrow a Book")
        print("3. View My Borrowed Books")
        print("4. Return a Book")
        print("5. Logout")
        print("6. Exit Application")
        
        try:
            choice = input("Enter choice: ")
            
            if choice == '1':
                manager.view_available_books()
            elif choice == '2':
                customer_borrow_menu(manager)
            elif choice == '3':
                manager.view_my_books(user_id)
            elif choice == '4':
                customer_return_menu(manager)
            elif choice == '5':
                manager.save_data()
                CURRENT_USER = None
                print("\n[INFO] Logged out successfully.")
                return
            elif choice == '6':
                manager.save_data()
                print("Exiting application. Goodbye!")
                sys.exit(0)
            else:
                print("[ERROR] Invalid choice. Please select 1-6.")
        except KeyboardInterrupt:
            print("\nLogging out for safety.")
            manager.save_data()
            CURRENT_USER = None
            return

# --- 5. Initial Menu Logic ---

def initial_user_type_menu():
    """The very first menu asking for user role."""
    print("\n\n=============== LIBRARY MANAGEMENT SYSTEM ===============")
    print("Please identify your role:")
    print("1. Staff Member")
    print("2. Customer")
    print("3. Exit Application")
    print("=======================================================")
    
    try:
        choice = input("Enter choice: ")
        return choice
    except KeyboardInterrupt:
        return '3'


def staff_login_type_menu():
    """The sub-menu for staff login/registration."""
    print("\n--- STAFF ACCESS ---")
    print("1. Returning Staff (Login)")
    print("2. New Staff (Register)")
    print("3. Back to Main Menu")
    
    try:
        choice = input("Enter choice: ")
        return choice
    except KeyboardInterrupt:
        return '3'

def customer_access_menu():
    """The sub-menu for customer login/registration."""
    print("\n--- CUSTOMER ACCESS ---")
    print("1. Returning Customer (Login)")
    print("2. New Customer (Register)")
    print("3. Back to Main Menu")
    
    try:
        choice = input("Enter choice: ")
        return choice
    except KeyboardInterrupt:
        return '3'

# --- Main Application Execution ---

if __name__ == "__main__":
    
    # Initialize the Library Manager (This loads data from JSON or creates initial books)
    library_manager = LibraryManager()
    
    while True:
        # If a user is logged in, show their respective menu
        if CURRENT_USER:
            if CURRENT_USER['role'] == 'staff':
                staff_main_menu(library_manager)
            elif CURRENT_USER['role'] == 'customer':
                customer_main_menu(library_manager)
            continue

        # If no user is logged in, show the initial role selection menu
        role_choice = initial_user_type_menu()

        if role_choice == '1':
            # Staff Path
            staff_choice = staff_login_type_menu()
            if staff_choice == '1':
                if authenticate_staff():
                    staff_main_menu(library_manager)
            elif staff_choice == '2':
                if register_staff():
                    staff_main_menu(library_manager)
            elif staff_choice == '3':
                continue # Back to initial menu

        elif role_choice == '2':
            # Customer Path
            customer_choice = customer_access_menu()
            if customer_choice == '1':
                if customer_login():
                    customer_main_menu(library_manager)
            elif customer_choice == '2':
                if customer_register():
                    customer_main_menu(library_manager)
            elif customer_choice == '3':
                continue # Back to initial menu

        elif role_choice == '3':
            # Exit application
            library_manager.save_data()
            print("\nExiting application. Goodbye!")
            break
        
        else:
            print("\n[ERROR] Invalid choice. Please select 1, 2, or 3.")
