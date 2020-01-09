#! /usr/bin/python

#######################################################################
# Produce IWG1 packets from a netCDF file. If variable is missing from
# netCDF file, maintain blank entries to keep IWG1 structure.
#
# Copyright University Corporation for Atmospheric Research, 2020 
#######################################################################

import netCDF4
import pandas as pd
from datetime import datetime
import sys
import threading
import socket
import argparse
import time

# get arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", help="netCDF file to convert", required=True)
parser.add_argument("-o", "--output_file", help="Optional IWG1 format converted output file")
parser.add_argument("-s", "--interval", help="Optional conversion interval seconds")
parser.add_argument("-u", "--UDP", type=bool, const=True, nargs="?", default=False, help="UDP broadcasting, set to True")
parser.add_argument("-v", "--extravars", help="file containing comma separated list of vars")
parser.add_argument("-er", "--emulate_realtime", type=bool, const=True, nargs="?", default=False, help="Emulate realtime mode, set to True") 
args = parser.parse_args()

if args.output_file is not None and args.UDP == True:
    sys.exit("Output file option set and UDP set to True. Only one can be set.")
elif args.output_file is not None and args.interval is not None:
    print("Output file and conversion interval arguments provided. Igoring conversion interval.")
elif args.UDP == False and args.emulate_realtime == True:
    sys.exit("You have UDP output set to False and emulate realtime set to True.")
else:
    pass
# default interval to 1 second but use argument if provided
input_file = args.input_file
if args.interval is not None:
    interval = args.interval
else:
    interval = 1

# configure UDP broadcast if argument is provided
if args.UDP == True:
    UDP_OUT = True
    UDP_PORT = 7071
    hostname = socket.gethostname()
    UDP_IP = socket.gethostbyname(hostname)
else:
    UDP_OUT = False

# read the input file to convert
nc = netCDF4.Dataset(input_file, mode='r')
iwg1_vars_list = ["GGLAT", "GGLON", "GGALT", "NAVAIL", "PALTF", \
                  "HGM232", "GSF", "TASX", "IAS", "MACH_A", "VSPD", \
                  "THDG", "TKAT", "DRFTA", "PITCH", "ROLL", "SSLIP", \
                  "ATTACK", "ATX", "DPXC", "TTX", "PSXC", "QCXC", \
                  "PCAB", "WSC", "WDC", "WIC", "SOLZE", "Solar_El_AC", \
		  "SOLAZ", "Sun_Az_AC"]

#######################################################################
# define function to extract vars from the netCDF file
#######################################################################
def extractVar(element, input_file):
    if element in input_file.keys():
        output = input_file[element][:]
        return output
    else:
        pass

#######################################################################
# define function to convert data to IWG1 format
#######################################################################
def buildIWG():
    # extract the time variable from the netCDF file
    TIME = nc.variables["Time"]
    dtime = netCDF4.num2date(TIME[:],TIME.units)
    dtime = pd.Series(dtime).astype(str)
    dtime = dtime.str.replace(":", "")
    dtime = dtime.str.replace("-", "")
    dtime = dtime.str.replace(" ", "T")

    df = {}
    for i in iwg1_vars_list:
        try:
            output = extractVar(i, nc.variables)
            df[i] = pd.DataFrame(output)
        except:
            print("Error in extracting variable "+i+" in "+input_file)

    global iwg
    iwg = pd.concat([df["GGLAT"], df["GGLON"], df["GGALT"], df["NAVAIL"], df["PALTF"], \
           df["HGM232"], df["GSF"], df["TASX"], df["IAS"], df["MACH_A"], \
           df["VSPD"], df["THDG"], df["TKAT"], df["DRFTA"], df["PITCH"], \
           df["ROLL"], df["SSLIP"], df["ATTACK"], df["ATX"], df["DPXC"], \
           df["TTX"], df["PSXC"], df["QCXC"], df["PCAB"], df["WSC"], \
           df["WDC"], df["WIC"], df["SOLZE"], df["Solar_El_AC"], df["SOLAZ"], \
           df["Sun_Az_AC"]], axis=1, ignore_index=False)

    iwg = pd.concat([dtime, iwg], axis=1, ignore_index=False)
    iwg.insert(loc=0, column='IWG1', value='IWG1')

    if args.extravars is not None:
        with open(args.extravars) as file:
            print file
            for line in file:
                additional_vars_list = line.split()
                print(additional_vars_list)
        extravars = {}
        for i in additional_vars_list:
            try:
                extra_output = extractVar(i, nc.variables)
                extravars[i] = pd.DataFrame(extra_output)
            except:
                print("Additional variables expected, but error in extraction.")
        extravars=pd.concat(extravars, axis=1, ignore_index=False)
        iwg = pd.concat([iwg, extravars], axis=1, ignore_index=False)

    else:
        pass

    iwg = iwg.fillna('')
    iwg = iwg.astype(str)
    return iwg

#######################################################################
# define UDP broadcast function
######################################################################
def broadcastUDP(output, count):
    if UDP_OUT == True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        with open(output, "r") as udp_packet:
            MESSAGE = str(udp_packet.readlines()[count])
            message = MESSAGE.translate(None, "[]'")
            message = message.rstrip()
            print(message)
            sock.sendto(message, ('', UDP_PORT))
    else:
        pass

######################################################################
# define main function
#######################################################################
def main():
    if args.output_file is not None:
        buildIWG()        
        iwg.to_csv(args.output_file, header=False, index=False)
    elif args.UDP == True:
        if args.emulate_realtime == False:
            threading.Timer(float(interval), main).start()
            buildIWG()
            iwg.to_csv("output.txt", header=False, index=False)
            broadcastUDP("output.txt", -1)
        elif args.emulate_realtime == True:
            buildIWG()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            iwg.to_csv("output.txt", header=False, index=False)
            with open("output.txt", "r") as udp_packet:
                lines = udp_packet.readlines()
                while len(lines) != 0:
                    MESSAGE = str(lines[0])
                    message = MESSAGE.translate(None, "[]'")
                    message = message.rstrip()
                    print(message)
                    sock.sendto(message, ('', UDP_PORT))
                    lines.remove(lines[0])
                    time.sleep(float(interval))
    else:
        threading.Timer(float(interval), main).start()
        buildIWG()
        iwg.to_csv("output.txt", header=False, index=False)
        with open("output.txt", "r") as stdout:
            stdout = str(stdout.readlines()[-1])
            stdout = stdout.translate(None, "[]'")
            stdout = stdout.rstrip()
            print(stdout)
#######################################################################
# main
#######################################################################
if __name__=="__main__":
    main()
