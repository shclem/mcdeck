from tqdm import tqdm

class MCProgress():
    __barFormat = "{desc}: {n_fmt:>3}/{total_fmt:<3}[{bar}] "

    def apply(self, iterable, desc, leave=True):
        return tqdm(iterable, desc=desc, leave=leave, bar_format=self.__barFormat)
