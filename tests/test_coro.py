async def coro():
    x = yield
    return


def test_coro():
    c = coro()
    c.asend(1)