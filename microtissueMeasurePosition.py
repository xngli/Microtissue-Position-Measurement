from __future__ import division
import glob, numpy
import Tkinter as tk
import tkFileDialog
from PIL import Image, ImageTk

# constants
canvas_width = 1024
canvas_height = 768
marker_size = 20    # size of the marker after you click a point on canvas
margin = 20

class Point:
    """Represents a point in 2-D space."""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Microtissue Position Measuremen")
        self.marker_left = Point(0, 0)
        self.marker_right = Point(1, 1)  # avoid division by zero
        self.point_chamber_top = Point(0, 0)
        self.point_chamber_bottom = Point(0, 0)
        self.point_left_top = Point(0, 0)
        self.point_left_bottom = Point(0, 0)
        self.point_right_top = Point(0, 0)
        self.point_right_bottom = Point(0, 0)
        self.tag = 1
        self.image_index = 0
        self.result = numpy.array([])
        self.createWidgets()
        
    def createWidgets(self):
        """create a series of buttons and a canvas."""
        # button for select directory    
        self.button = tk.Button(self, text='Select Directory', padx=5, pady=5) 
        self.button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.button.bind("<1>", self.select_dir)
        # label displaying selected directory
        self.tv = tk.StringVar() 
        self.label = tk.Label(self, textvariable=self.tv, width=50, height=5)
        self.label.grid(row=0, column=1, pady=10)
        # label displaying instructions
        self.instr = tk.StringVar() 
        self.label_instr = tk.Label(self, textvariable=self.instr, 
                                    anchor="e", width=35, height=5, 
                                    font=("Helvetica", 12, "bold"))
        self.label_instr.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.instr.set("Select directory")
        # canvas for displaying image and selecting points
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.canvas.grid(row=1, columnspan=3, pady=10)
#        # button for rotation
#        self.button_rotate = tk.Button(self, text='Rotate', padx=5, pady=5)
#        self.button_rotate.grid(row=2, column=0, padx=10, pady=10, sticky="w")
#        self.button_rotate.bind("<1>", self.rotate_image)
        # button for next image
        self.button_next = tk.Button(self, text='Next', padx=5, pady=5)
        self.button_next.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.button_next.bind("<1>", self.display_image)
        # button for exit
        self.buttonExit = tk.Button(self, text='Exit', padx=5, pady=5, 
                                    command=self.destroy)
        self.buttonExit.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        
    def select_dir(self, event):
        """Select directory that contains the images."""
        self.dirname = tkFileDialog.askdirectory(parent=self, 
                        initialdir='G:\OneDrive\Microtissue Positions', 
                        title='Please select a directory')
        self.tv.set(self.dirname)
        self.imNameList = glob.glob(self.dirname + '/*.png')
        self.instr.set("Click Next")
        
    def display_image(self, event):
        if self.image_index == len(self.imNameList):
            self.instr.set("Measurement done!")
            return
        imName = self.imNameList[self.image_index]
        self.im = Image.open(imName)
        img = ImageTk.PhotoImage(self.im)
        self.canvas.image = img
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.cursor_h = self.canvas.create_line(0, 0, 0, 0, fill="red")
        self.cursor_v = self.canvas.create_line(0, 0, 0, 0, fill="red")
        self.canvas.bind("<Motion>", self.display_cursor)
        self.canvas.bind("<1>", self.align)
        self.image_index += 1
        self.instr.set("Image rotation")
    
    def display_cursor(self, event):
        """Display current cursor position."""
        x, y = event.x,event.y
        self.canvas.coords(self.cursor_h, 0, y, canvas_width-1, y)
        self.canvas.coords(self.cursor_v, x, 0, x, canvas_height-1)
        self.canvas.update()
        
    def align(self, event):
        x, y = event.x, event.y
        self.canvas.create_line(x-marker_size/2, y, x+marker_size/2, y, 
                                fill="blue")
        self.canvas.create_line(x, y-marker_size/2, x, y+marker_size/2, 
                                fill="blue")
        if self.tag == 1:
            # left marker
            self.marker_left = Point(x, canvas_height-y)
            self.tag = 2
        else:
            # right marker
            self.marker_right = Point(x, canvas_height-y)
            self.canvas.delete(self.cursor_h)
            self.canvas.delete(self.cursor_v)
            self.canvas.unbind("<Motion>")
            self.canvas.unbind("<1>")
            self.tag = 1
            self.rotate_image()
            
    def rotate_image(self):
        theta = numpy.arctan((self.marker_left.y-self.marker_right.y)/  \
                (self.marker_right.x-self.marker_left.x))/numpy.pi*180
#        theta = (-theta) % 360
        img = ImageTk.PhotoImage(self.im.rotate(theta))
        self.canvas.delete(tk.ALL)
        self.canvas.image = img
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.cursor_h = self.canvas.create_line(0, 0, 0, 0, fill="red")
        self.cursor_v = self.canvas.create_line(0, 0, 0, 0, fill="red")
        self.canvas.bind("<Motion>", self.display_cursor)
        self.canvas.bind("<1>", self.measure_position)
        self.instr.set("Define chamber position")
        
    def measure_position(self, event):
        x, y = event.x, event.y
        self.canvas.create_line(x-marker_size/2, y, x+marker_size/2, y, 
                                fill="blue")
        self.canvas.create_line(x, y-marker_size/2, x, y+marker_size/2, 
                                fill="blue")
        if self.tag == 1:
            # chamber bottom
            self.canvas.create_text(x, y, anchor="se", text="C0")
            self.point_chamber_bottom = Point(x, canvas_height-y)
            self.tag = 2
        elif self.tag == 2:
            # chember top
            self.canvas.create_text(x, y, anchor="se", text="C1")
            self.point_chamber_top = Point(x, canvas_height-y)
            self.tag = 3
            self.instr.set("Define microtissue position on left post")
        elif self.tag == 3:
            # left microtissue anchor bottom
            self.canvas.create_text(x, y, anchor="se", text="L0")
            self.point_left_bottom = Point(x, canvas_height-y)
            self.tag = 4
        elif self.tag == 4:
            # left microtissue anchor top
            self.canvas.create_text(x, y, anchor="se", text="L1")
            self.point_left_top = Point(x, canvas_height-y)
            self.tag = 5
            self.instr.set("Define microtissue position on right post")
        elif self.tag == 5:
            # right microtissue anchor bottom
            self.canvas.create_text(x, y, anchor="se", text="R0")
            self.point_right_bottom = Point(x, canvas_height-y)
            self.tag = 6
        else:
            # right microtissue anchor top
            self.canvas.create_text(x, y, anchor="se", text="R1")
            self.point_right_top = Point(x, canvas_height-y)
            self.tag = 1
            self.result = numpy.append(self.result, 
                                       [self.point_chamber_bottom.y, 
                                        self.point_chamber_top.y,
                                        self.point_left_bottom.y, 
                                        self.point_left_top.y,
                                        self.point_right_bottom.y, 
                                        self.point_right_top.y])
            self.canvas.delete(self.cursor_h)
            self.canvas.delete(self.cursor_v)
            self.canvas.unbind("<Motion>")
            self.canvas.unbind("<1>")
            self.instr.set("Positions saved. Click Next")
    
app = App()     
app.mainloop()

app.result = app.result.reshape((-1, 6))
numpy.savetxt(app.dirname+'/positions.txt', app.result, fmt='%.1f', 
              delimiter=' ', header='C0 C1 L0 L1 R0 R1', 
              comments='')