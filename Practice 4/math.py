# Task 1: Convert degrees to radians
import math

degree = float(input("Input degree: "))
radian = degree * math.pi / 180   # Formula: radians = degrees × (π / 180)

print("Output radian:", round(radian, 6))  # Round to 6 decimal places for clean output


# Task 2: Calculate the area of a trapezoid
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))

area = 0.5 * height * (base1 + base2)  # Formula: A = ½ × h × (b1 + b2)

print("Expected Output:", area)


# Task 3: Calculate the area of a regular polygon
import math

n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))

area = (n * s * s) / (4 * math.tan(math.pi / n))  # Formula for a regular n-sided polygon

print("The area of the polygon is:", round(area))  # Round to the nearest whole number


# Task 4: Calculate the area of a parallelogram
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))

area = base * height  # Formula: A = base × height

print("Expected Output:", float(area))  # float() ensures the output always shows as a decimal




