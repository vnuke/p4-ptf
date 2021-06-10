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

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.Thrift import TException, TApplicationException

class SAIThriftTest(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)

        test_params = testutils.test_params_get()
        print("You specified the following test-params when invoking ptf:")
        for k, v in test_params.items():
            print(k, ":\t\t\t", v)

        # Set up thrift client and contact server
        self.transport = TSocket.TSocket('localhost', 9092)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = Client(self.protocol)
        self.transport.open()

    def tearDown(self):
        BaseTest.tearDown(self)
        self.transport.close()


class SAIThriftDataplaneTest(SAIThriftTest):

    def setUp(self):
        SAIThriftTest.setUp(self)

        # shows how to use a filter on all our tests
        testutils.add_filter(testutils.not_ipv6_filter)

        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()
        if config["log_dir"] != None:
            filename = os.path.join(config["log_dir"], str(self)) + ".pcap"
            self.dataplane.start_pcap(filename)

    def tearDown(self):
        if config["log_dir"] != None:
            self.dataplane.stop_pcap()
        testutils.reset_filters()
        SAIThriftTest.tearDown(self)


class AGFBaseTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.transport = TSocket.TSocket('localhost', 9092)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = Client(self.protocol)
        self.transport.open()

        self.context = 1

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

    def addIPv4Route(self, ip, mac, port):
        try:
            self.client.bm_mt_add_entry(self.context, "MyIngress.ipv4_lpm", ip, "MyIngress.ipv4_forward", [mac, port])
        except TApplicationException as err:
            print(err)
        except TException as err:
            print("{0}", err.message)

