import lcm, time, sys
from Queue import Queue
from shairport_lcm_t import shairport_lcm_t
from threading import Thread
from subprocess import call

class ShairportVolumeInfo:
	def __init__(self, volume):
		self.volume = volume
	def __str__(self):
        	return 'Shairport volume {} dB'.format(self.volume)

class ShairportStateInfo:
        def __init__(self, playing):
                self.playing = playing
	def __str__(self):
                return 'Shairport playing {}'.format(self.playing)

class ShairportFailureInfo:
        def __init__(self, info):
                self.info = info
        def __str__(self):
                return 'Shairport failure {}'.format(self.info)

class ShairportWatcher:
        def __init__(self, queue):
		self.queue = queue
		self.lc = lcm.LCM()
		self.subscription = self.lc.subscribe("DEFAULT", self.process_shairport_message)
		self.lcm_thread = Thread(target = self.lcm_listener)
		print("ShairportWatcher create")

	def __del__(self):
		self.lc.unsubscribe(self.subscription)
		print("ShairportWatcher destroy")

	def lcm_listener(self):
		try:	
			#raise Exception("Blah")
			while True:
				self.lc.handle()
		except Exception, e:
			self.queue.put(ShairportFailureInfo(repr(e)))


	def process_shairport_message(self, channel, data):
        	msg = shairport_lcm_t.decode(data)
        	#print("Received message on channel \"%s\"" % channel)
        	#print("message     = %s" % str(msg.message))
        	#print("value     = %s" % str(msg.value))
		if(msg.message == 'play'):
			#make sure that mpc is not playing
			call(["mpc", "stop"])
			self.queue.put(ShairportStateInfo(True))
		elif(msg.message == 'stop'):
			self.queue.put(ShairportStateInfo(False))
		elif(msg.message == 'volume'):
			self.queue.put(ShairportVolumeInfo(msg.value))
	
	def run(self):
		self.lcm_thread.start()

class ShairportWatcherRef:
    def __init__(self, s):
        self.s = s

def CreateNewShairportWatcher(q, s_ref):
        try:
                s_ref.s = ShairportWatcher(q)
                s_ref.s.run()
        except Exception, e:
                q.put(MPDFailureInfo(repr(e)))

def main(argv):
	# Code to test the module
        q = Queue()
        p_s = ShairportWatcherRef(None)
        CreateNewShairportWatcher(q,p_s)

        try:
                while True:
                        item = q.get(True, None)
                        print(str(item))
                        if(isinstance(item, ShairportFailureInfo)):
                                Timer(5, lambda : CreateNewShairportWatcher(q,p_s)).start()
                        q.task_done()

                print("done")
        except KeyboardInterrupt:
                sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)

