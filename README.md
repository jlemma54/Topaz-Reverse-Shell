# Topaz Reverse-Shell

A simple reverse shell for Windows written in python

## Disclaimer 

THIS IS ONLY TO BE USED FOR EDUCATIONAL PURPOSES. I DO NOT TAKE RESPONSIBILITY IF THIS PROJECT IS USED FOR MALICIOUS ACTIVITY

## Requirements

- python=2.7
- packages: 
  - pycryptodomex=3.97
  - pyngrok=4.12
  - opencv-python=4.2.0.32
  - pyaudio=0.2.11
  - pyautogui=0.9.50
  - pynput=1.68
  - pywin32=228
    - win32clipboard
    - wmi
    - win32crypt

---

## Description
The Topaz Reverse Shell is a basic remote shell program for Windows written in python used to execute its built in commands on a client computer. Topaz does this over a TCP connection and has the ability to be used on different networks by port forwarding the server onto an ngrok server using pyngrok. Pyngrok is a python wrapper for ngrok, making it possible to port forward within python itself. Topaz utilizes both RSA and AES 256 encryption algorithims to securely send commands, messages, and files between both the server and client computers.

---

## Feautres
- view_cwd -> Views current directory 
- custom_dir -> Lists all files in selected directory 
- download_file -> Downloads file from client computer to host computer
- send_file -> Sends file from host computer to client computer
- system_info -> Displays system information such as OS name, OS version, CPU, RAM, Graphics Card, Private IP, and Public IP
- screenshot -> Takes screenshot on client computer and sends to host as a .png file
- copy_clipboard -> Copies clipboard of client computer and sends to host computer
- key_logger -> Listens to keyboard of client computer for set period of time and sends keystrokes with time as .txt file
- browser_password -> Gets saved passwords from Google Chrome and sends them to host
- router_password -> Gets saved router passwords from client and sends them to host
- webcam -> Captures image from client webcam and sends to host as .jpg file
- listen -> Listens on microphone of client computer for set period of time and sends to host as a .wav file
- remove -> Remove file at given path from client computer
- shutdown -> remote shutdown of client computer
- exit -> exits program

---


## How to Use

If Python 2.7 is not installed on client computer use pyinstaller version 3.6 to convert client.py to an exe file. 

![Converting client.py to exe file](/pictures/screenshot0.png)


#### Running Client

To run client in background type **python client.py** 

![Running client.py](/pictures/screenshot1.png)

If server is being port forwarded to ngrok type in address of ngrok server and port number as such

![Connecting client.py to ngrok server](/pictures/screenshot8.png)

Otherwise type in ip of machine on same network and 22 for the port (default port is 22 if ran locally)

![Connecting to client.py within same network](/pictures/screenshot2.png)



#### Running Client in Background 

In order to run client.py in background save as a .pyw file instead and convert to exe file. **Changing client.py to a .pyw file and converting to exe results in a loss of the 'router_password' command.**


