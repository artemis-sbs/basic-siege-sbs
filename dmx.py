
# start of my python script program file
import sbs
import time
import math
import random
import script

dmxBlinkState = 0

########################################################################################################
def blink_dmx(clientID):
	global dmxBlinkState
	sbs.set_dmx_channel(clientID, 0, dmxBlinkState,   0,    0, 255);
#	sbs.set_dmx_channel(clientID, 1, dmxBlinkState,   0,    0, 255);
#	sbs.set_dmx_channel(clientID, 2, dmxBlinkState,   0,    0, 255);

	dmxBlinkState = dmxBlinkState+1
	if dmxBlinkState > 1:
		dmxBlinkState = 0

########################################################################################################
def HandleDMX(sim):

	blink_dmx(0)


# end of my python script program file


