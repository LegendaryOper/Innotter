from innotter.celery import app

@app.task()
def test_celery():
    print('celery is works!!!!!!')