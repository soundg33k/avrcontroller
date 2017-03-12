import rxv, sys
import time #for debug

def convertVolToDB(volume, minVolume, maxVolume):
        volumeNormalized = volume/100.0
        volumeRange = maxVolume - minVolume
        #maths are a bit weird... it is get db range in increments of 0.5 dB
        return int(((volumeNormalized * volumeRange)+ minVolume)* 2.0) / 2.0;

class YamahaReceiver:
        def __init__(self, ip, min, max):
		self.receiver = None
		self.ip = ip
		self.minVolume = min
		self.maxVolume = max
		self.volumeMPD = 0
		self.volumeShairport = -100
		self.powerMPD = False	
		self.powerShairport = False
	
	def __str__(self):
		return __repr__()

	#def __del__(self):
		

	def SetVolumeMPD(self, volume):
		self.volumeMPD = volume
		self.Update()

	def SetVolumeShairport(self, volume):
		self.volumeShairport = volume
		self.Update()

	def SetPowerMPD(self, power):
		self.powerMPD = power
		self.Update()
	
	def SetPowerShairport(self, power):
                self.powerShairport = power
                self.Update()

	def Update(self):
		try:
			start = time.time()
			if(self.receiver == None):
				self.receiver = rxv.RXV("http://" + self.ip + ":80/YamahaRemoteControl/ctrl", "Yamaha Receiver", "Zone_2")
			
			bReceiverPower = (self.powerMPD and self.volumeMPD > 0) or (self.powerShairport and self.volumeShairport > -140)
			if(self.receiver.on !=  bReceiverPower):
				self.receiver.on = bReceiverPower
				if(bReceiverPower and self.receiver.input != 'AV7'):
					self.receiver.input = 'AV7'
			
			if(bReceiverPower):
				volume = 0
                        	if(self.powerShairport): 
                                	volume = self.volumeShairport
				else:
					volume = convertVolToDB(self.volumeMPD, self.minVolume, self.maxVolume)
				if(bReceiverPower and self.receiver.volume != volume):
					self.receiver.volume = volume
			end = time.time()
			print 'Update took {}'.format(end - start)
		except:
			print "Exception during Update"
			self.receiver = None

def main(argv):
	pass

if __name__ == "__main__":
    main(sys.argv)
