from common import *


class TestA(TestCase):
    def _run(self):
        # hotswapping code a
        foo_bar_baz = self.create_module('foo.bar.bar', """\
            from houdini import hotswap

            @hotswap
            def f(n, m):
                v = n*m
                return v
        """)

        # client code
        import foo.bar.bar

        ff = foo.bar.bar.f
        fff = ff

        def probe(n, m):
            return foo.bar.bar.f(n, m), fff(n, m)

        # first test cases
        self.check(lambda: probe(10, 20) == (200, 200,))
        self.check(lambda: probe(100, 200) == (20000, 20000,))

        # change multiplication to addition
        foo_bar_baz.edit(verbatim_sub('n*m', 'n+m'))

        # second test cases
        self.check(lambda: probe(10, 20) == (30, 30,))
        self.check(lambda: probe(100, 200) == (300, 300,))

TestA().run()
