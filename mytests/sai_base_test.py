"""
Base classes for test cases

Tests will usually inherit from one of these classes to have the controller
and/or dataplane automatically set up.
"""

import ptf
from ptf.base_tests import BaseTest
from ptf import config
import ptf.testutils as testutils
import ptf.thriftutils as thriftutils

import os
################################################################
#
# Thrift interface base tests
#
################################################################

import bm_runtime
from bm_runtime.standard import Standard
from bm_runtime.standard.ttypes import *

try:
    from bm_runtime.simple_pre import SimplePre
except:
    pass
try:
    from bm_runtime.simple_pre_lag import SimplePreLAG
except:
    pass

import bmpy_utils as utils

from thrift.Thrift import TException, TApplicationException
from runtime_CLI import int_to_bytes, bytes_to_string


class AGFBaseTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.standard_client = utils.thrift_connect_standard('localhost', 9090)

        self.context = 0
        ip = "10.0.1.1"
        self.ip_rule = [int(b) for b in ip.split('.')]
        mac = "08:00:00:00:01:11"
        self.mac_rule = bytes_to_string([int(b, 16) for b in mac.split(':')])
        port_bytes = int_to_bytes(1, (9 + 7) // 8)  # 9 is the bitwidth of the port argument
        self.port_rule = bytes_to_string(port_bytes)

        # see line 558 of https://github.com/p4lang/behavioral-model/blob/main/tools/runtime_CLI.py
        self.prefix_len_rule = 24

        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()
        if config["log_dir"] is not None:
            filename = os.path.join(config["log_dir"], str(self)) + ".pcap"
            self.dataplane.start_pcap(filename)

    def tearDown(self):
        if config["log_dir"] is not None:
            self.dataplane.stop_pcap()
        testutils.reset_filters()
        BaseTest.tearDown(self)

        # self.transport.close()

    def addIPv4Route(self):
        try:
            lpm_param = BmMatchParamLPM(key=bytes_to_string(self.ip_rule),
                                        prefix_length=self.prefix_len_rule)
            param = BmMatchParam(type=BmMatchParamType.LPM, lpm=lpm_param)
            res = self.standard_client.bm_mt_add_entry(self.context, "MyIngress.ipv4_lpm", [param],
                                         "MyIngress.ipv4_forward", [self.mac_rule, self.port_rule],
                                                       BmAddEntryOptions(priority=0))
            self.entry_handle = self.standard_client.bm_mt_get_entry_from_key(0, "MyIngress.ipv4_lpm", [param])
            print(self.entry_handle)
            print(res)


        except TApplicationException as err:
            print("haz "+ err.message)
        except TException as err:
            print("haz {0}", err.message)

    def setIPv4Rules(self, ip, mac, port):
        self.ip_rule = ip
        self.mac_rule = mac
        self.port_rule = port
