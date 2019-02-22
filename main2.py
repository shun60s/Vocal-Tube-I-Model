#coding:utf-8

#
# two tube model, draw waveform, considering glottal voice source and mouth radiation
#                 load noise as substitution for turblent sound source at downstream
#                 save generated waveform as a wav file

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from scipy.io.wavfile import write as wavwrite
from twotube_downmix import *
from glottal import *
from load_sourcewav import *
from HPF import *

# Check version
#  Python 3.6.4 on win32 (Windows 10)
#  numpy 1.14.0 
#  matplotlib  2.1.1
#  scipy 1.0.0


def plot_waveform(yout, label, tube):
	plt.subplot(2,1,1)
	plt.xlabel('mSec')
	plt.ylabel('level')
	plt.title('Waveform: ' + label)
	plt.plot( (np.arange(len(yout)) * 1000.0 / glo.sr) , yout)
	
	plt.subplot(2,1,2)
	plt.xlabel('mSec')
	plt.ylabel('level')
	plt.title('red: volume velocity at edge, blue: smoothing, green: noise')
	plt.plot( (np.arange(len(tube.y2tm)) * 1000.0 / glo.sr) , tube.y2tm, color='r' )
	plt.plot( (np.arange(len(tube.y2tm_lpf)) * 1000.0 / glo.sr) , tube.y2tm_lpf, color='b' )
	plt.plot( (np.arange(len(tube.y2tm_noise)) * 1000.0 / glo.sr) , tube.y2tm_noise, color='g' )
	return yout
	
def make_zero(duration, sampling_rate=48000):
	# duration unit is [msec]
	return np.zeros( int((duration / 1000.) * sampling_rate) )

def save_wav( yout, wav_path, sampling_rate=48000):
	wavwrite( wav_path, sampling_rate, ( yout * 2 ** 15).astype(np.int16))
	print ('save ', wav_path) 

if __name__ == '__main__':
	
	# Length & Area value, from problems 3.8 in "Digital Processing of Speech Signals" by L.R.Rabiner and R.W.Schafer
	#
	# /i/
	L1_i=9.0    # set list of 1st tube's length by unit is [cm]
	A1_i=8.0    # set list of 1st tube's area by unit is [cm^2]
	L2_i=6.0    # set list of 2nd tube's length by unit is [cm]
	A2_i=1.0    # set list of 2nd tube's area by unit is [cm^2]
	# /u/
	L1_u=10.0   # set list of 1st tube's length by unit is [cm]
	A1_u=7.0    # set list of 1st tube's area by unit is [cm^2]
	L2_u=7.0    # set list of 2nd tube's length by unit is [cm]
	A2_u=3.0    # set list of 2nd tube's area by unit is [cm^2]
	
	# insatnce
	glo=Class_Glottal()   # instance as glottal voice source
	snoise= Class_WavSource('i_noise_narrow.wav') # load noise as substitution for turblent sound source at downstream terminal
	hpf=Class_HPF()       # instance for mouth radiation effect
	twotube  =  Class_TwoTube_dwnmix(L1_i,L2_i,A1_i,A2_i)
	
	# (1) /i/ without noise mix: noise_mix_ratio=0.0,
	# draw
	fig = plt.figure()
	
	yg_repeat=glo.make_N_repeat(repeat_num=10) # input source of two tube model
	y2tm=twotube.process(yg_repeat, snoise.yg, noise_mix_ratio=0.0, threshold_noise_generate=0.9)
	yout=hpf.iir1(y2tm)
	
	yout_i=plot_waveform(yout, '/i/ without noise mix' , twotube)
	save_wav(yout_i, 'yout_i.wav')  # save generated waveform as a wav file
	
	y100= make_zero(100) # append 100ms silent part
	yout_i_long= np.concatenate( (y100, yout_i, y100 ))
	save_wav(yout_i_long, 'yout_i_long.wav')  # save generated waveform as a wav file
	
	fig.tight_layout()
	plt.show()
	
	# (2) /i/ with noise mix: noise_mix_ratio=0.4, threshold_noise_generate=0.9
	# draw
	fig = plt.figure()
	
	yg_repeat=glo.make_N_repeat(repeat_num=10) # input source of two tube model
	y2tm=twotube.process(yg_repeat, snoise.yg, noise_mix_ratio=0.4, threshold_noise_generate=0.9)
	yout=hpf.iir1(y2tm)
	
	yout_i=plot_waveform(yout, '/i/ with noise mix', twotube)
	save_wav(yout_i, 'yout_i_noise-mix.wav')  # save generated waveform as a wav file
	
	y100= make_zero(100) # append 100ms silent part
	yout_i_long= np.concatenate( (y100, yout_i, y100 ))
	save_wav(yout_i_long, 'yout_i_noise-mix_long.wav')  # save generated waveform as a wav file
	
	fig.tight_layout()
	plt.show()
	
	
	"""
	# (3) /u/ with noise mix: noise_mix_ratio=0.4, threshold_noise_generate=0.9
	# draw
	fig = plt.figure()
	
	twotube  =  Class_TwoTube_dwnmix(L1_u,L2_u,A1_u,A2_u) # instance for /u/
	yg_repeat=glo.make_N_repeat(repeat_num=10) # input source of two tube model
	y2tm=twotube.process(yg_repeat, snoise.yg, noise_mix_ratio=0.4, threshold_noise_generate=0.9)
	yout=hpf.iir1(y2tm)
	
	yout_i=plot_waveform(yout, '/u/ with noise mix', twotube)
	save_wav(yout_i, 'yout_u_noise-mix.wav')  # save generated waveform as a wav file
	
	y100= make_zero(100) # append 100ms silent part
	yout_i_long= np.concatenate( (y100, yout_i, y100 ))
	save_wav(yout_i_long, 'yout_u_noise-mix_long.wav')  # save generated waveform as a wav file
	
	fig.tight_layout()
	plt.show()
	"""
	
#This file uses TAB

