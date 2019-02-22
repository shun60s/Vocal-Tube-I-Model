#coding:utf-8

#
# Two Tube Model, A python Class to procee reflection transmission of resonance tube
# This is the type that sound source yg_noise is also mixed at downstream edge when flow is bigger than a threshold
# 
# WARNING: frequecny response is not true.

import sys
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

# Check version
#  Python 3.6.4 on win32 (Windows 10)
#  scipy 1.0.0
#  numpy 1.14.0 



class Class_TwoTube_dwnmix(object):
	def __init__(self, L1, L2, A1, A2, rg0=0.95, rl0=0.9 ,sampling_rate=48000):
		# initalize Tube length and Tube area
		self.L1= L1 # set list of 1st tube's length by unit is [cm]
		self.A1= A1 # set list of 1st tube's area by unit is [cm^2]
		self.L2= L2 # set list of 2nd tube's length by unit is [cm]
		self.A2= A2 # set list of 2nd tube's area by unit is [cm^2]
		C0=35000.0  # speed of sound in air, round 35000 cm/second
		self.sr= sampling_rate
		self.tu1=self.L1 / C0   # delay time in 1st tube
		self.tu2=self.L2 / C0   # delay time in 2nd tube
		self.r1=( self.A2 - self.A1) / ( self.A2 + self.A1)  # reflection coefficient between 1st tube and 2nd tube
		self.rg0=rg0 # rg is reflection coefficient between glottis and 1st tube
		self.rl0=rl0 # reflection coefficient between 2nd tube and mouth
		
	def fone(self, xw):
		# calculate one point of frequecny response
		yi= 0.5 * ( 1.0 + self.rg0 ) * ( 1.0 + self.r1)  * ( 1.0 + self.rl0 ) * np.exp( -1.0j * ( self.tu1 + self.tu2 ) * xw) 
		yb= 1.0 + self.r1 * self.rg0 *  np.exp( -2.0j * self.tu1 * xw )  + self.r1 * self.rl0 * np.exp( -2.0j * self.tu2 * xw )  + self.rl0 * self.rg0 * np.exp( -2.0j * (self.tu1 + self.tu2) * xw )
		val= yi/yb
		return np.sqrt(val.real ** 2 + val.imag ** 2)

	def H0(self, freq_low=100, freq_high=5000, Band_num=256):
		print ('Warning: this frequency response compute is not revised yet, It is not true')
		# get Log scale frequecny response, from freq_low to freq_high, Band_num points
		amp=[]
		freq=[]
		bands= np.zeros(Band_num+1)
		fcl=freq_low * 1.0    # convert to float
		fch=freq_high * 1.0   # convert to float
		delta1=np.power(fch/fcl, 1.0 / (Band_num)) # Log Scale
		bands[0]=fcl
		#print ("i,band = 0", bands[0])
		for i in range(1, Band_num+1):
			bands[i]= bands[i-1] * delta1
			#print ("i,band =", i, bands[i]) 
		for f in bands:
			amp.append(self.fone(f * 2.0 * np.pi))
		return   np.log10(amp) * 20, bands # = amp value, freq list

	def process(self, yg , yg_noise, noise_mix_ratio=0.2, threshold_noise_generate=0.9 ,fc=300.0, btype='low', n_order=2):
		# process reflection transmission of resonance tube: yg is input, y2tm is output
		# two serial resonance tube
		#                      ---------------------
		#                      |                    |
		#   -------------------                     |
		#   |                                       |
		#   |                                       |
		#   -------------------                     |
		#                      |                    |
		#                      ---------------------
		# reflection ratio
		#   rg                 r1                   rl0
		#   ya1---(forward)--->   yb1---(forward)--->
		#   <-----(backward)--ya2  <---(backward)---yb2
		# input yg                             output y2tm
		#                                           mix yg_noise to yb2 when smoothed y2tm is bigger than a threshold
		#                                           
		M1= round( self.tu1 * self.sr ) + 1  # for precision, higher sampling_rate is better
		M2= round( self.tu2 * self.sr ) + 1  # for precision, higher sampling_rate is better
		M1= int(M1)
		M2= int(M2)
		ya1=np.zeros(M1)
		ya2=np.zeros(M1)
		yb1=np.zeros(M2)
		yb2=np.zeros(M2)
		self.y2tm=np.zeros(len(yg))
		self.y2tm_lpf=np.zeros(len(yg))
		self.y2tm_noise=np.zeros(len(yg))
		
		# check
		if len(yg_noise) < len(yg):
			print ('error: len(yg_noise) < len(yg)')
			sys.exit()
		
		# smoothing filter to smooth y2tm to detect over threshold softly
		b, a= signal.butter(n_order, (fc / (self.sr/2.0)) , btype=btype, analog=False, output='ba') # b=Numerator(bunsi), a=denominator(bunbo)
		zf= signal.lfilter(b, a, np.zeros(len(a)-1) )
		
		for tc0 in range(len(yg)):
			for i in range((M1-1),0,-1): # process one step
				ya1[i]=ya1[i-1]
				ya2[i]=ya2[i-1]
			for i in range((M2-1),0,-1): # process one step
				yb1[i]=yb1[i-1]
				yb2[i]=yb2[i-1]			
			# compute reflection
			ya1[0]= ((1. + self.rg0 ) / 2.) * yg[tc0] + self.rg0 * ya2[-1]
			ya2[0]= -1. * self.r1 *  ya1[-1]  +  ( 1. - self.r1 ) * yb2[-1]
			yb1[0]= ( 1 + self.r1 ) * ya1[-1] + self.r1 * yb2[-1]
			self.y2tm[tc0]= (1 + self.rl0) * yb1[-1]
			
			# smooth y2tm
			y, zf = signal.lfilter(b, a, [self.y2tm[tc0]], zi=zf)
			self.y2tm_lpf[tc0]=y[0]
			# mix noise when smoothing y2tm (flow) is bigger than threshold_noise_generate
			if np.abs(self.y2tm_lpf[tc0]) >  threshold_noise_generate:
				self.y2tm_noise[tc0]= yg_noise[tc0] * noise_mix_ratio
			else:
				self.y2tm_noise[tc0]=0.0
			
			yb2[0]=  -1. * self.rl0  * yb1[-1] +  self.y2tm_noise[tc0]


		return self.y2tm

if __name__ == '__main__':
	
	# Length & Area value, from problems 3.8 in "Digital Processing of Speech Signals" by L.R.Rabiner and R.W.Schafer
	#
	# /i/
	L1_i=9.0    # set list of 1st tube's length by unit is [cm]
	A1_i=8.0    # set list of 1st tube's area by unit is [cm^2]
	L2_i=6.0    # set list of 2nd tube's length by unit is [cm]
	A2_i=1.0    # set list of 2nd tube's area by unit is [cm^2]

	
	# insatnce
	twotube_i  =  Class_TwoTube_dwnmix(L1_i,L2_i,A1_i,A2_i)
	
	
#This file uses TAB

