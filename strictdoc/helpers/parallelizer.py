import multiprocessing
import sys


# This might be not the most efficient way to parallelize using processes,
# however it does not produce the following problem:
# objc[24250]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called.
# The suggestion solution to this problem is to use
# OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
# which seems to be a worth hack than using a little bit slower parallelization
# algorithm below (slower means roughly 7s instead of 6s, so 6/7).
class Parallelizer:
    @staticmethod
    def create(parallelize):
        if parallelize:
            return Parallelizer()
        else:
            return NullParallelizer()

    def __init__(self):
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        self.pool = multiprocessing.Pool(multiprocessing.cpu_count(),
                                         Parallelizer._run,
                                         (self.input_queue, self.output_queue,))

    def map(self, contents, processing_func):
        size = 0
        for content in contents:
            self.input_queue.put((content, processing_func))
            size += 1
        results = []
        while size > 0:
            result = self.output_queue.get(block=True)
            results.append(result)
            size -= 1
        return results

    @staticmethod
    def _run(input_queue, output_queue):
        while True:
            content, processing_func = input_queue.get(block=True)
            result = processing_func(content)
            sys.stdout.flush()
            sys.stderr.flush()
            output_queue.put(result)


class NullParallelizer:
    @staticmethod
    def map(contents, processing_func):
        results = []
        for content in contents:
            results.append(processing_func(content))
        return results
