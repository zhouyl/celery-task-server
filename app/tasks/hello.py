import arrow
from tasks import app


@app.task
def say_hello(name):
    import random
    import time

    s = random.random() * random.randrange(4, 8)

    print("Hello, %s [%s], sleep %f seconds" % (name, arrow.get().format(), s))

    time.sleep(s)

    t = arrow.get()
    print('Now time is [%s]' % t.format())

    return t.format()
