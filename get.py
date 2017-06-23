#!/usr/bin/python
import requests
import pdb
import argparse
import pdb
import os.path

def write_out( u, d, r, i, j, size, a ):
    "Retrieve HTTP data with size up to start - stop bytes, starting at index start. \
    u: URL to fetch \
    d: destination file \
    r: resume data file \
    i: start index \
    j: stop index \
    size: max size of u \
    a: append mode (T or F)"
    headers = {'accept-encoding':'gzip;q=0,deflate,sdch','range':'bytes='+str(i)+'-'+str(j)}
    req = requests.get( u, headers=headers )
    if( a == True ): # resume = append
        d_file = open( d, 'a' )
    else: # no resume = overwrite
        d_file = open( d, 'w+' )
    d_file.write( req.text )
    d_file.close()
    r_file = open( r, 'w+' )
    r_file.write( str(j)+","+d )
    r_file.close()
    return

parser = argparse.ArgumentParser( description="Simple http-get with resume for continuing aborted transfers.")
parser.add_argument( 'url', action='store', nargs=1, help='The URL to retrieve data from.' )
parser.add_argument( 'dest_file_name', action='store', nargs=1, help='The file to store data into.' )
parser.add_argument( '-d', action='store', dest='resume_file_name', nargs='?', default="NULL", help='Specify the resume data file manually. Defaults to <dest>_resume.dat' )
parser.add_argument( '-r', action='store_true', default='store_false', dest='resume', help="Specify to resume the transfer. If not given dest-file will be overwritten." )
parser.add_argument( '-t', action='store', default=10000000, dest='xfer_len', nargs='?', help="Size of chunks to transfer from the server." )
parser.add_argument( '-i', action='store', dest='iter', default='NULL', nargs='?', help="Number of iterations of xfer_len bytes to perform. Default will attempt to download until EOF is reached." )
args = parser.parse_args()
url = args.url[0]
dest_file_name = args.dest_file_name[0]
if( args.resume_file_name == 'NULL' ):
    resume_file_name = dest_file_name+"_resume.dat"
else:
    resume_file_name = args.resume_file_name[0]
xfer_len = int(args.xfer_len)
if( args.resume == True ):
    resume = True
else:
    resume = False

start = 0
if( resume == True ):
    if( not os.path.isfile( resume_file_name ) ):
        print "Resume data file ("+resume_file_name+") not found. Aborting."
        exit(1)
    resume_file_raw = open( resume_file_name, 'r+' )
    resume_file_data = resume_file_raw.readline().split(',')
    if( len(resume_file_data) != 2 ):
        exit(1)
    start = int(resume_file_data[0])
    fname = resume_file_data[1]
    if( fname != dest_file_name ):
        print "File names do not match!"
        cont = input( "Continue anyway? [Y/n]" )
        if( cont.lower() == 'n' or cont.lower() == 'no' ):
            print "Aborting."
            exit(1)
    resume_file_raw.close()

req = requests.head( url )
if not( req.status_code == 200 or req.status_code == 206 ):
    print "Invalid response code from server: "+str(req.status_code)
    exit(1)
if( req.headers.get( 'accept-ranges' ) == 'none' ):
    print "Server does not accept partial transfers. Aborting."
    exit(1)
max_size = int(req.headers.get( 'content-length' ))

stop = start+xfer_len
if( stop > max_size ):
    stop = max_size
if( os.path.isfile(dest_file_name) and not resume and os.path.getsize(dest_file_name) >= 0 ):
    print "WARNING! Resume (-r) NOT specified and data file exists ("+dest_file_name+")."
    cont = raw_input( "Continue anyway? NOTE: This behavior is NOT defined and will likely DESTROY data. y/N " )
    pdb.set_trace()
    if not( cont.lower != "yes" or cont.lower() != "y" ):
        print "Aborting."
        exit(1)

if( args.iter == "NULL" ):
    while( stop <= max_size ):
        write_out( url, dest_file_name, resume_file_name, start, stop, max_size, False ) 
        start,stop = stop,stop+xfer_len # increment the range
else:
    i = 0
    while( stop <= max_size and i <= int(args.iter) ):
        write_out( url, dest_file_name, resume_file_name, start, stop, max_size, True )
        start,stop = stop,stop+xfer_len
        i = i+1
exit( 0 )


