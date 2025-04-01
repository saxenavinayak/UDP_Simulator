# UDP Channel Data Transfer
This program simulates reliable, data-loss data transfer for a UDP channel.

# Components
## network_emulator
This script will act as a "middleware" to simulate a UDP channel, it will consume packets from an incoming port, and with drop probability d, will drop packets.
**Usage**
`python3 network_emulator.py $senderEmulatorPort $emulatorRecieverPort $recieverEmulatorPort $emulatorSenderPort $dropProbability`
Or you can simply run the script provided start_nEmulator, it has the params pre-defined
`./start_nEmulator`


## Sender
This script will send packets, given a filename, and the IP and port number of the reciever. It will wait timeout milliseconds for an ack before re-sending packets.
**Usage**
`python3 sender.py $ip_address $forward_port_number $backward_port_number $timeout $filename`
A similar script is provided
`./start_sender`

## Reciever
This script will recieve packets, write to a file filename, and send acks when chunks are successfully recieved. If out of order, it will cache the packets using their sequence numbers and correctly sort them a later time.
**Usage**
`python3 reciever.py  $ip_address $forward_port_number $backward_port_number $filename`
Again a script is provided
`./start_reciever`
# Data Flow
![title](https://raw.githubusercontent.com/saxenavinayak/UDP_Simulator/refs/heads/main/images/dataflow.png)
