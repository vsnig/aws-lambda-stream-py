def test_default_argments():
    def fn(arg1=None):
        print(arg1)

    fn()
