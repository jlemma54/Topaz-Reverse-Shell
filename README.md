# Topaz Reverse-Shell


A simple reverse shell for Windows written in python 2.7

## Disclaimer 

THIS IS ONLY TO BE USED FOR EDUCATIONAL PURPOSES. I DO NOT TAKE RESPONSIBILITY IF THIS PROJECT IS USED FOR MALICIOUS ACTIVITY


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
- browser_history -> Gets history from Google Chrome (Terminates chrome.exe if chrome is running)
- router_password -> Gets saved router passwords from client and sends them to host
- webcam -> Captures image from client webcam and sends to host as .jpg file
- listen -> Listens on microphone of client computer for set period of time and sends to host as a .wav file
- remove -> Remove file at given path from client computer
- cmd -> Executes command from command prompt on client computer
- tasklist -> Lists all running tasks on client computer
- kill -> Kills specified task on client computer
- shutdown -> remote shutdown of client computer
- exit -> exits program

---


## How to Use

If Python 2.7 is not installed on client computer use pyinstaller version 3.6 to convert client.py to an exe file. 

![Converting client.py to exe file](/pictures/screenshot0.png)


#### Running Server 

To run server type **python server.py**

![Running server.py](/pictures/screenshot4.png)

You will be asked whether or not you would like to port forward server onto ngrok server 

![Prompt to port forward to ngrok](/pictures/screenshot5.png)

If **n** is selected, server will begin listening for connections on local network 

![Listening on local network](/pictures/screenshot1.png)

if **y** is selected, server will be port forwarded to ngrok and pring out address and port number

![Server listening on ngrok server](/pictures/screenshot8.png)




#### Running Client

To run client type **python client.py** 

![Running client.py](/pictures/screenshot1.png)

If server is being port forwarded to ngrok type in address of ngrok server and port number as such

![Connecting client.py to ngrok server](/pictures/screenshot8.png)

Otherwise type in ip of machine on same network and 22 for the port (default port is 22 if ran locally)

![Connecting to client.py within same network](/pictures/screenshot2.png)



#### Running Client in Background 

In order to run client.py in background save as a .pyw file instead and convert to exe file. **Changing client.py to a .pyw file and converting to exe results in a loss of the 'router_password', 'cmd', 'tasklist', and 'kill' commands.**


