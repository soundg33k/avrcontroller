#!/usr/bin/env python

import sys, signal, threading, time, argparse
from MPDWatcher import *
from ShairportWatcher import *
from Queue import Queue
from datetime import datetime
from YamahaReceiver import YamahaReceiver

raspberryIP = "localhost"
yamahaMinVol = -30.0 #should be a argument
yamahaMaxVol = 0.0

def main(argv):
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("yamahaIP", help="address of the yamaha receiver")
	args = parser.parse_args()

	# Init
	retryTime = 5 # could be command line arg
	ip = raspberryIP
        q = Queue()
        p_m = MpdWatcherRef(None)
        CreateNewMPDWatcher(q,ip,p_m)
	p_s = ShairportWatcherRef(None)
        CreateNewShairportWatcher(q,p_s)

	receiver = YamahaReceiver(args.yamahaIP, yamahaMinVol, yamahaMaxVol)

        try:
                while True:
                        item = q.get(True, None)
                        print(str(item))
			#MPD
                        if(isinstance(item, MPDFailureInfo)):
                                Timer(retryTime, lambda : CreateNewMPDWatcher(q,ip,p_m)).start()
			elif(isinstance(item, MPDVolumeInfo)):
				receiver.SetVolumeMPD(int(item.volume))
			elif(isinstance(item, MPDStateInfo)):
				receiver.SetPowerMPD(item.playing)
			#Shairport
			elif(isinstance(item, ShairportFailureInfo)):
                                Timer(retryTime, lambda : CreateNewShairportWatcher(q,p_s)).start()
			elif(isinstance(item, ShairportVolumeInfo)):
                                receiver.SetVolumeShairport(int(item.volume))
			elif(isinstance(item, ShairportStateInfo)):
                                receiver.SetPowerShairport(item.playing)
                        q.task_done()

                print("done")
        except KeyboardInterrupt:
                sys.exit(1)

	
if __name__ == "__main__":
    	main(sys.argv)
