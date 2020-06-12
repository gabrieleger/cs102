import multiprocessing
import random
import time

import numpy
import psutil


def heavy_computation(data_chunk):
    M = 1100
    a = numpy.array([[random.randint(M * (-data_chunk), M * data_chunk)
                      for _ in range(M)] for _ in range(M)])
    b = numpy.array([[random.randint(M * (-data_chunk), M * data_chunk)
                      for _ in range(M)] for _ in range(M)])
    c = numpy.array([[random.randint(M * (-data_chunk), M * data_chunk)
                      for _ in range(M)] for _ in range(M)])
    x = a * b * c
    return x


def memory_to_int(memory_usage):
    m = memory_usage.upper()
    try:
        size = int(m)
        return size
    except Exception:
        if not m[-2:-1].isdigit():
            size = int(m[:-2])
            units = m[-2:]
            units_dict = {
                'GB': 1,
                'MB': 1024,
                'KB': 1024 * 1024,
            }
            size = size / units_dict[units]
        else:
            size = int(m[:-1]) / 1024 ** 3
        return round(size, 3)


class ProcessPool:
    def __init__(self, min_workers=2, max_workers=40, memory_usage='2GB'):
        self.memory_usage = memory_to_int(memory_usage)
        self.fact_memory_usage = 0
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.avg_workers = 0
        self.memory_queue = multiprocessing.Queue()

    def map(self, computations, data):
        print('Starting test process #1 for memory usage calculation...', end='')
        t_p = multiprocessing.Process(target=computations, name='test process', args=(data.get(),))
        t_p.start()
        print(' Done!')

        print('Starting test process #2 for memory usage calculation...', end='')
        t_m = multiprocessing.Process(target=self.memory_test, name='test memory', args=(t_p.pid,))
        t_m.start()
        print(' Done!')

        print('Waiting for calculations...')
        t_p.join()
        t_m.join()
        mem_list = []

        print('Approximate memory usage calculation...')
        while not self.memory_queue.empty():
            m = self.memory_queue.get()
            mem_list.append(m)
        self.fact_memory_usage = max(mem_list)

        print(f'Max memory used in tests:    {self.fact_memory_usage * 1024}MB')
        print(f'Memory avaliable for pools:  {self.memory_usage * 1024}MB')

        if self.fact_memory_usage > self.memory_usage:
            raise Warning('Memory level is too low even for one process!')
        else:
            print('> Memory usage test verdict: OK')

        self.avg_workers = int(self.memory_usage // self.fact_memory_usage)
        print(f'Workers avaliable for established memory limit: {self.avg_workers}')
        print(f'Established workers number: from {self.min_workers} to {self.max_workers}')
        if self.avg_workers > self.max_workers:
            self.avg_workers = self.max_workers
        elif self.avg_workers < self.min_workers:
            raise Warning('Memory level is too low even for minimum workers number!')
        else:
            self.avg_workers = int(self.memory_usage // self.fact_memory_usage)
            print('> Workers memory usage test verdict: OK')

        print('Creating process pool...')
        p_list = []
        for process_number in range(self.avg_workers):
            if not data.empty():
                print(f'Creating process number {process_number}...', end='')
                p = multiprocessing.Process(target=computations, args=(data.get(),))
                p.start()
                p_list.append(p)
                print(f' Done! Pool id {p.pid}')
            else:
                for pp in p_list:
                    pp.join()
                return self.avg_workers, self.fact_memory_usage
        print(f'> Process pool created')

        while True:
            for p in p_list:
                p.join(0.001)
                if not p.is_alive():
                    print(f'Process with id {p.pid} finished! Terminating...', end='')
                    p.terminate()
                    if not data.empty():
                        print(' Creating new process instead of old one...', end='')
                        p_list.remove(p)
                        pp = multiprocessing.Process(target=computations,
                                                     args=(data.get(),))
                        pp.start()
                        p_list.append(pp)
                        print(f' Done! New process id {pp.pid}')
                    else:
                        for pp in p_list:
                            pp.join()
                        return self.avg_workers, self.fact_memory_usage

    def memory_test(self, pid):
        print('Initializing memory queue...', end='')
        p_mem = psutil.Process(pid)
        while psutil.pid_exists(pid):
            try:
                self.memory_queue.put(p_mem.memory_info().rss // 1000000 / 1000)
            except:
                pass
            time.sleep(0.01)
        print(' Done!', flush=True)


if __name__ == '__main__':
    q = multiprocessing.Queue()
    for i in range(5):
        q.put(i * 100)

    pool = ProcessPool()
    print(pool.map(heavy_computation, q))
