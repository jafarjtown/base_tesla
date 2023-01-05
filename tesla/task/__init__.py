import multiprocessing as mp

class _Task:
    
    def add_tast(self, target, *args, **kwargs):
        p = mp.Process(target=target, args=args, kwargs=kwargs)
        p.start()


process = _Task()