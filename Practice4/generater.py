class c:
    def __init__(self,x):
        self.a = x
    def __iter__(self):
        return self
    def __next__(self):
        if(self.a >= 0):
            n = self.a
            self.a -=1
            return n
        else:
            raise StopIteration

s=int(input())
sqr = c(s)
siter = iter(sqr)
for i in siter:
    print(i)