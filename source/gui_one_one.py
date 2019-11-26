'''
LANBAC(Lan Based Audio Chatroom)
'''


# !/usr/bin/python3
from tkinter import *
from tkinter import messagebox
import socket
import json
import random
import netifaces as ni
import threading
import _thread
import sys
import pyaudio
import wave
import time



class MyThread(threading.Thread):
	'''General class for threads so that they run in the background'''
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("Thread started")
		while True:
			pass


#globals
CHUNK = 10240
flag=0
flag_myip = False
flag_t1 = True
flag_t2 = True
#definitions

def getmyip(y) :
	'''this function returns the ip address. Takes interface number as input
	:param num: interface number
	:type values: int
	:return: ip address
	:rtype: string




	'''
	x = ni.interfaces()
	ni.ifaddresses(x[int(y)])
	ip = ni.ifaddresses(x[int(y)])[ni.AF_INET][0]['addr']
	print(ip)
	return ip



def record_audio(s) :
	'''start recording through microphone and send on socket s. Take socket variable as input
	:param socket: socket object
	:type socket: socket
	'''
	global flag_t1
	global CHUNK
	global flag
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
	c,a=s.accept()
	print("*recording started*")
	while(flag_t1) :
		if(flag == 1) :
			data = stream.read(CHUNK)
			c.send(data)
	stream.close()
	p.terminate()
	print("*done recording*")




def play_audio(s) :
	'''start playing the audio received on socket s
	:param s: socket object
	:type s: socket
	'''
	global flag_t2
	global CHUNK
	global flag
	flag = 1
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	WIDTH = 2
	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(WIDTH),channels=CHANNELS,rate=RATE,output=True,frames_per_buffer=CHUNK)
	play_list=[]
	while(flag_t2) :
		data = s.recv(CHUNK)
		play_list.append(data)
		stream.write(b''.join(play_list))
		play_list.clear()
	c.close()


#main
s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def display_ip():
	'''gui function to display the interface available and get the interface number form the textbox. Displays the ip address.
	'''
	s = text_myip.get()
	s = int(s)
	global myIP
	global s1
	global flag_myip
	if(flag_myip == False) :
		myIP = getmyip(s)
		s1.bind((myIP,9000))
		s1.listen(10)
		flag_myip = True
	msg = messagebox.showinfo( "My IP addr", myIP)
	B_connect.config(state="normal")
	B_myIP.config(state=DISABLED)
	var.set("You are now in open state.\nYour IP address : "+myIP)

#
def connect():
	'''gui function. takes ip address from the text  box. connects it to the other user'''
	global s2
	otherIP = str(text_ip.get())
	s2.connect((otherIP,9000))
	t2 = threading.Thread(target=play_audio,args=(s2,))
	t2.start()
	msg = messagebox.showinfo( "", "Connected")
	B_connect.config(state=DISABLED)
	B_start.config(state="normal")
	B_stop.config(state="normal")

def start_recording():
	'''gui function. starts background thread for recording the audio'''
	global s1
	t1 = threading.Thread(target=record_audio,args=(s1,))
	t1.start()
	msg = messagebox.showinfo( "", "started")


def stop_recording():
	'''stops recording the audio and destroys the parent gui window'''
	global flag_t1
	global flag_t2
	flag_t2 = False
	flag_t1 = False
	top.destroy()



top = Tk()
top.geometry("450x400")
var = StringVar()
label = Message(top, textvariable = var, relief = RAISED,justify=LEFT,width=500)
var.set("Available interfaces in your system\nChoose one to get ip\n" + str(ni.interfaces()) + "\nEnter in the box below")
label.place(x = 20,y = 50)

text_myip = Entry(top, bd = 5)
text_myip.place(x = 20,y = 150)
text_myip.insert(0, "")

B_myIP= Button(top, text = "My IP",bg="lightyellow", command = display_ip)
B_myIP.place(x = 260,y = 150)

text_ip = Entry(top, bd = 5)
text_ip.place(x=20,y=190)
text_ip.insert(0, "0.0.0.0")

B_connect = Button(top, text = "Connect",bg="lightyellow", command = connect, state=DISABLED)
B_connect.place(x = 260,y = 190)

B_start = Button(top, text = "Start",bg="green", command = start_recording,state=DISABLED)
B_start.place(x = 80,y = 240)

B_stop = Button(top, text = "EXIT",bg="red", command = stop_recording,state=DISABLED)
B_stop.place(x = 180,y = 240)

top.mainloop()
