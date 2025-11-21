import math

num1 = input("Enter the first number: ")
operator = input("Enter the operation you wish to perform (+, -, *, /): ")
num2 = input("Enter the second number: ")

num1 = float(num1)
num2 = float(num2)

if operator == "+":
    result = num1 + num2
elif operator == "-":
    result = num1 - num2
elif operator == "*":
    result = num1 * num2
elif operator == "/":
    result = num1 / num2
else:
    print("Invalid operator entered.")

print(f"{num1} {operator} {num2} = {result}")