from socket import *
import sys
import os
from packet import Packet
from datetime import datetime
# print("Correct usage: ./client.sh <server_address> <n_port> <command> <filename>")

nEmulator_host_name = sys.argv[1] # I will send data to this host 
nEmulator_data_port = int(sys.argv[2]) # I will send data to this port
nEmulator_ACK_port = int(sys.argv[3]) # I will recieve ACKs from this port
timeout = int(sys.argv[4]) # TImeout to wait for each package
filename = sys.argv[5] # Name of file to send


def send_eot(current_seq, my_socket, host, port):
    packet_to_send = Packet(2, current_seq, 0, '')
    my_socket.sendto(packet_to_send.encode(), (host, port))





senderSocket = socket(AF_INET, SOCK_DGRAM)
senderSocket.bind(('', nEmulator_ACK_port))
senderSocket.settimeout(0)
window_size = 10
current_seqnum = 0
unacked_packets = {}
timer = None
data = None
seq_num_log = []
ack_num_log = []
EOT_FROM_SENDER = False
chunks = []
if not os.path.exists(filename):
    print("File does not exist.")
    exit(0)

with open(filename, 'rb') as file:
    while True:
        chunk = file.read(500)
        if not chunk:
            break
        chunks.append(chunk)


def get_next_chunk():
    if len(chunks) == 0:
        return b''
    else:
        return chunks.pop(0)


while True:
    # We still have pending packets to send, since there is room in window size
    if (len(unacked_packets) < window_size):
        # Read data from file
        data = get_next_chunk()
        # In the case that theres nothing in the file, and we have recieved ACK for all our packages, send EOT and exit
        if data == b'' and len(unacked_packets) == 0 and not EOT_FROM_SENDER:
            send_eot(current_seqnum, senderSocket, nEmulator_host_name, nEmulator_data_port)
            seq_num_log.append("EOT")

        # Otherwise, if there are pending packets to send, read from file and send, and start timer
        elif data != b'':
            packet_to_send = Packet(1, current_seqnum, len(data), data.decode())
            senderSocket.sendto(packet_to_send.encode(), (nEmulator_host_name, nEmulator_data_port))
            seq_num_log.append(current_seqnum)
            unacked_packets[current_seqnum] = packet_to_send
            current_seqnum = (current_seqnum + 1)
            timer = datetime.now()
    # Check if timer is up
    if ((datetime.now() - timer).total_seconds())*1000 > timeout:
        # Counter of how many packets to re-transmit
        packets_retransmitted_after_timeout = 0
        # Transmit un-acked packets
        for seq in unacked_packets:
            # If we sent 10 packets, break from loop
            # if packets_retransmitted_after_timeout == 10:
                # break
            # Retransmit packets from the queue
            packet = unacked_packets[seq]
            senderSocket.sendto(packet.encode(), (nEmulator_host_name, nEmulator_data_port))
            seq_num_log.append(seq)
            packets_retransmitted_after_timeout += 1
        # If there is still space left after transmitting un-acked packets, resend
        while packets_retransmitted_after_timeout < 10:
            # Read new data
            data = get_next_chunk()
            # If no new data, and we got all ACKs, send EOT and terminate
            if data == b'':
                if len(unacked_packets) == 0 and not EOT_FROM_SENDER:
                    send_eot(current_seqnum, senderSocket, nEmulator_host_name, nEmulator_data_port)
                    break
                else:
                    break
            elif data != b'':
            
                packet_to_send = Packet(1, current_seqnum, len(data), data.decode())
                senderSocket.sendto(packet_to_send.encode(), (nEmulator_host_name, nEmulator_data_port))
                seq_num_log.append(current_seqnum)
                unacked_packets[current_seqnum] = packet_to_send
                current_seqnum = (current_seqnum + 1)
            
                packets_retransmitted_after_timeout += 1

        # data = None
        timer = datetime.now()


    # Initalize ack_packet to None, so if it changes we can detect
    ack_packet = None
    # Weird BlockingIOError kept popping up, ignored it
    try:
        ack_packet, address = senderSocket.recvfrom(2048)
    except BlockingIOError:
        pass

    if ack_packet == None:
        continue
    # Get ACK, check if it is EOT
    packet_type, seqnum, length, data = Packet(ack_packet).decode()
    if packet_type == 2 and length == 0:
        # It is EOT package, but don't want to exit yet incase there are other ACKs we are missing
        EOT_FROM_SENDER = True
        ack_num_log.append("EOT")
    else:
        # Not EOT, continue with program
        ack_num_log.append(seqnum)
    if seqnum in unacked_packets:
        unacked_packets.pop(seqnum)
        # Only if EOT packet recieved and all unacked packets are acked, exit
    if len(unacked_packets) == 0 and EOT_FROM_SENDER:
        senderSocket.close()
        break

# Write to log files
with open("seqnum.log", 'w') as logfile:
    for item in seq_num_log:
        logfile.write(str(item)+"\n")

with open("ack.log", 'w') as logfile:
    for item in ack_num_log:
        logfile.write(str(item)+"\n")
        

