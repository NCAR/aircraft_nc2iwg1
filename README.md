# nc2iwg1
## Python port of aircraft_nc_utils

Original script was written in C++.

The script can take up to six arguments. 

The first (-i) is the input netCDF file containing the variables that you wish to extract and either write to standard out, broadcast via UDP, or write to the IWG1 file. This is a required argument.

The second (-o) is an output file in the iwg1 file format. This is optional. If no argument is provided, the script continues to run without a user defined output file.

The third (-s) is the frequency at which the user would like the conversion to take place. This should be an integer representing the number of seconds. This is optional and if not provided, the program will execute the conversion at 1 second intervals.

The fourth (-u) is optional and should be set to True if you would like the data to be broadcast via UDP. If not provided, then the script will not broadcast vi UDP.

The fifth (-v) is optional and allows users to select additional variables beyond the standard IWG1 list. These variables should be included in a text file in a single row delimited by a single space. See example below:

The sixth (-re) is optional and allows users to have a realtime emulator for complete netCDF files after a given flight is complete. This is intended to be used for testing purposes to mimic the functionality of the script while a flight is in progress. 

## Argument Format:
./nc2iwg1.py -i <input_file> -o <output_file>

./nc2iwg1.py -i <input_file> 

./nc2iwg1.py -i <input_file> -s <interval> -u <True>

./nc2iwg1.py -i <input_file> -o <output_file> -v <extra_variables.txt>

./nc2iwg1.py -i <input_file> -s <interval> -u <True> -re <True>

## Practical Examples:
### UDP Brodcast
./nc2iwg1.py -i MethaneAIRrf01.nc -s 5 -u True
IWG1,20191108T194046,39.9128646851,-105.118080139,1718.63244629,5380.68554688,4.53537416458,0.0279335938394,-0.0110997995362,37.0053863525,,,-1.74751281738,0.335055530071,,,22.7556190491,,831.13079834,0.10000000149,831.234436035,,,,58.0850868225,-16.0002632141\n
IWG1,20191108T194046,39.9128646851,-105.118080139,1718.63244629,5380.68554688,4.53537416458,0.0279335938394,-0.0110997995362,37.0053863525,,,-1.74751281738,0.335055530071,,,22.7556190491,,831.13079834,0.10000000149,831.234436035,,,,58.0850868225,-16.0002632141\n

### Format of text file with extra variables to include in the IWG1 packet
Contents of extra_variables.txt:
AT_A ATH1 ATH2 

### Note: there are no restrictions on the number of additional variables or the name of the extra variables text file


## Installation Requirements
### MacOS
download zip: https://github.com/NCAR/aircraft_nc2iwg1
pip install pandas
pip install netCDF4

### Linux
download zip: https://github.com/NCAR/aircraft_nc2iwg1
yum install pandas-python
yum install netCDF4-python

### Windows
(not sure yet)
