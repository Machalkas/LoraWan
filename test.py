class D:
    constant = None


global d
d = D()


class C2:
    def __init__(self, x) -> None:
        global d
        self.D = d
        self.D.constant=x

    def this_constant(self):
        print(self.D.constant, id(self.D.constant))


an_object = C2(1)
an_object.this_constant()

x = C2(13)
x.this_constant()
print(id(x.D.constant))
x.D.constant = 12
an_object.this_constant()
