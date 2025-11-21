import random

# Initialize turns counter
turns = 0

# Generate a random number between 1 and 100 (inclusive)
num = random.randint(1, 100) 

# Inform the user about the game
print("Computer selected a number from 1 to 100 inclusive.") # (1:11)
print("Now it's your turn.") 

# Game loop
while True: 
    # Get user input for their guess
    guess = int(input("Enter the guess number: ")) 

    # Check if the guess is correct
    if guess == num: 
        print("You got it right!") 
        break 
    # Check if the guess is too low
    elif guess < num: 
        print("Bigger number please.") 
        turns += 1 
    # Check if the guess is too high
    elif guess > num: # (3:24)
        print("Lesser number please.") 
        turns += 1 

# Print the total number of turns taken
print("Number of turns = ", turns + 1) 