# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Thrift SAI interface basic tests
"""

import time
import logging

import ptf.dataplane as dataplane
import sai_base_test

from ptf.testutils import *

from bm_runtime.standard.ttypes import  *

from ptf.mask import Mask



@group("group_1")
class SimpleForward(sai_base_test.AGFBaseTest):
    def runTest(self):
        print()
        print("Sending packet ")
        vlan_id = 10
        port1 = 0
        port2 = 1
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = 1

        self.addIPv4Route()


        pkt = simple_tcp_packet(eth_dst='00:11:11:11:11:11',
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.0.1.1',
                                ip_id=101,
                                ip_ttl=64)

        try:
            # in tuple: 0 is device number, 2 is port number
            # this tuple uniquely identifies a port
            send_packet(self, (0, 2), pkt)
            verify_packets(self, pkt, device_number=0, ports=[1])
            # or simply
            # send_packet(self, 2, pkt)
            # verify_packets(self, pkt, ports=[1])
        finally:
            print("sending was a success, please check table of switch to verify tables")
