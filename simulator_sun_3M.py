#simulator considering the use of the three modulations at a given time
import random
import numpy
import sys

number_of_retries = int(sys.argv[1])
window_size = int(sys.argv[2])
w_prob = 20 #int(sys.argv[3])


modulations = {1:"FSK", 2:"OQPSK", 3:"OFDM"}
current_mod = [1,2,3]
lqe_mod = [0,0,0]
prob_mod = [0.34,0.33,0.33]
num_of_mod = 1
packet_counter = 0
retry = 0

tx_counter = [0,0,0,0]
ack_counter = [0,0,0,0]
prr_th = 0.9

rx_counter = 0
retry_counter = 0
prev_packet = -1

cont_window = 0

cont_trial = 0
acc_trial = 0

verbose = False

try:
    random.seed()
    current_config = 0
    previous_mod = -1
    while (True):
        #the the PDR to transmit the next packet
        if(retry == 0):
            if(cont_window == 0):
                ent = input().split('\t')
                cont_window = int(ent[1])
                if(cont_window > 75):
                    continue
                pdr_fsk = float(ent[2])
                pdr_oqpsk = float(ent[3])
                pdr_ofdm = float(ent[4])
                if(verbose):
                    print(pdr_fsk)
                    print(pdr_oqpsk)
                    print(pdr_ofdm)
            cont_window -= 1
            
        #calculating a new estimation for one of the modulations
        if(tx_counter[previous_mod] == window_size):
            arr = (ack_counter[inst_mod]/tx_counter[inst_mod])
            lqe_mod[inst_mod-1] = arr
            tx_counter[inst_mod] = 0
            ack_counter[inst_mod] = 0
            if(verbose):
                print("ARR of {} = {}: ".format(modulations[inst_mod],arr))
         
          # w_prob = 5
          # for i in range(3):
          #     prob_mod[i] = (1+(w_prob*lqe_mod[i]))/(3+(w_prob*sum(lqe_mod)))
          #     if(verbose):
          #         print(prob_mod[i])
          
            sum_p = 0
            for i in range(3):
                sum_p += (1+lqe_mod[i])**w_prob
            for i in range(3):
                prob_mod[i] = ((1+lqe_mod[i])**w_prob)/(sum_p)
                if(verbose):
                    print(prob_mod[i])
                   
        #pick the modulation to be used
        inst_mod = 1#numpy.random.choice(current_mod, size=None, replace=True, p=prob_mod)
        trial = random.random()
        if(trial <= prob_mod[0]):
            inst_mod = 1
        elif(trial <= (prob_mod[0]+prob_mod[1])):
            inst_mod = 2
        else:
            inst_mod = 3
        if(verbose):
            print("Modulation to be used: ",inst_mod)
            
       # if(lqe_mod[inst_mod-1] < prr_th and (retry > 0 and inst_mod == previous_mod)):   
        if((retry > 0 and inst_mod == previous_mod)):                      
            #w_prob = int(sys.argv[3])
            if(inst_mod == 1):
                mod_1 = 2
                mod_2 = 3
            elif(inst_mod == 2):
                mod_1 = 1
                mod_2 = 3
            else:
                mod_1 = 1
                mod_2 = 2
            prob_ret = [0,0]
            
           # k = 0
           # for i in range(1,4):
           #    if(i == inst_mod):
           #        continue
           #    prob_ret[k] = (1+(w_prob*lqe_mod[i-1]))/(2+(w_prob*(lqe_mod[mod_1-1] + lqe_mod[mod_2-1])))
           #    k+=1
            
            prob_ret = [0,0]  
            #w_prob = int(sys.argv[3])
            sum_p = 0
            for i in range(1,4):
                if(i == inst_mod):
                    continue
                sum_p += (1+lqe_mod[i-1])**w_prob
            k = 0
            for i in range(1,4):
                if(i == inst_mod):
                    continue
                prob_ret[k] = ((1+lqe_mod[i-1])**w_prob)/(sum_p)
                k+=1
                
            
            trial = random.random()
            if(trial <= prob_ret[0]):
                inst_mod = mod_1
            else:
                inst_mod = mod_2

            if(verbose):
                print("Different modulation for retransmission",inst_mod)
        previous_mod = inst_mod
        
        trial  = random.random()

        if(verbose):
            print("Transmitting packet {} retry {} modulation {}".format(packet_counter, retry, modulations[inst_mod]))
        retry_counter += 1
        tx_counter[inst_mod] += 1
        pdr_phy = float(ent[inst_mod+1])

        #packet delivered
        if(trial <= pdr_phy):
            if(verbose):
                print("Receiving packet {} retry {}".format(packet_counter, retry))
            if(packet_counter != prev_packet):
                rx_counter += 1
            prev_packet = packet_counter
            
            #sending ACK
            trial = random.random()

            if(trial <= pdr_phy):
                if(verbose):
                    print("Receiving ACK {} retry {}".format(packet_counter, retry))
                ack_counter[inst_mod] += 1
                packet_counter += 1
                retry = 0
            else:
                if(verbose):
                    print("ACK not received {} retry {}".format(packet_counter, retry))   
                #transmit again?
                if(retry < number_of_retries):
                    retry += 1
                else:
                    packet_counter += 1
                    retry = 0

        #transmission failed
        else:
            #transmit again?
            if(retry < number_of_retries):
                retry += 1
            else:
                packet_counter += 1
                retry = 0
        
except EOFError as e:
    print("{},{}".format(rx_counter/packet_counter,retry_counter/packet_counter))
