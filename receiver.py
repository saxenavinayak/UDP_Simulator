from socket import *
import sys
import os
from packet import Packet

# print("Correct usage: ./client.sh <server_address> <n_port> <command> <filename>")

nEmulator_host_name = sys.argv[1] # This host will send me data
nEmulator_backwards_port = int(sys.argv[2]) # I will send ACKs to this port, and the address above
reciever_port = int(sys.argv[3]) # I will listen on this port to recieve data
filename = sys.argv[4] # Write contents of file here

arrival_log = []
def check_if_next_packet_in_buffer(next_expected_packet, buffer):
    if next_expected_packet in buffer:
        return True
    return False

# New UDP socket for reciever, will listen on it for data

recieverSocket = socket(AF_INET, SOCK_DGRAM)
recieverSocket.bind(('', reciever_port))

next_expected_packet_seq_num = 0
buffer = {}
# Clear data
with open(filename, 'w'):
    pass
while True:
    packet, address = recieverSocket.recvfrom(2048)
    packet_type, seqnum, length, data = Packet(packet).decode()
    # if next_expected_packet_seq_num == seqnum: # Check the sequence number of the packet
    if packet_type == 2 and length == 0: # packet is of type EOT
        recieverSocket.sendto(packet, (nEmulator_host_name, nEmulator_backwards_port))
        arrival_log.append("EOT")
        recieverSocket.close()
        break
    else:
        arrival_log.append(seqnum)
        # Send an ACK for the packet
        ack_packet = Packet(0, seqnum, 0, "")
        print("Sending ACK packet for sequence number: ", seqnum)
        recieverSocket.sendto(ack_packet.encode(), (nEmulator_host_name, nEmulator_backwards_port))
        if seqnum not in buffer: # If the packet was not previously recieved, add it to buffer
            buffer[seqnum] = data
            with open(filename, 'a') as file: # Check if we can write to our file with an updated buffer
                while check_if_next_packet_in_buffer(next_expected_packet_seq_num, buffer):
                    file.write(buffer[next_expected_packet_seq_num])
                    buffer.pop(next_expected_packet_seq_num)
                    next_expected_packet_seq_num = (next_expected_packet_seq_num + 1) 

# Write to log files
with open("arrival.log", 'w') as logfile:
    for item in arrival_log:
        logfile.write(str(item) + "\n")