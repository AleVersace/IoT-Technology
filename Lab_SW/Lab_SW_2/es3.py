import threading
import json
import requests
import random
import time

class thread_device(threading.Thread):
    url = 'http://127.0.0.1:8080/devices/'
    d = {
        'id': '',
        'end-points': '',
        'resources': ['Temperature', 'Led']
    }
    def __init__(self, id):
        self.id = id
        self.time = random.randint(4, 20)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.d['id'] = self.id
            requests.post(self.url, data=json.dumps(self.d))
            time.sleep(self.time)

if __name__ == "__main__":
    threads = []

    for i in range(0, 5):
        threads.append(thread_device(i))

    for t in threads:
        t.start()
        time.sleep(60)