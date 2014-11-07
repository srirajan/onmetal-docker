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

import os
import sys
import pyrax
import utils
import config
import time
import urllib
import json
import time
import haslib


pyrax.set_setting("identity_type", "rackspace")
pyrax.set_setting("region", config.cloud_region)
try:
    pyrax.set_credentials(config.cloud_user,
                          config.cloud_api_key,
                          region=config.cloud_region)
except pyrax.exc.AuthenticationFailed:
    utils.log_msg(" ".join(["Pyrax auth failed using", config.cloud_user]),
                  "ERROR",
                  config.print_to)

utils.log_msg(" ".join([ "Authenticated using", config.cloud_user]),
              "INFO",
              config.print_to)

etcd_url = "http://etcd_host:4001/v2/keys/services/web/web"

for i in xrange(1,10):
    main_url = etcd_url + str(i)
    load_main_url = urllib.urlopen(main_url);
    main_data  = json.loads(load_main_url.read())
    if main_data.has_key('errorCode'):
        print "Got error code: ", main_data['errorCode'], " Skipping..."
    else:
        node_url = urllib.urlopen(main_url + "/public_ipv4_addr");
        node_data = json.loads(node_url.read())
        if node_data.has_key('node'):
            ip = node_data['node']['value']

        node_url = urllib.urlopen(main_url + "/port");
        node_data = json.loads(node_url.read())
        if node_data.has_key('node'):
            port = node_data['node']['value']
        add_server(ip, port)


def add_server(ip, port):
  url = "".join(["http://", ip , ":", str(port), "/", config.server_health_url])
  try:

    urlobj = urllib2.urlopen(url,timeout = 5 )
    urldata = urlobj.read()
    sha1 = hashlib.sha1()
    sha1.update(urldata)
    if sha1.hexdigest() == config.server_health_url_digest:
      utils.log_msg(" ".join([server_log_id, "Health test passed. Adding to load balancer"]),
                    "INFO",
                    config.print_to)

      # Add to load balancer pool
      clb = pyrax.cloud_loadbalancers
      if clb is None:
          utils.log_msg(" ".join([server_log_id, "Failed to get load balancer object"]),
                        "ERROR", config.print_to)

      else:
          lb_name = config.clb_name
          vip_found = False
          lb_error = False
          attempts = 5
          while True:
              if attempts == 0:
                  utils.log_msg(" ".join([server_log_id, "Max attempts reached to get load balancer listing"]),
                                "ERROR", config.print_to)
                  lb_error = True
                  break
              try:
                  for lb in clb.list():
                      if lb.name == lb_name:
                          utils.log_msg(" ".join([server_log_id, "Load balancer pool",
                                                  lb_name, "found"]),
                                          "INFO",
                                          config.print_to)
                          lb_id = lb.id
                          vip_found = True
                          break
              except (pyrax.exceptions.OverLimit,pyrax.exceptions.ClientException) as e:
                  time.sleep(config.clb_limit_sleep)
                  continue
                  attempts = attempts - 1
              break

          if vip_found == True and lb_error == False:
              skip_node = False
              attempts = 5
              while True:
                  if attempts == 0:
                      utils.log_msg(" ".join(["Max attempts reached to get load balancer node list"]),
                                    "ERROR", config.print_to)
                      lb_error = True
                      break
                  try:
                      lb = clb.get(lb_id)
                      if hasattr(lb, 'nodes'):
                          for node in lb.nodes:
                              if node.address == ip:
                                  skip_node = True
                      if skip_node:
                          utils.log_msg(" ".join(["Skipping node as it already exists"]),
                                        "INFO",
                                        config.print_to)
                      else:
                          node = clb.Node(address=ip, port=port, condition="ENABLED")
                          utils.log_msg(" ".join(["Adding server to load balancer"]),
                                        "INFO",
                                        config.print_to)
                          attempts = 5
                          while True:
                              if attempts == 0:
                                  utils.log_msg(" ".join(["Max attempts reached to get load balancer listing"]),
                                              "ERROR", config.print_to)
                                  lb_error = True
                                  break
                              try:
                                  lb = clb.get(lb_id)
                                  pyrax.utils.wait_until(lb, "status", "ACTIVE",
                                             interval=config.clb_build_check_interval,
                                             attempts=config.clb_build_check_attempts,
                                             verbose=False)
                                  lb.add_nodes([node])

                              except (pyrax.exceptions.OverLimit,pyrax.exceptions.ClientException) as e:
                                  time.sleep(config.clb_limit_sleep)
                                  continue
                                  attempts = attempts - 1
                              break

                  except pyrax.exceptions.OverLimit,e:
                      time.sleep(config.clb_limit_sleep)
                      continue
                      attempts = attempts - 1
                  break

  except urllib2.URLError:
    utils.log_msg(" ".join(["Health test failed. Skipping server..."]),
            "ERROR", config.print_to)

