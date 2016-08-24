import math
import random
import time
import sys
import datetime
from Queue import Queue
from threading import Thread

messages_length_queue = Queue()
messages_arrival_queue = Queue()

available_space_in_protocol_buffer = 256 * 1024
available_space_in_transmit_buffer = 256 * 1024
number_of_packets = 0
number_of_packets_transmitted = 0
number_of_packets_received = 0
simulation_status = False
available_space_in_receive_buffer = 6000
packet_received_in_mac_module = 0
packet_sent_from_mac_module = 0
packets_received_from_receive_buffer = 0
packet_count = 0
number_of_packets_in_receive_buffer = 0
message_dropped = 0
x = 0

class Protocol_Processor(Thread):
    def __init__(self):
        Thread.__init__(self)
        #simulation_status = False
        self.busy_status = False

    def run(self):
        global number_of_packets, simulation_status
        while simulation_status:
            if not messages_arrival_queue.empty():
                message_length = messages_length_queue.get()
                arrival_time = messages_arrival_queue.get()
                print ("Message added to queue")
                self.process_message(message_length)
                print "Message length", message_length
                #print "Number of messages", number_of_messages


    def process_message(self, message_length):
        if self.is_space_available_in_protocol_buffer(message_length):
            self.add_message_to_protocol_buffer(message_length)
        if self.is_space_available_in_transmit_buffer():
            print "Adding data to transmit buffer"
            self.create_packets(message_length)


    def create_packets(self, message_length):
        global available_space_in_protocol_buffer
        while message_length > 0 and simulation_status:
            if available_space_in_transmit_buffer >= 1526:
                if message_length >= 1500:
                    message_length -= 1500
                else:
                    message_length = self.create_frame_by_appending_zeroes()
                self.add_packet_to_transmit_buffer()
        available_space_in_protocol_buffer += message_length

    def is_space_available_in_protocol_buffer(self, message_length):
        global available_space_in_protocol_buffer
        if available_space_in_protocol_buffer > message_length:
            print "Space available in protocol buffer", available_space_in_protocol_buffer
            f.write("Space available in protocol buffer" + " " + str(available_space_in_protocol_buffer) + " " + "at time" + " " + str(time.time()) + "\n")
            #f.write ("Time:" + str(time.time()) + "\n")
        else:
            global message_dropped
            message_dropped += 1
            f.write( str("Message dropped") + " " + "at time" + " " + str(time.time()) + "\n")
            f.write("Message dropped" + " " + str(message_dropped) + "\n")
        #f.write ("Time:" + str(time.time()) + "\n")
        #if available_space_in_protocol_buffer <= message_length:
         #   pass
        return available_space_in_protocol_buffer >= message_length

    def is_space_available_in_transmit_buffer(self):
        global available_space_in_transmit_buffer
        f.write("Available space in transmit buffer" + " " + str(available_space_in_transmit_buffer) + " " + "at time" + " " + str(time.time()) + "\n")
        #f.write ("Time:" + str(time.time()) + "\n")
        return available_space_in_transmit_buffer >= 1526

    def add_packet_to_transmit_buffer(self):
        print "packet added to transmit buffer"
        global available_space_in_transmit_buffer , number_of_packets
        available_space_in_transmit_buffer -= 1526
        number_of_packets += 1

    def add_message_to_protocol_buffer(self, message_length):
        global available_space_in_protocol_buffer, number_of_packets
        available_space_in_protocol_buffer -= message_length
        f.write("message added to protocol buffer" + " " + "at time" + " " + str(time.time()) + "\n")
        #f.write ("Time:" + str(time.time()) + "\n")
        print "message added to protocol buffer"
        #if available_space_in_protocol_buffer < 0 :



    def create_frame_by_appending_zeroes(self):
        return 0

    def is_busy(self):
        return self.busy_status

#class Protocol_buffer(Thread):
 #   def __init__(self):
  #      Thread.__init__(self)

class Transmitter(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global simulation_status, x
        while simulation_status:
            global available_space_in_transmit_buffer, number_of_packets, number_of_packets_transmitted, x
            #print type(number_of_packets_transmitted)
            if number_of_packets != 0 and x == 0:
                number_of_packets -= 1
                available_space_in_transmit_buffer += 1526
                number_of_packets_transmitted += 1
                time.sleep(5.92E-7)
                f.write("Number of packets transmitted" + " " + str(number_of_packets_transmitted) + " " + str(time.time()) + "\n")


class Mac_module(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global simulation_status, packet_count, packets_received_from_receive_buffer
        global packet_received_in_mac_module, available_space_in_protocol_buffer, packet_sent_from_mac_module, x
        mac = open('controller-log', 'w')
        while simulation_status:
            if x == 1:
                print "Packet received"
                mac.write("Packet received" + " " + "at time" + " " + str(time.time()) + "\n")
                x = 0
            else:
                global available_space_in_receive_buffer
                print "Packet sent"
                mac.write("Packet transmitted" + " " + "at time" + " " + str(time.time()) + "\n")
                x = 1
            time.sleep(24E-7)


class Receive_buffer(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global simulation_status, number_of_packets, available_space_in_receive_buffer, message_length, x, number_of_packets_received, number_of_packets_in_receive_buffer
        recv = open('receiverbuffer-log','w')
        while simulation_status :
            if x == 1:
                if number_of_packets_transmitted > number_of_packets_received and available_space_in_receive_buffer > 1526:
                    #print "Packet received from Mac module"

                    number_of_packets_received += 1

                    number_of_packets_in_receive_buffer += 1
                    recv.write("Number of packets received" + "at time" + " " + str(time.time()) + "\n")
                    packet_count = random.randint(1,5)
                    recv.write("Segments created" + " " + str(packet_count) + " " + "at time" + " " + str(time.time()) + "\n")
                    if number_of_packets_in_receive_buffer > packet_count:
                        number_of_packets_in_receive_buffer -= packet_count

                #print "Number of packets generated randomly", packet_count
            #print "Available space in receive buffer", available_space_in_receive_buffer


def add_message_to_queue(message_length, arrival_time):
    messages_length_queue.put(message_length)
    messages_arrival_queue.put(arrival_time)

if __name__ == "__main__":
    simulation_time = float(sys.argv[1])
    arrival_rate = int(sys.argv[2])
    arrival_time = 0
    number_of_messages = 0
    global message_length
    print "simulation time", simulation_time, "arrival rate", arrival_rate
    simulation_status = True
    protocol_processor = Protocol_Processor()
    protocol_processor.start()
    d1 = datetime.datetime.now()
    transmitter = Transmitter()
    transmitter.start()
    receive_buffer = Receive_buffer()
    receive_buffer.start()
    mac_module = Mac_module()
    mac_module.start()
    simulation_starts = time.time()
    print simulation_starts
    f = open('SM-log', 'w')


    try:
        while arrival_time < simulation_time:
            #f.write("Arrival time" + " "+ str(arrival_time) + "\n")
            message_length = int(math.ceil(-math.log(random.random()) * 32 * 1024))
            if message_length > 65536:
                message_length = 65536
            arrival_time += -math.log(random.random()) / arrival_rate
            number_of_messages += 1

            add_message_to_queue(message_length, arrival_time)
        simulation_stops = time.time()

        while simulation_stops - simulation_starts < simulation_time:
            simulation_stops = time.time()
        print "Simulation stopped"
        print simulation_stops
        #recv.write("Number of packets in receiving buffer after removing the segments" + " " + str(number_of_packets_in_receive_buffer) + " " + "at time" + " " + str(time.time()) + "\n")

        simulation_status = False
        time.sleep(1)
        f.write("Total number of messages arrived" + " " + str(number_of_messages) + "\n")
        print "Number of messages arrived", number_of_messages
        print "Number of packets transmitted", number_of_packets_transmitted
        #print "Space available in protocol buffer", available_space_in_protocol_buffer
        print "Number of packets received", number_of_packets_received
        print "messages dropped", message_dropped
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        protocol_processor.join()
        transmitter.join()
        receive_buffer.join()
        mac_module.join()
