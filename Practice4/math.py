import math
import random
#eg1

numbers = [5, 2, 8, 1, 9, 3]
print("Numbers:", numbers)
print("Min:", min(numbers))
print("Max:", max(numbers))
print("Sum:", sum(numbers))

#eg 2

print("\nRandom float [0.0, 1.0):")
for _ in range(5):
    print(random.random())
    
#eg3
    
angle_deg = 90
angle_rad = math.radians(angle_deg)
print(f"\n{angle_deg} degrees = {angle_rad} radians")
print(f"sin(90°) = {math.sin(angle_rad)}")

angle_rad2 = math.pi
angle_deg2 = math.degrees(angle_rad2)
print(f"{angle_rad2} radians = {angle_deg2} degrees")

#eg4

print("\nFactorials:")
for i in range(6):
    print(f"{i}! = {math.factorial(i)}")