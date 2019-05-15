from tkinter import *
from tkinter import messagebox
import yaml
import keyring
import os
import threading
import paramiko
import time
import pyperclip

class Rememberator:
        
    def save_credentials(self):
        self.creds = {
            'uname' : unameEntry.get(),
            'port' : portEntry.get()
            }
        
        self.pwd = pwdEntry.get()
        keyring.set_password('SSH', unameEntry.get(), self.pwd)
        
        conf_file = open('config.yml', 'w+')
        yaml.dump(self.creds, conf_file)
        
        
    def check_if_file_exists(self):
        self.check = os.path.isfile('./config.yml')
        return self.check
        
    def insert_credentials(self):
        if self.check_if_file_exists():
            try:
                with open('config.yml', 'r') as stream:
                    creds = yaml.load(stream)
                unameEntry.insert(0, creds['uname'])
                portEntry.insert(0, creds['port'])
                pwdEntry.insert(0, keyring.get_password('SSH', creds['uname']))
            except:
                pass

class Connection:
    
    def __init__(self):
        self.output = ''
        self.hostname = serverEntry.get().strip()
        self.port = portEntry.get().strip()
        self.username = unameEntry.get().strip()
        self.password = pwdEntry.get().strip()
        if varval.get() == 1:
            self.command_1 = 'sudo -u mqm runmqsc ' + r1_1.get()
            if var1_2.get() == 'display':
                self.command_2 = var1_2.get() + ' qlocal ' + "('" + r1_4.get() + "') CURDEPTH MAXDEPTH"
            elif var1_2.get() == "alter":
                self.command_2 = var1_2.get() + ' qlocal' + "('" + r1_4.get() + "') MAXDEPTH(" + r1_4.get() + ")" 
        elif varval.get() == 2:
            self.command_1 = 'runmqsc ' + r2_1.get()
            self.command_2 = var2_2.get() + " channel('" + r2_3.get() + "')"  
            if var2_2 == 'stop':
                self.command_2 += ' MODE(FORCE)'
        elif varval.get() == 3:
            self.command_1 = "/appli/scripts/pilotage/" + var3_1.get() + " " + r3_2.get() + " " + r3_3.get()
        elif varval.get() == 4:
            self.command = r4_1.get()
            r4_1.delete(0, 'end')    
            
    
    def idle(self):
        print('wait')
        global flag_exit
        thread1_idle.clear()
        thread1_idle.wait()
        if flag_exit:
            os._exit(1)
        self.exec_connection()
    
    def entry_delete(self):
        if(varval.get() == 1):
            r2_1.delete(0, 'end')
            r2_3.delete(0, 'end')
            r3_2.delete(0, 'end')
            r3_3.delete(0, 'end')
            r4_1.delete(0, 'end')
            
        if(varval.get() == 2):
            r1_1.delete(0, 'end')
            r1_4.delete(0, 'end')
            r3_2.delete(0, 'end')
            r3_3.delete(0, 'end')
            r4_1.delete(0, 'end')
        
        if(varval.get() == 3):
            r1_1.delete(0, 'end')
            r1_4.delete(0, 'end')
            r2_1.delete(0, 'end')
            r2_3.delete(0, 'end')
            r4_1.delete(0, 'end')
            
        if(varval.get() == 4):
            r1_1.delete(0, 'end')
            r1_4.delete(0, 'end')
            r2_1.delete(0, 'end')
            r2_3.delete(0, 'end')
            r3_2.delete(0, 'end')
            r3_3.delete(0, 'end')
    
        
    def output_recv(self):
        while True:
            if self.channel.recv_ready():
                self.output = self.channel.recv(1024).decode('utf-8')
                outpt_insert(self.output)
                outpt.see("end")
                print(self.output, sep=' ', end='', flush=True)
#                 buf = io.StringIO(self.output)
#                 for lines in buf.read().split('\n'):
#                     print(lines)
                time.sleep(0.25)
            elif (self.hostname + ":" + self.username) in self.output and self.channel.recv_ready() == False:
                break
            
    def output_recv_short(self):
        Counter = 0
        while True:
            if self.channel.recv_ready():
                self.output = self.channel.recv(1024).decode('utf-8')
                outpt_insert(self.output)
                outpt.see("end")
                print(self.output, sep=' ', end='', flush=True)
                Counter = 0
            elif (self.hostname + ":") in self.output:
                Counter = 0
                break
            elif self.channel.recv_ready() == False:
                time.sleep(.1)
                Counter += 1
                if Counter > 10:
                    break
                
                
            
#     def buffer(self, out):
#         global first
#         if('%') in out:
#             try:
#                 if int(out.split('%')[0]) >= 0 and int(out.split('%')[0]) <= 100:
#                     self.second = out.split('%')[0]
#                     if(first != self.second):
#                         first = self.second
#                         print(self.second + '%', end = '')
#             except:
#                 pass
#         else:
#             print(out)
                
    def exec_connection(self):
        self.__init__()
        try:
            self.sshClient = paramiko.SSHClient()
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshClient.connect(self.hostname + '.unix.appliarmony.net', username = self.username, password = self.password)
            self.channel = self.sshClient.get_transport().open_session()
            self.channel.get_pty()
            self.channel.invoke_shell()
            outpt_insert('CONNECTION INITIALIZED\n\n')
            self.output_recv_short()
        except:
            outpt_insert('Something went wrong, check Server\n')
            self.sshClient.close()
            self.idle()
            
        while True:
            
            if flag_exit:
                try:
                    self.sshClient.close()
                except:
                    pass
                os._exit(1)
            
            thread1_event.clear()
            thread1_event.wait()
            
            if flag_exit:
                try:
                    self.sshClient.close()
                except:
                    pass
                os._exit(1)
            
            self.__init__()

            if varval.get() == 0:
                messagebox.showinfo('INFO', 'Select Script first')
            
            else:
                
                self.entry_delete()
            
                if (varval.get() == 1):
                    
                    if hasattr(Connection(), 'command_1'):
                        if r1_1.get() != '':
                            self.channel.send(self.command_1 + '\n')
                            r1_1.delete(0, 'end')
                            self.output_recv_short()

                    if hasattr(Connection(), 'command_2'):
                        self.channel.send(self.command_2 + '\n')
                        self.output_recv_short()
              
                elif(varval.get() == 2):
                    
                    if hasattr(Connection(), 'command_1'):
                        if r2_1.get() != '':
                            self.channel.send(self.command_1 + '\n')
                            r2_1.delete(0, 'end')
                            self.output_recv_short()
                        
                    if hasattr(Connection(), 'command_2'):
                        self.channel.send(self.command_2 + '\n')
                        self.output_recv_short()
                        
                elif(varval.get() == 3):
                    
                    if hasattr(Connection(), 'command_1'):
                        self.channel.send(self.command_1 + '\n')
                        self.output_recv()
                        
                
                
#                     else:
#                         messagebox.showinfo('INFO', 'No data given')
                        
#                 elif (varval.get() == 3):
#                     self.entry_delete()
#                     stdin_, stdout_, stderr_ = self.sshClient.exec_command(self.command_1)
#                     outpt_insert('\nWait for output... Patiently...\n')
#                     print('\nWait for output... Patiently...\n')
#                     stdout_.channel.recv_exit_status()
#                     lines = stdout_.readlines()
#                     for line in lines:
#                         print(line)
#                     outpt_insert('\nOutput ready in CMD\n')
                
                elif (varval.get() == 4):
                    self.entry_delete()
                    hasattr(Connection(), 'command')
                    command = self.command 
                    self.channel.send(command + '\n')
                    self.output_recv_short()
                    if command == 'exit':
                        print('\nLogged out successfully')
                        outpt_insert('\nLogged out successfully')
                        outpt.see('end')
                        break
                  
            
        self.sshClient.close()
        self.idle()
        

def clipboard_paste(event):
    data = pyperclip.paste().split()
    
    if len(data) == 3:
        serverEntry.insert(0,data[0])
        
        if varval.get() == 1:
            serverEntry.delete(0, 'end')
            r1_1.delete(0, 'end')
            r1_4.delete(0, 'end')
            serverEntry.insert(0,data[0])
            r1_1.insert(0, data[1])
            r1_4.insert(0, data[2])
            
        if varval.get() == 2:
            serverEntry.delete(0, 'end')
            r2_1.delete(0, 'end')
            r2_3.delete(0, 'end')
            serverEntry.insert(0,data[0])
            r2_1.insert(0, data[1])
            r2_3.insert(0, data[2])
            
        if varval.get() == 3:
            serverEntry.delete(0, 'end')
            r3_2.delete(0, 'end')
            r3_3.delete(0, 'end')
            serverEntry.insert(0,data[0])
            r3_2.insert(0, data[1])
            r3_3.insert(0, data[2])
            
        if varval.get() == 4:
            serverEntry.delete(0, 'end')
            serverEntry.insert(0,data[0])
            
    elif len(data) == 1:
        serverEntry.delete(0, 'end')
        serverEntry.insert(0,data[0])
        
def prev_command_save():
    prev_command_list.append(r4_1.get())
    
def prev_command_get(event):
    global prev_command_count
    e = list(reversed(prev_command_list))
    r4_1.delete(0, 'end')
    r4_1.insert(0, e[prev_command_count])
    prev_command_count += 1

def thread1_event_set(event):
    thread1_event.set()
    if r4_1.get() != "":
        prev_command_save()
    if r4_1_focus:
        global prev_command_count
        prev_command_count = 0
    
def thread1_idle_set(event = None):
    thread1_idle.set()
    
def outpt_insert(text):
    outpt.config(state = NORMAL)
    outpt.insert(END, text)
    outpt.config(state = DISABLED)
    
def r4_1_focusIn(event):
    global r4_1_focus
    r4_1_focus = True
    
def r4_1_focusOut(event):
    global r4_1_focus
    r4_1_focus = False

def show_shortcuts():
    messagebox.showinfo(
                        'SHORTCUTS', 'ENTER\nSend command to the server\n\n'
                        + 'F1 - F4\nSelect script\n\n'
                        + 'F9\nPaste data into the fields.\nData in clipboard must be formated as follows:\nServerName Argument1 Argument2\nOR\nServerName\n\n'
                        + 'F12\nExecute Connection (Same as "CONNECT" button)'
                        )
                        
    
def F1(event):
    varval.set(1)

def F2(event):
    varval.set(2)

def F3(event):
    varval.set(3)

def F4(event):
    varval.set(4)
    r4_1.focus_set()
    
def change_color():
    widgets_bw = [serverFrame, serverEntry, portEntry, unameEntry, pwdEntry, saveButton,
               scriptFrame, r1_1, r1_2, r1_3, r1_4, r2_1, r2_2, r2_3, r3_1, r3_2, r3_3, r4_1, 
               outputFrame, outpt]
    
    widgets_b = [scriptFrame_1, scriptFrame_2, scriptFrame_3, scriptFrame_4]
    
    widgets_optbutt = [r1_2, r2_2, r3_1]
    
    widgets_radio = [r1, r2, r3, r4]
    
    widgets_text = [serverEntry, unameEntry, portEntry, pwdEntry, r1_1, r1_4, r2_1, r2_3, r3_2, r3_3, r4_1]
    
    for wid in widgets_bw:
        wid.configure(bg = "black", fg = "white")
        
    for wid in widgets_b:
        wid.configure(bg = "black")

    for wid in widgets_optbutt:
        wid.configure(bg = "black", fg = "white", activebackground = "black", activeforeground = "white", disabledforeground = 'black', highlightthickness=0)
        wid['menu'].config(bg = "black", fg = "white", activebackground = "black", activeforeground = "white", selectcolor = "white", borderwidth = 0)
    
    for wid in widgets_radio:
        wid.configure(bg = "black", fg = "white", activebackground = "black", activeforeground = "white", highlightbackground = "black", highlightcolor = "white", selectcolor = "black")
        
    for wid in widgets_text:
        wid.configure(insertbackground = "white")
    
def quit_():
    global flag_exit
    flag_exit = True
    thread1_idle.set()
    thread1_event.set()


root = Tk()
root.title("SSH")
root.configure(bg = "black")
root.geometry('960x1080+951+0')
root.protocol("WM_DELETE_WINDOW", quit_)

flag_exit = False

prev_command_list = []
prev_command_count = 0
r4_1_focus = False
first = 0


# FILEMENU
menubar = Menu(root)
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label = 'Show shortcuts', command = show_shortcuts)
menubar.add_cascade(label = 'help', menu = filemenu)
root.config(menu = menubar)



# SERVER DETAILS
serverFrame = LabelFrame(root, text = "Server Connection", padx = 15, pady = 15)
serverFrame.grid(row = 0, column = 0)

Label(serverFrame, text = "Server", bg = "black", fg = "white").grid(row = 0, column = 0)
serverEntry = Entry(serverFrame)
serverEntry.grid(row = 0, column = 1)
Label(serverFrame, text = "Port", bg = "black", fg = "white").grid(row = 0, column = 2)
portEntry = Entry(serverFrame)
portEntry.grid(row = 0, column = 3)
Label(serverFrame, text = "User Name", bg = "black", fg = "white").grid(row = 1, column = 0)
unameEntry = Entry(serverFrame)
unameEntry.grid(row = 1, column = 1)
Label(serverFrame, text = "Password", bg = "black", fg = "white").grid(row = 2, column = 0)
pwdEntry = Entry(serverFrame, show = '*')
pwdEntry.grid(row = 2, column = 1)

credentialsFrame = Frame(serverFrame)
credentialsFrame.grid(row = 3, column = 0, sticky = W, pady = (10,0))
saveButton = Button(credentialsFrame, text = "Save credentials", command = Rememberator().save_credentials)
saveButton.grid(row = 0, column = 0)



# SCRIPT
scriptFrame = LabelFrame(root, text = "Scripts", padx = 15, pady = 15)
scriptFrame.grid(row = 1, column = 0)

varval = IntVar()
var1_2 = StringVar()
var1_2.set('display')
scriptFrame_1 = Frame(scriptFrame)
scriptFrame_1.grid(row = 0, column = 0, sticky = W, pady = 5)
r1 = Radiobutton(scriptFrame_1, text = "sudo -u mqm runmqsc", variable = varval, value = 1)
r1.grid(row = 0, column = 0)
r1_1 = Entry(scriptFrame_1)
r1_1.grid(row = 0, column = 1)
r1_2 = OptionMenu(scriptFrame_1, var1_2, 'display', 'alter')
r1_2.grid(row = 0, column = 2)
r1_3 = Label(scriptFrame_1, text = "qlocal")
r1_3.grid(row = 0, column = 3)
r1_4 = Entry(scriptFrame_1)
r1_4.grid(row = 0, column = 4)

var2_2 = StringVar()
var2_2.set("display")
scriptFrame_2 = Frame(scriptFrame)
scriptFrame_2.grid(row = 1, column = 0, sticky = W, pady = 5)
r2 = Radiobutton(scriptFrame_2, text = "runmqsc", variable = varval, value = 2)
r2.grid(row = 0, column = 0)
r2_1 = Entry(scriptFrame_2)
r2_1.grid(row = 0, column = 1)
r2_2 = OptionMenu(scriptFrame_2, var2_2, 'display', 'stop', 'reset', 'start')
r2_2.grid(row = 0, column = 2) 
r2_3 = Entry(scriptFrame_2)
r2_3.grid(row = 0, column = 3)

var3_1 = StringVar()
var3_1.set("statusAS")
scriptFrame_3 = Frame(scriptFrame)
scriptFrame_3.grid(row = 2, column = 0, sticky = W, pady = 5)
r3 = Radiobutton(scriptFrame_3, text = "/appli/scripts/pilotage/", variable = varval, value = 3)
r3.grid(row = 0, column = 0)
r3_1 = OptionMenu(scriptFrame_3, var3_1, 'statusAS', 'stopAS', 'startAS')
r3_1.grid(row = 0, column = 1)
r3_2 = Entry(scriptFrame_3)
r3_2.grid(row = 0, column = 2)
r3_3 = Entry(scriptFrame_3)
r3_3.grid(row = 0, column = 3)

scriptFrame_4 = Frame(scriptFrame)
scriptFrame_4.grid(row = 3, column = 0, sticky = W, pady = 5)
r4 = Radiobutton(scriptFrame_4, text = 'Custom command: ', variable = varval, value = 4)
r4.grid(row = 0, column = 0)
r4_1 = Entry(scriptFrame_4)
r4_1.grid(row = 0, column = 1)



# OUTPUT
outputFrame = LabelFrame(root, text = "Output", padx = 15, pady = 15)
outputFrame.grid(row = 2, column = 0, sticky = W)

outpttxt = ""
outpt = Text(outputFrame, width = 113)

outpt.grid(row = 0, column = 0, sticky = W)
outpt_scroll = Scrollbar(outputFrame, command = outpt.yview)
outpt_scroll.grid(row = 0, column = 1, sticky = 'nsew')
outpt['yscrollcommand'] = outpt_scroll.set

change_color()

# KEY BINDINGS
root.bind('<Return>', thread1_event_set)
root.bind('<F1>', F1)
root.bind('<F2>', F2)
root.bind('<F3>', F3)
root.bind('<F4>', F4)
root.bind('<F9>', clipboard_paste)
root.bind('<F12>', thread1_idle_set)
r4_1.bind('<Up>', prev_command_get)
r4_1.bind('<FocusIn>', r4_1_focusIn)
r4_1.bind('<FocusOut>', r4_1_focusOut)


connect_button = Button(root, text = 'CONNECT', command = thread1_idle_set, bg = "black", fg = "white").grid(row = 10, column = 0)

# THREADING
thread1 = threading.Thread(name = "Thread-1", target = Connection().idle)
thread1_event = threading.Event()
thread1_idle = threading.Event()
thread1.start()
thread2 = threading.Thread(name = 'Thread-2', target = Rememberator().insert_credentials())
thread2.start()


root.mainloop()

# chujowo zriobione troche, caly mainloop powinien byc zrealizowany jako osobny thread
