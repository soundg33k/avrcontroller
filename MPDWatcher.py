import mpd, sys
from Queue import Queue
from threading import Thread
from threading import Timer

class MPDVolumeInfo:
	def __init__(self, volume):
		self.volume = volume
	def __str__(self):
        	return 'MPD volume {}'.format(self.volume)

class MPDStateInfo:
        def __init__(self, playing):
                self.playing = playing
	def __str__(self):
                return 'MPD playing {}'.format(self.playing)

class MPDFailureInfo:
        def __init__(self, info):
                self.info = info
        def __str__(self):
                return 'MPD failure {}'.format(self.info)

class MPDWatcher:
        def __init__(self, queue, clientIP):
		self.queue = queue
		self.client = mpd.MPDClient(use_unicode=True)
		self.client.connect(clientIP, 6600)
		self.mpd_thread = Thread(target = self.mpd_listener)
		print('MPDWatcher create {}'.format(hex(id(self))))

	def __str__(self):
		return __repr__()

	def __del__(self):
		print('MPDWatcher destroy begin {}'.format(hex(id(self))))		
		try:	
			self.client.close()
		finally:
			print('MPDWatcher destroy end {}'.format(hex(id(self))))			

	def mpd_listener(self):
		try:	
			while True:
				eventType = self.client.idle(u'mixer', u'player')
				mpdStatus = self.client.status()
				if (eventType == [u'mixer']):
					self.queue.put(MPDVolumeInfo(mpdStatus[u'volume']))
				elif (eventType == [u'player']):
					self.queue.put(MPDStateInfo(mpdStatus[u'state'] == u'play'))
		except Exception, e:
			self.queue.put(MPDFailureInfo(repr(e)))


	def run(self):
		self.mpd_thread.start()


class MpdWatcherRef:
    def __init__(self, m):
	self.m = m

def CreateNewMPDWatcher(q, ip, m_ref):
	try:
		m_ref.m = MPDWatcher(q, ip)
    		m_ref.m.run()
	except Exception, e:
        	q.put(MPDFailureInfo(repr(e)))

def main(argv):
	# Code to test the module
	ip = 'localhost'
	q = Queue()
	p_m = MpdWatcherRef(None)
	CreateNewMPDWatcher(q,ip,p_m)

	try:
        	while True:
                	item = q.get(True, None)
                	print(str(item))
			if(isinstance(item, MPDFailureInfo)):
				Timer(5, lambda : CreateNewMPDWatcher(q,ip,p_m)).start()
                	q.task_done()

		print("done")
	except KeyboardInterrupt:
        	sys.exit(1)    


if __name__ == "__main__":
    main(sys.argv)
