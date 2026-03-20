import functools

a = [1, 2, 3, 4, 5]
b = map(lambda x: x**2, a)
print(list(b))

def f(c):
    return c * 9/5 + 32

c = [0, 20, 30, 40]
d = list(map(f, c))
print(d)

e = [1, 2, 3]
f2 = [4, 5, 6]
g = list(map(lambda x, y: x + y, e, f2))
print(g)

a = [1,2,3,4,5,6,7,8,9,10]
b = list(filter(lambda x: x % 2 == 0, a))
print(b)

c = [1, None, 2, None, 3, 0, 4]
d = list(filter(lambda x: x is not None, c))
print(d)

e = list(filter(None, c))
print(e)

a = [1,2,3,4,5]
b = reduce(lambda x, y: x + y, a)
print(b)

c = reduce(lambda x, y: x + y, a, 10)
print(c)

d = reduce(lambda x, y: x if x > y else y, a)
print(d)

e = [("a",1),("b",2),("c",3)]
f = reduce(lambda x, y: {**x, y[0]: y[1]}, e, {})
print(f)


a = [1,2,3,4,5,6,7,8,9,10]

b = filter(lambda x: x % 2 == 0, a)
c = map(lambda x: x**2, b)
d = reduce(lambda x, y: x + y, c, 0)

print(d)

r = reduce(lambda x, y: x + y,
           map(lambda x: x**2,
               filter(lambda x: x % 2 == 0, a)),
           0)
print(r)

r = sum(x**2 for x in a if x % 2 == 0)
print(r)

b = [x**2 for x in a]
print(b)

c = [x for x in a if x % 2 == 0]
print(c)