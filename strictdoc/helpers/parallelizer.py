import concurrent
import multiprocessing

from concurrent.futures import ProcessPoolExecutor


class Parallelizer:
    @staticmethod
    def create(parallelize):
        if parallelize:
            return Parallelizer()
        else:
            return NullParallelizer()

    def map(self, contents, processing_func):
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            result = executor.map(processing_func, contents)
            return result


class NullParallelizer:
    @staticmethod
    def map(contents, processing_func):
        results = []
        for content in contents:
            results.append(processing_func(content))
        return results
