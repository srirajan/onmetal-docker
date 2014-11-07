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

import sys
import os

# cloud auth data will be pulled from environment
cloud_user = os.environ['OS_USERNAME']
cloud_api_key = os.environ['OS_PASSWORD']
cloud_region = os.environ['OS_REGION_NAME'].upper()
cloud_tenant = os.environ['OS_TENANT_NAME']

# load balancer configuration
clb_name = os.environ['LB_NAME']
clb_protcol = "HTTP"
clb_limit_sleep = 10
clb_build_check_interval = 15
clb_build_check_attempts = 10

server_loop_sleep = 10
server_max_count = 100
server_health_url = os.environ['SERVER_HEALTH_URL']
server_health_url_digest = os.environ['SERVER_HEALTH_DIGEST']

print_to = sys.stdout #use this to print to screen
