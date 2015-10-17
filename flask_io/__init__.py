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

# Make marshmallow's functions and classes importable from flask-io
from marshmallow import post_load, post_dump, Schema, ValidationError
from marshmallow.utils import missing

from .io import FlaskIO
from .errors import Error

__version__ = '1.6.0'
__author__ = 'Vinicius Chiele'
__license__ = 'Apache License 2.0'
