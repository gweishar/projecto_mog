from Tkinter import *
from obspy.core import *
from obspy.signal.trigger import classicSTALTA, plotTrigger
from obspy.signal import seisSim, cornFreq2Paz
#from obspy.signal import seisSim, cornFreq2Paz
from tkFileDialog import *
#from obspy.gse2.paz import readPaz
#from obspy.xseed import Parser
import Pmw
from obspy.xseed import Parser
stream_data= {} #dictionary with saved streams
parser_data= {} #dictionary with saved parser data for stations
import os

class Gui:
   def __init__(self, master):
      
      
      self.frame = Frame(master)
      # Create the Balloon.
      self.balloon = Pmw.Balloon(master) 
      #Create the menu bar
      self.makeMenuBar(master, self.balloon) 
       
      # Create and pack the canvas
      self.scrolledCanvas = Pmw.ScrolledCanvas(master,
                canvas_width = 500,
                canvas_height = 215)
      self.scrolledCanvas.pack()   
      
      #Create the button box   
      self.buttonBox = Pmw.ButtonBox(master,
                labelpos = 'nw',
                label_text = 'Data Processing',
                frame_borderwidth = 2,
                frame_relief = 'groove')
      self.buttonBox.pack(fill = 'both', expand = 1, padx = 10, pady = 10)
      
      self.buttonBox.add('Plot Stream Data',command = self.plot_stream_options)
      self.buttonBox.add('Filter Options', command = self.filter_options)
      self.buttonBox.add('Convolution', command = self.convolution_options)
      
      self.frame.pack()
      
   
   def makeMenuBar(self,master, balloon):
      ''' Creates the top menu bar options of the application'''
      menuBar = Pmw.MenuBar(master,
		       hull_relief = 'raised',
               hull_borderwidth = 1,balloon = self.balloon)
               
      menuBar.pack(side="top", fill = 'x')
      self.menuBar = menuBar
	  
      menuBar.addmenu('Load','Select and load seismic data')
      menuBar.addmenuitem('Load','command','open a stream file',
            command = self.load_stream,
            label = 'Stream File')            
      menuBar.addmenuitem('Load','command','open a dataless file',
            command = self.load_dataless,
            label = 'Dataless File')
            
      menuBar.addmenu('Edit', 'Data Options')
      menuBar.addmenuitem('Edit','command','Delete stream data',
            command = self._del_stream,
            label = 'Stream clearing')
      menuBar.addmenuitem('Edit','command','Delete parser data',
            command = self._del_parser,
            label = 'Parser clearing')
      menuBar.addmenuitem('Edit','command','Save Stream Data',
            command = self.save_options,
            label = 'Save Stream Data')
      
      menuBar.addmenu('Options', 'General Options')
      menuBar.addmenuitem('Options','command','Check stream stats',
            command = self.display_stats_options,
            label = 'Stream Stats')
      
             
   def _del_stream(self):
      '''Clears the stream data dictionary'''
      try:
         stream_data.clear()
      except:
         print "Problem with the data struture"
      finally:
         print "The stream data was cleared. Ready for more" 
         
   def _del_parser(self):
      '''Clears the parser data dictionary'''
      
      try:
         parser_data.clear()
      except:
         print "Problem with the data struture"
      finally:
         print "The parser data was cleared. Ready for more"
                  
   def load_stream(self):
      ''' User input: Locate the directory of the waveform file and reads
          it using the read method from obspy.
      
      Saves the stream into the stream_data dictionary'''
      
      dir_stream=askopenfilenames()
      
      for dir in dir_stream:
         try:      
            st=read(dir)
         except:
            print('Problem reading the waveform file, try another one')
         else:
            stream_data[st[0].stats.station]=st         

   def load_dataless(self):
      ''' User input: Locate and saves the directory of the dataless file into the
      parser_data dictionary.
      
      Saves the parser data using the parser method from obspy, 
      into parser_data dictionary'''
      
      dir_dl=askopenfilenames()
      
      key_name="" #key name for the dictionary data
      for dir in dir_dl:
         for c in dir:
            if c != '.':
               key_name+=c
            else:
               break
               
         parser=Parser(dir)
    
         parser_data[key_name]=parser
      '''try:      
         parser=Parser(dir_dl)
      except:
         print('Problem parsing the dataless file, try another one')
      else:
         parser_data[key_name]=parser'''
    
   def create_selection_box(self):
      ''' Creates a selection box with the stream data. Uses the global dictionary
       stream_data
       
       The check list is created using a for loop calling the object selection_box'''
      try:
         #Check if dictionary stream_data is empty. Raises exception if so.
         if stream_data:
            pass       
                 
      except:
         print "You haven't loaded the streams yet"
         
      else:
         self.selection_box=Toplevel(self.frame)         
         self.button_dic=stream_data.copy()
         #Set all values in the button_dic to zero
         for key in self.button_dic: self.button_dic[key]=0
      
         for key in self.button_dic:
            self.button_dic[key] = IntVar()
            check_button = Checkbutton(self.selection_box, text=key,
                             variable=self.button_dic[key])
            check_button.pack(side="top")
            
   def display_stats_options(self):
      ''' Displays the seleted stream stats inside the canvas component '''
      
      self.create_selection_box()
      self.selection_box.title('Select Streams')
      display_button=Button(self.selection_box, text="Display Stats", 
                         command=self.display_stats)
      display_button.pack()
      
      cancel_button=Button(self.selection_box, text="Cancel", 
                         command=self.selection_box.destroy)
      cancel_button.pack()
      
   def display_stats(self):
   
      for key, value in self.button_dic.items():
         state = value.get()
         if state:
            st=stream_data[key]
            for tr in st:
               print tr.stats
              
            self.button_dic[key].set(0)
            
   def convolution_automatic(self):
      #st=stream_data.values().copy()
      #for tr in st and key in parser_data:
      
      inst2hz = cornFreq2Paz(float(self.inst2hz.getvalue())) #what the hell is this?
      waterLevel=float(self.water_level.getvalue())
      for key, st in stream_data:
         for tr in st:
            try:
               pr=parser_data.find(key[0:2])
            except:
               print "Try the manual option"
            else:
               paz=pr.getPAZ(tr.stats)
            
               df = tr.stats.sampling_rate
               tr.data = seisSim(tr.data, df, paz_remove=paz, paz_simulate=inst2hz,
						     water_level=waterLevel) 
			
			#save data into a user seleted dirotory 

   def convolution_options(self):
      self.create_selection_box()
      self.selection_box.title('Convolution options')
						
      self.inst2hz=Pmw.EntryField(self.selection_box,
                    labelpos = 'w',
                    label_text = 'Inst to Hz:',
                    value = 2.0,
                    validate = {'validator' : 'real'})
      self.inst2hz.pack()  
          
      self.water_level=Pmw.EntryField(self.selection_box,
                    labelpos = 'w',
                    label_text = 'Inst to Hz:',
                    value = 60,
                    validate = {'validator' : 'real'})
      self.water_level.pack() 
      
      auto_button=Button(self.selection_box, text="Automatic", 
                         command=self.convolution_automatic)
      auto_button.pack()  
      
      manual_button=Button(self.selection_box, text="Manual", 
                         command=self.convolution_manual)
      manual_button.pack()  
                      
      cancel_button=Button(self.selection_box, text="Cancel", 
                         command=self.selection_box.destroy)
      cancel_button.pack()
      
   def convolution_manual(self):
      ''' create a cross list type widget to associate the parser file with the 
      wafeform data'''
      
   def save_options(self):
      self.create_selection_box()
      self.selection_box.title('Select the streams you wish to save') 
      
      save_button=Button(self.selection_box, text="Save", 
                         command=self.save_stream)
      save_button.pack(side=BOTTOM)
      cancel_button=Button(self.selection_box, text="Cancel", 
                         command=self.selection_box.destroy)
      cancel_button.pack(side=BOTTOM)
      
   def save_stream(self):
      ''' '''
      save_dir=askdirectory()
      
      for key, value in self.button_dic.items():
         state = value.get()
         if state:
            file_name=open(os.path.join(save_dir,key+'.mseed'),"w")
            stream_data[key].write(file_name,format='MSEED')
            self.button_dic[key].set(0)   
            
   def filter_options(self):
      self.create_selection_box()
      self.selection_box.title('Butterworth Filter options')
      
      self.freq_min=Pmw.EntryField(self.selection_box,
                    labelpos = 'w',
                    label_text = 'Freq Min (Hz):',
                    value = 1,
                    validate = {'validator' : 'numeric'})
      self.freq_min.pack()
    
      
      self.freq_max=Pmw.EntryField(self.selection_box,
                    labelpos = 'w',
                    label_text = 'Freq Max (Hz):',
                    value = 20,
                    validate = {'validator' : 'numeric'})
      self.freq_max.pack()
      
      self.freq=Pmw.EntryField(self.selection_box,
                    labelpos = 'w',
                    label_text = 'Corner Freq (Hz):',
                    value = 1,
                    validate = {'validator' : 'numeric'})
      self.freq.pack()
      b_pass='bandpass'; b_stop='bandstop'; h_pass='highpass'; l_pass='lowpass';  
      
      bandpass_button=Button(self.selection_box, text="Bandpass",
                         command=lambda: self.apply_filter(b_pass))
      bandpass_button.pack()
      
      bandstop_button=Button(self.selection_box, text="Bandstop",
                         command=lambda: self.apply_filter(b_stop))
      bandstop_button.pack()
      
      
      highpass_button=Button(self.selection_box, text="Highpass",
                         command=lambda: self.apply_filter(h_pass))
      highpass_button.pack()
      
      lowpass_button=Button(self.selection_box, text="Lowpass",
                         command=lambda: self.apply_filter(l_pass))
      lowpass_button.pack()
      
      
      cancel_button=Button(self.selection_box, text="Cancel", 
                         command=self.selection_box.destroy)
      cancel_button.pack(side=BOTTOM)
   
   def apply_filter(self, filter_key):
      ''' Apply's the given filtered by keyword filter_key.
      
          Saves the filtered stream into stream_data with the 
          keyword: [station name]_filtered'''
      
      for key, value in self.button_dic.items():
         state = value.get()
         if state:
            temp=stream_data[key].copy()
            #Detrend the stream object
            temp.detrend()
            #Apply the bandpass or stop filter
            if filter_key.startswith('band'):
               temp.filter(filter_key,freqmin=int(self.freq_min.getvalue()), 
                     freqmax=int(self.freq_max.getvalue()))
               stream_data[key+'_filtered']=temp.copy()
               stream_data[key+'_filtered'].plot() 
            else:
            #Apply the high or low pass filter
               temp.filter(filter_key,freq=int(self.freq.getvalue()))
               stream_data[key+'_filtered']=temp.copy()
               stream_data[key+'_filtered'].plot() 
            self.button_dic[key].set(0) 
         
  
   def plot_stream_options(self):
      '''Plots the stream file that was previsouly loaded by the user'''
      self.create_selection_box()
      self.selection_box.title('Selecting Stations')
      plot_button = Button(self.selection_box, text="Plot", command=self.plot_stream)
      plot_button.pack()
      cancel_button=Button(self.selection_box, text="Cancel", 
                         command=self.selection_box.destroy)
      cancel_button.pack()
      
   def plot_stream(self):     
      for key, value in self.button_dic.items():
         state = value.get()
         if state:
            stream_data[key].plot()
            self.button_dic[key].set(0)
          
#############################################  
    
root = Tk()
root.geometry("600x400")
root.title('Gorbatikov Method')

exitButton = Button(root, text = 'Exit', command =root.destroy)
exitButton.pack(side=BOTTOM)

gui = Gui(root)
root.mainloop()
      