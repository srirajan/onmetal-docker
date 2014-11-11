#!/usr/bin/env python
# All Rights Reserved.
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
import urllib2
import json
import time
import hashlib

"""
Health check the server and call add or remove
"""

def process_server(ip, port):
  global config_res
  url = "".join(["http://", ip , ":", str(port), "/", config_res["SERVER_HEALTH_URL"]])
  try:
    urlobj = urllib2.urlopen(url,timeout = 5 )
    urldata = urlobj.read()
    sha1 = hashlib.sha1()
    sha1.update(urldata)
    if sha1.hexdigest() == config_res["SERVER_HEALTH_DIGEST"]:
      utils.log_msg(" ".join(["Health test passed. Adding to load balancer"]),
                    "INFO",
                    config.print_to)
      add_server(ip, port)
    else:
      utils.log_msg(" ".join(["Health test failed - Hash mismatch. Expecting", sha1.hexdigest(), "Calling remove"]),
                    "INFO",
                    config.print_to)
      remove_server(ip, port)

  except urllib2.URLError:
    utils.log_msg(" ".join(["Health test failed - Url timeout.", "Calling remove"]),
            "ERROR", config.print_to)
    remove_server(ip, port)

"""
Remove a server from the load balancer
"""

def remove_server(ip, port):
  global config_res
  clb = pyrax.cloud_loadbalancers
  if clb is None:
      utils.log_msg(" ".join(["Failed to get load balancer object"]),
                    "ERROR", config.print_to)
  else:
      lb_name = config_res["LB_NAME"]
      vip_found = False
      lb_error = False
      attempts = 5
      while True:
          if attempts == 0:
              utils.log_msg(" ".join(["Max attempts reached to get load balancer listing"]),
                            "ERROR", config.print_to)
              lb_error = True
              break
          try:
              for lb in clb.list():
                  if lb.name == lb_name:
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
          attempts = 3
          node_found = False
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
                        if node.address == ip and str(node.port) == port:
                          node_found = True
                          utils.log_msg(" ".join(["Removing server from load balancer"]),
                                        "INFO",
                                        config.print_to)
                          attempts = 3
                          while True:
                              if attempts == 0:
                                  utils.log_msg(" ".join(["Max attempts reached to get load balancer listing"]),
                                              "ERROR", config.print_to)
                                  lb_error = True
                                  break
                              try:
                                  pyrax.utils.wait_until(lb, "status", "ACTIVE",
                                             interval=config.clb_build_check_interval,
                                             attempts=config.clb_build_check_attempts,
                                             verbose=False)
                                  node.delete()

                              except (pyrax.exceptions.OverLimit,pyrax.exceptions.ClientException) as e:
                                  utils.log_msg(" ".join(["Caught pyrax.exceptions.OverLimit"]),
                                              "ERROR", config.print_to)
                                  time.sleep(config.clb_limit_sleep)
                                  attempts = attempts - 1
                                  continue
                      if not node_found:
                        utils.log_msg(" ".join(["Node not found"]),
                                      "INFO", config.print_to)
                        return

              except pyrax.exceptions.OverLimit,e:
                  utils.log_msg(" ".join(["Caught pyrax.exceptions.OverLimit"]),
                              "ERROR", config.print_to)
                  time.sleep(config.clb_limit_sleep)
                  attempts = attempts - 1
                  continue
              break


"""
Add a server to the load balancer
"""

def add_server(ip, port):
  global config_res
  clb = pyrax.cloud_loadbalancers
  if clb is None:
      utils.log_msg(" ".join(["Failed to get load balancer object"]),
                    "ERROR", config.print_to)
  else:
      lb_name = config_res["LB_NAME"]
      vip_found = False
      lb_error = False
      attempts = 3
      while True:
          if attempts == 0:
              utils.log_msg(" ".join(["Max attempts reached to get load balancer listing"]),
                            "ERROR", config.print_to)
              lb_error = True
              break
          try:
              for lb in clb.list():
                  if lb.name == lb_name:
                      utils.log_msg(" ".join(["Load balancer pool",
                                              lb_name, "found"]),
                                      "INFO",
                                      config.print_to)
                      lb_id = lb.id
                      vip_found = True
                      break
          except (pyrax.exceptions.OverLimit,pyrax.exceptions.ClientException) as e:
              utils.log_msg(" ".join(["Caught pyrax.exceptions.OverLimit"]),
                          "ERROR", config.print_to)
              time.sleep(config.clb_limit_sleep)
              attempts = attempts - 1
              continue
          break

      if vip_found == True and lb_error == False:
          skip_node = False
          attempts = 3
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
                        if node.address == ip and str(node.port) == port:
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
                      attempts = 3
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
                              utils.log_msg(" ".join(["Caught pyrax.exceptions.OverLimit"]),
                                          "ERROR", config.print_to)
                              attempts = attempts - 1
                              continue
                          break

              except pyrax.exceptions.OverLimit,e:
                  utils.log_msg(" ".join(["Caught pyrax.exceptions.OverLimit"]),
                              "ERROR", config.print_to)
                  time.sleep(config.clb_limit_sleep)
                  continue
                  attempts = attempts - 1
              break

"""
Print a summary
"""

def print_summary():
  clb = pyrax.cloud_loadbalancers
  if clb is None:
      utils.log_msg(" ".join(["Failed to get load balancer object"]),
                    "ERROR", config.print_to)
  else:
      lb_name = config_res["LB_NAME"]
      vip_found = False
      lb_error = False
      attempts = 5
      utils.log_msg(" ".join(["Printing summary"]),
                      "INFO",
                      config.print_to)
      while True:
          if attempts == 0:
              utils.log_msg(" ".join(["Max attempts reached to get load balancer listing"]),
                            "ERROR", config.print_to)
              lb_error = True
              break
          try:
              for lb in clb.list():
                  if lb.name == lb_name:
                      utils.log_msg(" ".join(["Load balancer pool",
                                              lb_name, "found"]),
                                      "INFO",
                                      config.print_to)
                      my_lb = clb.get(lb.id)
                      if hasattr(lb, 'nodes'):
                        for node in my_lb.nodes:
                          utils.log_msg(" ".join(["Nodes:",
                                              node.address, str(node.port)]),
                                      "INFO",
                                      config.print_to)
                        break
          except (pyrax.exceptions.OverLimit,pyrax.exceptions.ClientException) as e:
              time.sleep(config.clb_limit_sleep)
              continue
              attempts = attempts - 1
          break

if __name__ == '__main__':

    config_qry = ["OS_USERNAME", "OS_REGION", "OS_PASSWORD", "OS_TENANT_NAME", 
                  "LB_NAME", "SERVER_HEALTH_URL", "SERVER_HEALTH_DIGEST"]
    config_res = {}
    etcd_rscloud_url = "http://etcd_host:4001/v2/keys/services/rscloud"
    for cfg in config_qry:
      conf_url = urllib.urlopen(etcd_rscloud_url + "/" + cfg);
      conf_data = json.loads(conf_url.read())
      if conf_data.has_key('node'):
          config_res[cfg] = conf_data['node']['value']
          #print config_res[cfg]

    pyrax.set_setting("identity_type", "rackspace")
    pyrax.set_setting("region", config_res["OS_REGION"])
    try:
        pyrax.set_credentials(config_res["OS_USERNAME"],
                          config_res["OS_PASSWORD"],
                          region=config_res["OS_REGION"])
    except pyrax.exc.AuthenticationFailed:
        utils.log_msg(" ".join(["Pyrax auth failed using", config_res["OS_USERNAME"]]),
                  "ERROR",
                  config.print_to)

    utils.log_msg(" ".join([ "Authenticated using", config_res["OS_USERNAME"]]),
              "INFO",
              config.print_to)

    etcd_url = "http://etcd_host:4001/v2/keys/services/web/web"

    config_qry = ["SERVER_HEALTH_URL", "SERVER_HEALTH_DIGEST"]
    while True:
      etcd_rscloud_url = "http://etcd_host:4001/v2/keys/services/rscloud"
      for cfg in config_qry:
        conf_url = urllib.urlopen(etcd_rscloud_url + "/" + cfg);
        conf_data = json.loads(conf_url.read())
        if conf_data.has_key('node'):
            config_res[cfg] = conf_data['node']['value']

      for i in xrange(1, config.server_max_count):
          main_url = etcd_url + format(i,'02')
          load_main_url = urllib.urlopen(main_url);
          main_data  = json.loads(load_main_url.read())
          if main_data.has_key('errorCode'):
              utils.log_msg(" ".join(["web", format(i , '02') , "does not exist.Skipping..."]),
                        "INFO",
                        config.print_to)
          else:
              utils.log_msg(" ".join(["web", format(i , '02') , "Found. Processing server"]),
                        "INFO",
                        config.print_to)
              node_url = urllib.urlopen(main_url + "/public_ipv4_addr");
              node_data = json.loads(node_url.read())
              if node_data.has_key('node'):
                  ip = node_data['node']['value']

              node_url = urllib.urlopen(main_url + "/port");
              node_data = json.loads(node_url.read())
              if node_data.has_key('node'):
                  port = node_data['node']['value']
              process_server(ip, port)

      print_summary()
      utils.log_msg(" ".join(["Sleeping", str(config.server_loop_sleep ) , "seconds..."]),
                "INFO",
                config.print_to)
      time.sleep(config.server_loop_sleep)
