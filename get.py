#!/usr/bin/python
import requests
import pdb
import argparse
import pdb

url = ""
dest_file_name = ""
resume_file_name = ""
xfer_len = -1
resume = False
parser = argparse.ArgumentParser( description="Simple http-get with resume for continuing aborted transfers.")
parser.add_argument( 'url', action='store', nargs=1, help='The URL to retrieve data from.' )
parser.add_argument( 'dest_file_name', action='store', nargs=1, help='The file to store data into.' )
parser.add_argument( '-d', action='store', dest='resume_file_name', nargs='?', default="NULL", help='Specify the resume data file manually. Defaults to <dest>_resume.dat' )
parser.add_argument( '-r', action='store_true', default='store_false', dest='resume', help="Specify to resume the transfer. If not given dest-file will be overwritten." )
parser.add_argument( '-t', action='store', default=10000000, dest='xfer_len', nargs='?', help="Size of chunks to transfer from the server." )
args = parser.parse_args()
url = args.url[0]
dest_file_name = args.dest_file_name[0]
if( resume_file_name == "NULL" ):
    resume_file_name = dest_file_name+"_resume.dat"
else:
    resume_file_name = args.resume_file_name[0]
xfer_len = args.xfer_len
if( args.resume == "store_true" ):
    resume = True
else:
    resume = False

# read in resume data
if( resume == True ):
    resume_file_raw = open( resume_file_name, 'r+' )
    resume_file_data = resume_file_raw.readline().split(',')
    if( len(resume_file_data) != 2 ):
        exit(1)
    start = resume_file_data[0]
    fname = resume_file_data[1]
    if( fname != dest ):
        print "File names do not match!"
        cont = input( "Continue anyway? [Y/n]" )
        if( cont.lower() == 'n' or cont.lower() == 'no' ):
            print "Aborting."
            exit(1)
##

# get headers and setup request
pdb.set_trace()
req = requests.head( url )
if( req.headers.get( 'accept-ranges' ) == 'none' ):
    print "Server does not accept partial transfers. Aborting."
    exit(1)

# explicitly set no gzip
if( resume ): # set range -> resume_data+xfer_len
    stop=start+xfer_len
    headers = {'accept-encoding':'gzip;q=0,deflate,sdch','range':'bytes='+str(start)+'-'+str(stop)}
else: # range -> 0-xfer_len
    headers = {'accept-encoding':'gzip;q=0,deflate,sdch','range':'bytes=0-'+str(xfer_len)}

##
dest_file = open( dest_file_name, 'a' )
req = requests.get( url, headers=headers )
dest_file.write( req.text )
exit( 0 )
