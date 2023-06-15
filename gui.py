"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import sys

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface



class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(0.95, 0.89, 0.59, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.
   def run_command(self):
        #Run the simulation from scratch.
        self.cycles_completed = 0
        cycles = self.read_number(0, None)
   def run_command(self):
        #Run the simulation from scratch.
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycfrom userint import UserInterfaceles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.
    
    on_continue_button(self, event): Event handler for when the user clicks the continue
                                button.
    
    on_switch_button1(self, event): Event handler for when the user clicks the switch1
                                button.
    
    on_switch_button0(self, event): Event handler for when the user clicks the switch0
                                button.
    
    on_set_monitor_button(self, event): Event handler for when the user clicks the set monitor
                                button.
                                
    on_zap_monitor_button(self, event): Event handler for when the user clicks the zap monitor
                                button.
    
    on_quit_button(self, event): Event handler for when the user clicks the quit
                                button.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu

        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.cyclestext = wx.StaticText(self, wx.ID_ANY, "Number of Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.switch1_button = wx.Button(self, wx.ID_ANY, "On")
        self.switch0_button = wx.Button(self, wx.ID_ANY, "Off")
        self.set_monitor_button = wx.Button(self, wx.ID_ANY, "Monitor")
        self.zap_monitor_button = wx.Button(self, wx.ID_ANY, "Zap")
        self.help_button = wx.Button(self, wx.ID_ANY, "Help")
        self.quit_button = wx.Button(self, wx.ID_ANY, "Quit")

        self.switext = wx.StaticText(self, label = "Switch")
        switch_names = ["sw1","swb","swc"]
        self.swicombobox = wx.ComboBox(self, choices = switch_names)

        self.sigtext = wx.StaticText(self, label = "Signal")
        signal_names = ["sw1","clk1","sigc"]
        
        self.sigcombobox = wx.ComboBox(self, choices = signal_names)

        self.montext = wx.StaticText(self, label = "Monitor")
        monitor_names = ["k", "sw1", "clk1", "sigc"]
        self.moncombobox = wx.ComboBox(self, choices = monitor_names)



        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.swicombobox.Bind(wx.EVT_COMBOBOX, self.on_swicombobox)
        self.sigcombobox.Bind(wx.EVT_COMBOBOX, self.on_sigcombobox)
        self.moncombobox.Bind(wx.EVT_COMBOBOX, self.on_moncombobox)
        self.switch1_button.Bind(wx.EVT_BUTTON, self.on_switch1_button)
        self.switch0_button.Bind(wx.EVT_BUTTON, self.on_switch0_button)
        self.set_monitor_button.Bind(wx.EVT_BUTTON, self.on_set_monitor_button)
        self.zap_monitor_button.Bind(wx.EVT_BUTTON, self.on_zap_monitor_button)
        self.quit_button.Bind(wx.EVT_BUTTON, self.on_quit_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        rc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cycle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        onoff_sizer = wx.BoxSizer(wx.HORIZONTAL)
        helpquit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sim_sizer = wx.StaticBoxSizer(wx.StaticBox(self, id=wx.ID_ANY, label='Simulation'), wx.VERTICAL)
        #swi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #sig_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #mon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sm_sizer = wx.StaticBoxSizer(wx.StaticBox(self, id=wx.ID_ANY, label='Switches and Monitors'), wx.VERTICAL)
        smgrid_sizer = wx.FlexGridSizer(rows=3,cols=3,vgap=1,hgap=5)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        #side_sizer.Add(self.simtext, 1, wx.TOP, 10)
        #sim_sizer.Add(cycle_sizer,1, wx.ALL, 5)
        
        sim_sizer.Add(cycle_sizer,1,wx.ALL,5)
        sim_sizer.Add(rc_sizer,1,wx.ALL,5)

        #side_sizer.Add(self.cyclestext, 1, wx.TOP, 10)
        cycle_sizer.Add(self.cyclestext, 1, wx.ALL, 5)
        cycle_sizer.Add(self.spin, 1, wx.ALL, 5)
        #side_sizer.Add(cycle_sizer,1, wx.ALL, 5)

        rc_sizer.Add(self.run_button, 1, wx.ALL, 5)
        rc_sizer.Add(self.continue_button, 1, wx.ALL, 5)
        side_sizer.Add(sim_sizer,1,wx.ALL,5)
        #side_sizer.Add(rc_sizer,1,wx.ALL,5)

        """
        swi_sizer.Add(self.switext, 1, wx.ALL, 5)
        swi_sizer.Add(self.swicombobox, 1, wx.ALL, 5)
        swi_sizer.Add(self.switch1_button, 1, wx.ALL, 5)
        sm_sizer.Add(swi_sizer,1,wx.ALL,5)

        sig_sizer.Add(self.sigtext, 1, wx.ALL, 5)
        sig_sizer.Add(self.sigcombobox, 1, wx.ALL, 5)
        sig_sizer.Add(self.set_monitor_button, 1, wx.ALL, 5)
        sm_sizer.Add(sig_sizer,1,wx.ALL,5)

        mon_sizer.Add(self.montext, 1, wx.ALL, 5)
        mon_sizer.Add(self.moncombobox, 1, wx.ALL, 5)
        mon_sizer.Add(self.zap_monitor_button, 1, wx.ALL, 5)
        sm_sizer.Add(mon_sizer,1,wx.ALL,5)

        side_sizer.Add(sm_sizer,1,wx.ALL,5)
        """
        onoff_sizer.Add(self.switch1_button)
        onoff_sizer.Add(self.switch0_button)
        
        smgrid_sizer.AddMany([self.switext, self.swicombobox, onoff_sizer,
                          self.sigtext, self.sigcombobox, self.set_monitor_button,
                          self.montext, self.moncombobox, self.zap_monitor_button])
        #side_sizer.Add(smgrid_sizer,1,wx.ALL,5)
        sm_sizer.Add(smgrid_sizer,1,wx.ALL,5)
        side_sizer.Add(sm_sizer,1,wx.ALL,5)


        helpquit_sizer.Add(self.help_button)
        helpquit_sizer.Add(self.quit_button)

        side_sizer.Add(helpquit_sizer)
        #side_sizer.Add(self.help_button, 1, wx.ALL, 5)
        #side_sizer.Add(self.quit_button, 1, wx.ALL, 5)
        #side_sizer.Add(self.switch0_button, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)


        #Added from userint
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.cycles_completed = 0
        self.switch_id = None
        self.signal_id = None
        self.monitor_id = None
        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position


    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_About:
            wx.MessageBox("Select the number of cycles then either\nrun a new simulation or continue\nthe current simulation.",
                          "Running Simmulations", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_Switches_Monitors:
            wx.MessageBox("To alter a switch's state, select it from\nthe drop-down menu and toggle the On/Off button.\nTo add a monitor, select a signal from the drop-down\nmenu and press the Monitor button.\nTo delete a monitor, select a monitor from the\ndrop-down menu and press the zap button.",
                          "Running Simmulations", wx.ICON_INFORMATION | wx.OK)

        
    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "".join(["Run button pressed. Should run for:", str(self.spin.GetValue())])
        self.canvas.render(text)
        self.run_command()

    def run_command(self):
        #Run the simulation for scratch
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        if cycles is not None:
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def run_network(self, cycles):
        #run simulation for set nmuber cycles
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillation.")
                return False
        self.monitors.display_signals()
        return True


    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        self.canvas.render(text)
        self.continue_command()
    
    def continue_command(self):
        #Continue a previously run simulation
        cycles = self.spin.GetValue()
        if cycles is not None:
            if self.cycles_completed == 0:
                print("Error! Nothing to contiue")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))


    def on_switch1_button(self, event):
        """Handle the event when the user clicks the switch1 button."""
        text = "On switch button pressed."
        self.canvas.render(text)
        self.switch1_command(1)
    
    def on_switch0_button(self, event):
        """Handle the event when the user clicks the switch0 button."""
        text = "Off switch button pressed."
        self.canvas.render(text)
        self.switch0_command(1)


    def switch1_command(self, state):
        #set the specified switch to the specified signal level
        if self.switch_id == None:
            print("Please select a switch")
        else:
            print(self.switch_id)
            self.devices.set_switch(self.names.query(self.switch_id), 1)
            print("Successfully set switch.")

    def switch0_command(self, state):
        #set the specified switch to the specified signal level
        if self.switch_id == None:
            print("Please select a switch")
        else:
            print(self.switch_id)
            self.devices.set_switch(self.names.query(self.switch_id), 0)
            print("Successfully reset switch.")

    def on_swicombobox(self, event):
        """Handle the event when the user selects a switch."""
        self.switch_id = self.swicombobox.GetValue()
        text = "".join(["New switch selection: ", self.switch_id])
        self.canvas.render(text)
        print(self.switch_id)
    
    def on_sigcombobox(self, event):
        """Handle the event when the user selects a signal."""
        self.signal_id = self.sigcombobox.GetValue()
        text = "".join(["New signal selection: ", self.signal_id])
        self.canvas.render(text)
        print(self.signal_id)
    
    def on_moncombobox(self, event):
        """Handle the event when the user selects a monitor."""
        self.monitor_id = self.moncombobox.GetValue()
        text = "".join(["New monitor selection: ", self.monitor_id])
        self.canvas.render(text)
        print(self.monitor_id)


    def on_set_monitor_button(self, event):
        """Handle the event when the user clicks the set_monitor button."""
        text = "Set Monitor button pressed."
        self.canvas.render(text)
        self.monitor_command()
    
    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.names.query(self.signal_id)
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.names.query(self.signal_id)
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]
    
    def read_monitor_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.names.query(self.monitor_id)
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.names.query(self.monitor_id)
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]
    
    def monitor_command(self):
        print(self)
        monitor = self.read_signal_name()
        if monitor == None:
            print("Please select a device to monitor")
        else:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")


    def on_zap_monitor_button(self, event):
        """Handle the event when the user clicks the zap_monitor button."""
        text = "zap_monitor button pressed."
        self.canvas.render(text)
        self.zap_command()
    
    def zap_command(self):
        monitor = self.read_monitor_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")

    def on_quit_button(self, event):
        """Handle the event when the user clicks the quit button."""
        text = "quit button pressed."
        self.canvas.render(text)
        sys.exit()
