from common import *


class TestB(TestCase):
    def _run(self):
        # hotswapping code a
        foo_bar = self.create_module('foo.bar', """\
            import houdini

            class Kalle(object):
                def __init__(self):
                    self.xs = []

                @houdini.hotswap
                def tap(self, n):
                    self.xs.append(n)
        """)

        # hotswapping code b
        kammomille_ = self.create_module('kammomille', """\
            import houdini
            import foo.bar

            try:
                kalle
            except:
                kalle = foo.bar.Kalle()

            @houdini.hotswap
            def sjallabam():
                kalle.tap(22)
        """)

        # client code
        import kammomille

        kammomille.sjallabam()
        kammomille.sjallabam()

        # first test cases
        self.check(lambda: kammomille.kalle.xs == [22, 22])

        foo_bar.edit(verbatim_sub('append(n)', 'append(n*n)'))
        kammomille_.edit(verbatim_sub('22', '5'))

        kammomille.sjallabam()
        kammomille.sjallabam()

        # second test cases
        self.check(lambda: kammomille.kalle.xs == [22, 22, 25, 25])


TestB().run()
