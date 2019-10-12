import sys
sys.path.append('/annoroad/data1/bioinfo/PMO/yangmengcheng/Work/MutConfidence-Model/')
from lib.queue_manager import queue_manager
from lib.multithreading import MultiThread
import t
queue_manager.add_queue('test')
queue = queue_manager.get_queue('test')
def rese():
    while True:
        s = queue.get()
        if s == 'EOF':
            print('get EOF, terminate!')
            return
        else:
            print(s)

def iteration():
    for i in range(5):
        yield i

def send():
    t1 = MultiThread(rese)
    t1.start()

    for i in iteration():
        #print(i)
        queue.put(i)
        #print(queue.get())
    else:
        queue.put('EOF')

send()
