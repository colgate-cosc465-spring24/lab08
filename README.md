# Lab 08: Stop-and-Wait Automatic Repeat reQuest (ARQ) Simulator

## Overview
In this lab, you will implement the sender side of a simple stop-and-wait Automatic Repeat reQuest (ARQ) protocol that transmits data in only one direction (and acknowledgements in the reverse direction).

### Learning objectives
After completing this lab, you should be able to:
* Explain how acknowledgments and timeouts are used to guarantee packets are delivered
* Demonstrate the importance of conforming to protocol standards

## Getting started
Clone your git repository on a `tigers` server. 

As you work on this lab, you may want to consult [Section 2.5.1](https://book.systemsapproach.org/direct/reliable.html#stop-and-wait) of _Computer Networks: A Systems Approach_.

### Packets
The `Packet` class defined in `stop_and_wait.py` is used to represent a data or acknowledgement (ACK) packet. Every packet contains:
* The character `D` or `A`, which indicates whether it is a <span style="text-decoration:underline;">D</span>ata or <span style="text-decoration:underline;">A</span>CK packet
* A sequence number
* Up to 1400 bytes of data (only in data packets)

This object-based representation of a packet can be converted to a sequence of bytes to be sent across the network using the `to_bytes` method. Conversely, a sequence of bytes received from the network can be converted to an object-based representation using the `Packet.from_bytes` method.

The sender and receiver both interact with a simple lower layer protocol that sends and receives packets across the network on behalf of the stop-and-wait ARQ protocol. The `LowerLayerEndpoint` class in `lower_layer.py` exposes a basic API for sending and receiving a packet—really just a sequence of bytes—to/from a "remote" endpoint.

## Implement sender
You are responsible for implementing the sender side of a stop-and-wait ARQ protocol by completing the `Sender` class in `stop_and_wait.py`. 

The sender must do three things:
1. Send a data packet. If there is already an outstanding unACK'd data packet, then the caller (e.g., an application) will be blocked until the outstanding data has been ACK'd.
2. Retransmit the data packet if it is not ACK'd within a predetermined amount of time.
3. Discard data once it has been successfully ACK'd, thus enabling new data to be sent.

These tasks should be handled by the `_send`, `_retransmit`, and `_recv` functions, respectively, within the `Sender` class. As you write the code, I recommend you add some debugging statements—use the function `logging.debug` instead of `print`—to make it easier to trace your code’s execution.

### `_send`

The `_send` function is invoked by the `send` function which is invoked by an "application" (e.g., `client.py`). The `_send` function needs to:
1. Wait until the next data packet can be sent—a [semaphore](https://docs.python.org/3.8/library/threading.html#semaphore-objects) is the simplest way to handle this.
2. Save the chunk of data—in case it needs to be retransmitted.
3. Send the data in a packet with the appropriate type (`D`) and sequence number—use the `Packet` class to construct such a packet and use the `send` method provided by the `LowerLayerEndpoint` class to transmit the packet across the network.
4. Start a retransmission timer—the [Timer](https://docs.python.org/3.8/library/threading.html#timer-objects) class provides a convenient way to do this; the timeout should be 1 second, defined by the constant `Sender._TIMEOUT`; when the timer expires, the `_retransmit` method should be called.

### `_retransmit`
The `_retransmit` function is invoked whenever a retransmission timer—started in `_send` or a previous invocation of `_retransmit`—expires. The `_retransmit` function needs to complete steps 4 and 5 performed by the `_send `function.

### `_recv`
The `_recv` function runs as a separate thread—started when an `Sender` is created—and receives packets from the lower layer until the sender is shutdown. The sender should only receive ACK packets—you should ignore any packets that aren’t ACKs. Every time a chunk of data is ACK’d, the `_recv` function needs to:
1. Cancel the retransmission timer.
2. Discard the data that has been ACK'd.
3. Signal that the next data packet can be sent.

## Testing and debugging
To test your code:
1. Start the server using the command: 
```bash
./server.py -p PORT
```
replacing `PORT` with a port number.
2. In a separate terminal window, start the client using the command:
```bash
./client.py -p PORT
```
replacing `PORT` with the port number you specified when you started the server.
3. Type something into the client and hit enter; the data should appear on the server.

To test your retransmission code, include the command line argument `-l PROBABILITY` (that is a lowercase L) when you start the client and/or the server. Replace `PROBABILITY` with a decimal number between `0.0` to `1.0` (inclusive), indicting the probability that a packet is dropped. If you pass this option to the client, then packets may be dropped. If you pass this option to the server, then ACK packets may be dropped.

## Self-assessment
The self-assessment for this lab will be available on Moodle on Friday, March 29th. Please complete the self-assessment by 11pm on Monday, April 1st.

