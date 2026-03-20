
f = open("demofile.txt")
print(f.read()) 


with open("demofile.txt") as f:
  print(f.read()) 
f.close() 

with open("demofile.txt") as f:
  print(f.read(5)) 

with open("demofile.txt") as f:
  print(f.readline()) 