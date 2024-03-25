import enum
import logging
import lower_layer
import queue
import struct
import threading

class PacketType(enum.IntEnum):
    DATA = ord('D')
    ACK = ord('A')

class Packet:
    _PACK_FORMAT = '!BB'
    _HEADER_SIZE = struct.calcsize(_PACK_FORMAT)
    MAX_DATA_SIZE = 1400 # Leaves plenty of space for IP + UDP + SWP header 

    def __init__(self, type, seq_num, data=b''):
        self._type = type
        self._seq_num = seq_num
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def seq_num(self):
        return self._seq_num
    
    @property
    def data(self):
        return self._data

    def to_bytes(self):
        header = struct.pack(Packet._PACK_FORMAT, self._type.value, 
                self._seq_num)
        return header + self._data
       
    @classmethod
    def from_bytes(cls, raw):
        header = struct.unpack(Packet._PACK_FORMAT,
                raw[:Packet._HEADER_SIZE])
        type = PacketType(header[0])
        seq_num = header[1]
        data = raw[Packet._HEADER_SIZE:]
        return Packet(type, seq_num, data)

    def __str__(self):
        return "%s %d %s" % (self._type.name, self._seq_num, repr(self._data))

class Sender:
    _TIMEOUT = 1

    def __init__(self, remote_address, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(remote_address=remote_address,
                loss_probability=loss_probability)

        # TODO: Add additional sate variables


        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()
        
    def send(self, data):
        for i in range(0, len(data), Packet.MAX_DATA_SIZE):
            self._send(data[i:i+Packet.MAX_DATA_SIZE])

    def _send(self, data):
        # TODO
        return
        
    def _retransmit(self):
        # TODO
        return

    def _recv(self):
        while True:
            # Receive ACK packet
            raw = self._ll_endpoint.recv()
            if raw is None:
                continue
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)

            # TODO 

class Receiver:
    def __init__(self, local_address, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(local_address=local_address, 
                loss_probability=loss_probability)

        self._last_ack = 1

        # Received data waiting for application to consume
        self._ready_data = queue.Queue()

        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()

    def recv(self):
        return self._ready_data.get()

    def _recv(self):
        while True:
            # Receive data packet
            raw = self._ll_endpoint.recv()
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)

            # Put data in buffer for application to consume if not a retransmission
            if (packet.seq_num != self._last_ack):
                self._ready_data.put(packet.data)

            # Send ACK
            self._last_ack = packet.seq_num
            ack = Packet(PacketType.ACK, self._last_ack)
            self._ll_endpoint.send(ack.to_bytes())
            logging.debug("Sent: %s" % ack)
