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
from bm_runtime.standard.Standard import Client
from bm_runtime.standard.ttypes import *

import bmpy_utils

from thrift.Thrift import TException, TApplicationException


class AGFBaseTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        bmpy_utils.thrift_connect_standard('localhost', 9090)

        self.context = 1

        self.ip_rule = "10.0.1.1"
        self.mac_rule = "08:00:00:00:01:11"
        self.port_rule = "1"

        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()
        if config["log_dir"] != None:
            filename = os.path.join(config["log_dir"], str(self)) + ".pcap"
            self.dataplane.start_pcap(filename)
	

    def tearDown(self):
        if config["log_dir"] != None:
            self.dataplane.stop_pcap()
        testutils.reset_filters()
        BaseTest.tearDown(self)
        self.transport.close()

    def addIPv4Route(self):
        try:
            print(self.client.bm_mgmt_get_info())
            mtEntry = BmMatchParamLPM(key=self.ip_rule, prefix_length=24)
            params = BmMatchParam(type=BmMatchParamType.LPM, lpm=mtEntry)

            self.client.bm_mt_add_entry(self.context, "MyIngress.ipv4_lpm", [params],
                                        "MyIngress.ipv4_forward", [self.mac_rule, self.port_rule], None)

        except TApplicationException as err:
            print(err)
        except TException as err:
            print("{0}", err.message)

    def setIPv4Rules(self, ip, mac, port):
        self.ip_rule = ip
        self.mac_rule = mac
        self.port_rule = port
