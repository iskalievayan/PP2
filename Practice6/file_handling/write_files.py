with open("demofile.txt", "a") as f:
  f.write("Now the file has more content!")
f.close()

with open("demofile.txt") as f:
  print(f.read()) 
f.close()
with open("demofile.txt", "w") as f:
  f.write("Woops! I have deleted the content!")
f.close()

with open("demofile.txt") as f:
  print(f.read()) 
f.close()
