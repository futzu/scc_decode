#!/usr/bin/env python3

import sys

blank=''

# I drop these codes ....for now?
drops=('9170','94ae','94ad','9420', '942c','9425','9426','97a1')

'''
Lookup tables for character and scc code conversion
I roll it out to make encoding or decoding values easy,
'''
specials={'chars': ('®','°', '½',  '¿', '™', '¢',  '£',  '♪', 'à', ' ', 'è', 'â', 'ê', 'î', 'ô', 'û', ),
	'codes':('91b0','9131','9132','91b3','9134','91b5','91b6','9137','9138','91b9','91ba','913b','91bc',
	'913d','913e','91bf',) }

extended={ 'chars': ('Û', 'Å', '“', 'Õ', 'Ï', '‘', '~', '└', '_', 'ã', 'Ç', 'å', 'Ù', 'ø', '^', 'ï', '—', '”',
		'Í', '}', '{', 'Ô','Â', '¤', '*', 'Ë', '¡', 'ù', '┘', '¥', 'Ì', 'ü', 'Ú', 'Ø', 'ë', 'õ',
		'À', 'Ó', 'Á', 'Ê','ò', 'ß', 'Ã', 'ä', '¦','┐', '•', 'ì','ö', '«', 'È', '»', '┌', '’',
		'|', '℠', '\\', '©', 'Ò', 'É', 'Î', 'Ü', 'Ö', 'Ä',) ,
	'codes': ('923d', '1338', '92ae', '13a7', '9238', '9226', '132f', '133e', '13ad', '13a1', '9232', '13b9',
		'923b', '133b', '132c', '92b9', '922a', '922f', '13a2', '132a', '1329', '92ba', '9231', '13b6', '92a8',
		'92b5', '92a7', '92bc','13bf', '13b5', '1323', '9225', '9223', '13ba', '92b6', '13a8', '92b0', '92a2',
		'9220', '9234', '1326', '1334','1320', '1331', '13ae', '133d', '92ad', '13a4', '13b3', '923e', '92b3',
		'92bf', '13bc', '9229', '1337', '922c','13ab', '92ab', '1325', '92a1', '9237', '92a4', '1332', '13b0',) }

###### utility ####
def pad(num,depth=2):
	if num < 10:
		return "%s%i"%("0"*(depth -1),num)
	return "%i"%num	
	
def write_out_file(out_name,output,seqnum):
	with open(out_name,'w+') as out_file:
		out_file.write('\n'.join(output))
		print('\n\t\t\t\t %(seqnum)s captions written to %(out_name)s \n' %{'seqnum':seqnum,'out_name':out_name})


def bump_time(ms,bump=0):
	'''
	ms is the  display time line offet from the start of  video in milliseonds
	bump is the subtitle adjustment in seconds
	'''

	ms +=(bump*1000)
	return ms


def hours(ms):
	secs=int(ms/1000)
	return int(secs/3600)

def minutes(ms):
	secs=int(ms/1000)
	return	int((secs % 3600)/60)


def seconds(ms):
	return int((ms/1000) % 60)

def milliseconds(ms):
	return int(ms % 1000)


##### SCC #########


def char2scc(achar):
	return hex(ord(achar))[2:]

def scc2char(hexed):
    if hexed == '80':
        return '\n'
    s='0x'+hexed
    i=int(s,16)
    if hexed[0] in ['a','b','c','d','e','f']:
        i= i ^ 0x80
    print(hexed," -> ",chr(i))
    return chr(i)



def scc2ms(line_time):
	'''
	00:00:01:24	to milliseconds
	'''
	h = int(line_time[0:2])
	m = int(line_time[3:5])
	s = int(line_time[6:8])
	ms = int(line_time[9:11])
	as_milliseconds=((h*3600)+(m*60)+s)*1000+ms
	return as_milliseconds


def ms2scc(msecs):
	'''
	milliseconds to 00:00:01:24
	'''
	h = hours(ms)
	m = minutes(ms)
	s = seconds(ms)
	hs = int(msecs % 10000)
	return '%(h)s:%(m)s:%(s)s:%(ms)s' %{'h':pad(m),'m':pad(m),'s':pad(s),'hs':pad(hs)}


'''
drop the chunk if it's in drops
'''
def clear_drops(chunk):
	if chunk in drops:
		chunk= blank
	return chunk


def scc_chunk2char(chunk):
	'''
	take an scc chunk like '92ad'
	and see if it is listed in
	the specials or extended codes tuples
	return decoded value from a chars tuple
	'''
	decoded=blank
	for datamap in [specials, extended]:
		if chunk in datamap['codes']:
			idx=datamap['codes'].index(chunk)
			decoded=datamap['chars'][idx]

	return decoded


def scc_chunk2twochars(chunk):
	'''
	decode scc into chaars
	'''
	decoded=blank
	chunk=chunk.lower()
	if chunk.startswith('9') or chunk.startswith('1'):
		decoded=scc_chunk2char(chunk)
	else:
		one,two=chunk[:2],chunk[2:]
		try:
			decoded=scc2char(one)
			decoded +=scc2char(two)
		except:
			pass
	return decoded


def scc_dechunk(chunked):
	'''
	split captions into chunks,
	and decode everything
	'''
	buffed=[]
	chunks=chunked.split(' ')
	for chunk in chunks:
		chunk=clear_drops(chunk)
		if chunk is not blank:
			decoded=scc_chunk2twochars(chunk)
			buffed.append(decoded)
	return  buffed


def scc_split(scc_file):
	'''
	times and captions are separated by a tab,
	'''
	scc_input=scc_file.readlines()
	scc_times=[]
	scc_caps=[]
	for line in scc_input:
		if '\t' in line:
			sl=line.split('\t')
			dechunked=scc_dechunk(sl[1])
			if len(dechunked) > 1:
				scc_times.append(sl[0])
				scc_caps.append(dechunked)
	return scc_times,scc_caps


def scc_decoder(scc_file):
	scc_times,scc_caps=scc_split(scc_file)
	captions=[]
	seqnum=0
	for i in range (len(scc_caps)):
		seqnum +=1
		start=scc2ms(scc_times[i])
		try:
			stop=scc2ms(scc_times[i+1])
		except:
			stop=0
		text=''.join(scc_caps[i])
		caption={'seqnum':seqnum,
			'start':start,
			'stop':stop,
			'text' :text}
		captions.append(caption)
	return captions

#### VTT
def vtt_minutes(ms):
	secs=int(ms/1000)
	return int(secs/60)

def vtt2ms(line_time):
	'''
	00:01.000  to milliseconds
	'''
	m = int(line_time[0:2])
	s = int(line_time[3:5])
	ms = int(line_time[9:12])
	as_milliseconds=((m*60)+s)*1000+ms
	return as_milliseconds

def ms2vtt(msecs):
	'''
	milliseconds to 00:00:01,068
	'''
	m = vtt_minutes(msecs)
	s = seconds(msecs)
	ms = milliseconds(msecs)
	return '%(m)s:%(s)s,%(ms)s' %{'m':pad(m),'s':pad(s),'ms':pad(ms,3)}


def cap_as_vtt(cap):
	start=ms2vtt(cap['start'])
	stop=ms2vtt(cap['stop'])
	text=cap['text']
	vtt_data = ['%(start)s --> %(stop)s ' %{ 'start':start, 'stop': stop},
		'%(text)s \n\n' %{'text':text}]
	return '\n'.join(vtt_data)

def vtt_header():
	header= 'WEBVTT\n\n'
	return header

def to_vtt(captions):
	'''
	WEBVTT

	00:01.000 --> 00:04.000
	LET'S GET MORE NOW FROM CNN'S
	'''
	output=[]
	output.append(vtt_header())
	[output.append(cap_as_vtt(c)) for c in captions]
	return ''.join(output)


#########  SRT #######################


def srt2ms(line_time):
	'''
	00:00:01,068  to milliseconds
	'''
	h = int(line_time[0:2])
	m = int(line_time[3:5])
	s = int(line_time[6:8])
	ms = int(line_time[9:12])
	as_milliseconds=((h*3600)+(m*60)+s)*1000+ms
	return as_milliseconds


def ms2srt(msecs):
	'''
	milliseconds to 00:00:01,068
	'''
	h = hours(msecs)
	m = minutes(msecs)
	s = seconds(msecs)
	ms = milliseconds(msecs)
	return '%(h)s:%(m)s:%(s)s,%(ms)s' %{'h':pad(m),'m':pad(m),'s':pad(s),'ms':pad(ms,3)}



def cap_as_srt(cap):
	seqnum=cap['seqnum']
	start=ms2srt(cap['start'])
	stop=ms2srt(cap['stop'])
	text=cap['text']
	srt_data = ['%(sq)i ' %{'sq':seqnum},
		'%(start)s --> %(stop)s ' %{ 'start':start, 'stop': stop},
		'%(text)s \n\n' %{'text':text}]
	return '\n'.join(srt_data)


def to_srt(captions):
	output=[]
	[output.append(cap_as_srt(c)) for c in captions]
	return ''.join(output)


def help():
	print("\n\t\tusage: \n \t\t\tsubtle sccfile outfilename.vtt\n")
	

if __name__=='__main__':
	pmap={'srt':to_srt,
		'vtt': to_vtt}
	if len(sys.argv) >2:
		with open(sys.argv[1]) as scc_file:
			captions=scc_decoder(scc_file)
			fname=sys.argv[2]
			with open(fname,'w+') as outfile:
				if fname.endswith('vtt'): outfile.write(to_vtt(captions))
				else: outfile.write(to_srt(captions))
	else:	

		help()
		sys.exit()