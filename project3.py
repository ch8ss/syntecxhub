# Student Management System in Python

# 1. Global Data Structure
# The list to store student records (dictionaries).
# Initializing with one record to show the required format.
STD_LIST = [
    {'Name': 'Jawad', 'Roll': '01003', 'Depart': 'AI'}
]

# 2. Functions

def show_student_list():
    """Displays the list of all students with their details."""
    if not STD_LIST:
        print("\n[INFO] The student list is currently empty.")
        return

    print("\n--- STUDENT LIST ---")
    # enumerate is used to get the index for numbering (index + 1)
    for index, student in enumerate(STD_LIST):
        # [14:02]
        print(f"{index + 1}. Name: {student['Name']}, Roll: {student['Roll']}, Depart: {student['Depart']}")
    print("----------------------")

def add_student(data):
    """Adds a new student dictionary to the global STD_LIST."""
    # [12:01]
    STD_LIST.append(data)
    # [16:16]
    print("\n[SUCCESS] Student Added Successfully!")

def edit_student(roll_number):
    """Edits the details of a student based on their Roll Number."""
    for student in STD_LIST:
        if student['Roll'] == roll_number:
            print(f"\nEditing record for Roll Number: {roll_number}")
            
            # Get new details
            new_name = input("Enter Student New Name: ") 
            new_roll = input("Enter Student New Roll Number: ") 
            new_depart = input("Enter Student New Department: ") 

            # Update the student record
            student['Name'] = new_name 
            student['Roll'] = new_roll 
            student['Depart'] = new_depart 

           
            print("\n[SUCCESS] Student Updated Successfully!")
            return # Exit the function once the student is found and updated

   
    print(f"\n[ERROR] Oops! Student With Roll Number '{roll_number}' Not Exists.")

def delete_student(roll_number):
    """Deletes a student record based on their Roll Number."""
    # Note: It's safer to iterate over a copy or use indices when modifying a list during iteration,
    # but the presenter's simple loop logic is preserved here.
    for student in STD_LIST:
        if student['Roll'] == roll_number:
           
            STD_LIST.remove(student)
           
            print("\n[SUCCESS] Student Deleted Successfully!")
            return # Exit the function once the student is found and deleted

   
    print(f"\n[ERROR] Oops! Student With Roll Number '{roll_number}' Not Exists.")

# 3. Main Program Loop

while True: 
  
    print("\n\n=============== STUDENT MANAGEMENT PORTAL ===============")
    print("1. Show Student List")
    print("2. Add Student")
    print("3. Edit Student")
    print("4. Delete Student")
    print("5. Exit From Portal")
    print("=======================================================")

    try:
      
        choice = int(input("Enter Your Choice: "))
    except ValueError:
        print("\n[ERROR] Invalid input. Please enter a number (1-5).")
        continue

    # Exit Condition [07:46]
    if choice == 5:
      
        print("\nExiting Portal... Goodbye!")
        break

    # Match/Case Logic (Python 3.10+) [08:55]
    match choice:
        case 1:
            # Show Student List 
            show_student_list()

        case 2:
            # Add Student 
            std_name = input("Enter Student Name: ")
            std_roll = input("Enter Student Roll Number: ")
            std_depart = input("Enter Student Department: ")
            
            # Create data dictionary 
            data = {
                "Name": std_name,
                "Roll": std_roll,
                "Depart": std_depart
            }
            
            add_student(data)

        case 3:
            # Edit Student 
            roll_to_edit = input("Enter Student Roll Number For Edit: ")
            edit_student(roll_to_edit)

        case 4:
            # Delete Student 
            roll_to_delete = input("Enter Student Roll Number For Delete: ")
            delete_student(roll_to_delete)

        case _:
            # Default case for invalid number
            print("\n[ERROR] Invalid choice. Please select a number from 1 to 5.")
