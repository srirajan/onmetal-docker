#!/usr/bin/env python
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function
from termcolor import colored
import sys
import datetime
import os
import config
import string
    
color_debug = "yellow"
color_error = "red"
color_pass = "green"


def log_msg(msg, type, fileobj):
    if config.print_color:
        if type == "ERROR" or type == "FAIL":
            print_color = "red"
        if type == "PASS" or type == "NORMAL" or type == "INFO":
            print_color = "green"
        if type == "DEBUG":
            print_color = "yellow"
        print(colored("".join(["[", datetime.datetime.now().strftime('%x %X'), "]:", msg]),
                      print_color), file=fileobj)
    else:
        print("".join(["[", datetime.datetime.now().strftime('%x %X'), "]",
                              "[", type, "]:", msg])
                      , file=fileobj)

