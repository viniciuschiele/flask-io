# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import perf_counter


class Stopwatch(object):
    def __init__(self):
        self.elapsed = 0.0
        self._start = None

    @staticmethod
    def start_new():
        sw = Stopwatch()
        sw.start()
        return sw

    def start(self):
        if not self._start:
            self._start = perf_counter()

    def stop(self):
        if self._start:
            end = perf_counter()
            self.elapsed += (end - self._start)
            self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
