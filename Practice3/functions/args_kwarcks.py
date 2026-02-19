def args(*p):
    print(*p)
args(1, 2, 3, 4, 986, 123) # I can pass as many arg as i want

def kwr(**k):
    print("hello ", k("name"))
kwr(name="Ayan", age=17) # I can pass as many key word arguments as i want