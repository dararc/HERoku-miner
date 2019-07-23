import optparse
import sys
import socket
import threading
import subprocess

def execute_command( command ):
    output = subprocess.check_output( command, shell=True )
    return output

def server_handler( _clsocket ):
    data, datalength = _clsocket.recv( 4096 ), 1   # Bytes to Receive at a time.
    while datalength:
        toadd = _clsocket.recv( 4096 )
        datalength = len( toadd )
        data += toadd
        if datalength < 4096:
            break
    output = execute_command( data.rstrip( ) )
    _clsocket.send( output )

def listen_to_client( tgt, port ):
    tgt = '0.0.0.0' if not tgt else tgt   # Listen to All interface in case of no target.
    print ("[>] Listening on %s:%d") % (tgt, port)
    server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    server.bind( ( tgt, port ) )
    server.listen( 5 )

    while True:
        (cl_socket, cl_address) = server.accept()  # cl denotes to the word "Cllient"
        print "[<] Received Connection From %s" % ( cl_address[0] )
        t = threading.Thread( target=server_handler, args=( cl_socket, ) )
        t.daemon = True
        t.start()

def connect_to_server( tgt, port, command ):
    sclient = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sclient.connect(( tgt, port ))
    command = "uname" if not command else command
    
    sclient.send( command )
    data, datalength = sclient.recv( 4096 ), 1
    while datalength:
       toadd = sclient.recv( 4096 )
       datalength = len( toadd )
       data += toadd
       if datalength < 4096:
           break
    print data

def main( ):
    parser = optparse.OptionParser()
    parser.add_option( '-l', '--listen', dest='listen', default=False, action="store_true", help="Listen on the specified port!" )
    parser.add_option( '-p', '--port', dest='port', default=3222, type="int", help="Port to Listen on or connect to!" )
    parser.add_option( '-t', '--target', dest='target', default=None, type="string", help="Taregt hostname or ip address to connect" )
    parser.add_option( '-e', '--execute', dest='execute', default=False, type="string", help="Command to execute on target window" )
    (options, args) = parser.parse_args()

    if options.listen and options.port:
        listen_to_client( options.target, options.port )   # Will be our function to setup a remote server
    elif options.target and options.output and options.execute:
        connect_to_server( options.target, options.port, options.execute )
    else:
        sys.exit( "[~] Error! Not All Required arguments are supplied!" )
