import time


class Timer:

    def __init__(self):
        self.times = []
        self.times.append(time.time())

    def _record(self):
        self.times.append(time.time())

    def print_last_step_cost(self, step_name=""):
        self._record()
        assert len(self.times) >= 2
        str_cost = self._to_str(self.times[-1] - self.times[-2])
        print(f"step:  {step_name} cost: {str_cost}")

    def print_cum_cost(self):
        self._record()
        str_cost = self._to_str(self.times[-1] - self.times[0])
        print(f"all cost: {str_cost}")

    @staticmethod
    def _to_str(seconds):
        ss = seconds % 60
        mm = int(seconds / 60) % 60
        hh = int(seconds / 60 / 60) % 24
        dd = int(seconds / 60 / 60 / 24)
        s = ''
        if dd > 0:
            s += f'{dd}天'
        if hh > 0:
            s += f'{hh}小时'
        if mm > 0:
            s += f'{mm}分'
        if ss > 0:
            s += f'{ss:.2f}秒'
        return s
