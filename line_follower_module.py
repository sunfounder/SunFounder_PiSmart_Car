import smbus

class Line_Follower(object):
	def __init__(self, address=0x11):
		self.bus = smbus.SMBus(1)
		self.address = address

	def read_raw(self):
		for i in range(0, 5):
			try:
				raw_result = self.bus.read_i2c_block_data(self.address, 0, 10)
				Connection_OK = True
				break
			except:
				Connection_OK = False
				print "Error accessing %2X, Try again." % self.address

		if Connection_OK:
			return raw_result
		else:
			return False
			#print "Error accessing %2X" % self.address

	def read(self):
		raw_result = self.read_raw()
		if raw_result:
			result = [0, 0, 0, 0, 0]
			for i in range(0, 5):
				high_byte = raw_result[i*2] << 8
				low_byte = raw_result[i*2+1]
				result[i] = high_byte + low_byte
			return result

if __name__ == '__main__':
	lf = Line_Follower()
	while True:
		print lf.read()
