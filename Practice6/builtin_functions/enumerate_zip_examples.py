print("enumerate():")

a = ['apple', 'banana', 'cherry']
for i, x in enumerate(a):
    print(f"{i}: {x}")

for i, x in enumerate(a, 1):
    print(f"{i}: {x}")

b = [10, 20, 30, 20]
c = [i for i, x in enumerate(b) if x == 20]
print(c)


a = ['Alice', 'Bob', 'Charlie']
b = [85, 92, 78]

for x, y in zip(a, b):
    print(f"{x}: {y}")

c = list(zip(a, b))
print(c)

d = [1, 2]
e = ['a', 'b', 'c']
print(list(zip(d, e)))

f = ['name', 'age']
g = ['Alice', 30]
h = dict(zip(f, g))
print(h)


a = ['pen', 'pencil']
b = [1.5, 0.8]

for i, (x, y) in enumerate(zip(a, b), 1):
    print(f"{i}. {x} ${y}")