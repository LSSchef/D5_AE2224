import sys
import vallenae as vae
import os
import math
import pyqtgraph as pg
from PySide6.QtGui import QColor
from PySide6.QtCore import *
from PySide6.QtWidgets import *
import yaml
from scipy.fft import fft, fftfreq
import numpy as np

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        try:
            with open('settings.yml', 'r') as file:
                results = yaml.safe_load(file)
            self._tradb_file_location = results['tradb']
            self._pridb_file_location = results['pridb']
        except FileNotFoundError:
            with open('settings.yml', 'w') as file:
                databases = {
                    'tradb': None,
                    'pridb': None
                }
                yaml.dump(databases, file, sort_keys=False)
                self._tradb_file_location = None
                self._pridb_file_location = None


        # Create widgets
        self.create_bunch_of_stuff()
        self.create_empty_table()
        self.create_db_selector()      
        self.create_enter_trai()
        self.create_left_side()
        self.style_graph()
        self.style_freq_graph()
        self.style_count_graph()

        # Create a layout for frequency plot
        self.freq_layout = QVBoxLayout()
        self.freq_layout.setContentsMargins(0, 0, 0, 0)
        
        self.count_layout = QVBoxLayout()
        self.count_layout.setContentsMargins(0,0,0,0)
        
        

        # Create main layout
        main_layout = QGridLayout()
        main_layout.addWidget(self._database_select, 0, 0, 1, 4)
        #self.graph_grid = QGridLayout()
        main_layout.addLayout(self.graph_grid, 1, 1,1,3)
        main_layout.addWidget(self._left_side, 1, 0,1,1)
        main_layout.setColumnStretch(0, 0)
        main_layout.setColumnStretch(1, 20)

        # Set dialog layout
        self.setLayout(main_layout)

        # Add button signal to greetings slot
        self.button.clicked.connect(self.calculate_trai)
        self._open_tradb_button.clicked.connect(self.set_open_tradb)
        self._open_pridb_button.clicked.connect(self.set_open_pridb)

    def create_bunch_of_stuff(self):
        frame_style = QFrame.Sunken | QFrame.Panel
        self.graph_grid = QGridLayout()
        self.edit = QLineEdit()
        self.button = QPushButton("Show TRAI")
        self.table = QTableWidget()
        self.graph = pg.PlotWidget()
        self.freq_graph = pg.PlotWidget()
        self.count_graph = pg.PlotWidget()
        self._open_tradb_label = QLabel()
        self._open_tradb_label.setText(self._tradb_file_location)
        self._open_tradb_label.setFrameStyle(frame_style)
        self._open_tradb_button = QPushButton("Select tradb file")
        self._open_pridb_label = QLabel()
        self._open_pridb_label.setText(self._pridb_file_location)
        self._open_pridb_label.setFrameStyle(frame_style)
        self._open_pridb_button = QPushButton("Select pridb file")

    def create_empty_table(self):
        self.data = ["time", "channel", "param id", "amplitude", "duration", "energy", "rms", "set id", "threshold", "rise time", "signal strength", "counts", "variance E10", "Counts/log(RT e4)"]
        unit = ["s", "-", "-", "µV", "s", "eu", "µV", "-", "µV", "µs", "nVs", "-", "µV2", "N/dB"]
        self.table.setRowCount(14)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Data", "Value", "Unit"])
        self.table.setFixedWidth(350)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for (i, name) in enumerate(self.data):
            data_str = QTableWidgetItem(name)
            self.table.setItem(i, 0, data_str)
        for (i, unit) in enumerate(unit):
            unit_str = QTableWidgetItem(unit)
            self.table.setItem(i, 2, unit_str)

    def create_db_selector(self):
        self.create_pridb_box()
        self.create_tradb_box()
        self._database_select = QGroupBox("Select database files")
        layout = QHBoxLayout()
        layout.addWidget(self._pridb_box)
        layout.addWidget(self._tradb_box)
        self._database_select.setLayout(layout)

    def create_pridb_box(self):
        self._pridb_box = QGroupBox("")
        layout = QVBoxLayout()
        layout.addWidget(self._open_pridb_button)
        layout.addWidget(self._open_pridb_label)
        self._pridb_box.setLayout(layout)

    def create_tradb_box(self):
        self._tradb_box = QGroupBox("")
        layout = QVBoxLayout()
        layout.addWidget(self._open_tradb_button)
        layout.addWidget(self._open_tradb_label)
        self._tradb_box.setLayout(layout)

    def create_enter_trai(self):
        self._enter_trai = QGroupBox("Enter TRAI")
        layout = QHBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self._enter_trai.setLayout(layout)
        self._enter_trai.setFixedWidth(350)

    def create_left_side(self):
        self._left_side = QGroupBox()
        layout = QVBoxLayout()
        layout.addWidget(self._enter_trai)
        layout.addWidget(self.table)
        self._left_side.setLayout(layout)

    def style_graph(self):
        self.graph.setBackground('w')
        self.pen_main = pg.mkPen(color=(0, 0, 255))
        self.pen_treshold = pg.mkPen(color=(255,0,0), style=Qt.DashLine)
        self.graph.setTitle("Amplitude VS Time", color=(255,0,0), size="20px")
        self.graph.setLabel('left', "<font color='blue'>Amplitude", "V")
        self.graph.setLabel('bottom', "<font color='blue'>Time", "s")
        self.graph.showGrid(x=True, y=True)
        self.graph_grid.addWidget(self.graph,0,0)
        
    def style_freq_graph(self):
        self.freq_graph.setBackground('w')
        self.freq_graph.setTitle("Amplitude VS Frequency", color=(255,0,0), size="20px")
        self.freq_graph.setLabel('left', "<font color='blue'>Amplitude", "V")
        self.freq_graph.setLabel('bottom', "<font color='blue'>Frequency", "Hz")
        self.freq_graph.showGrid(x=True, y=True)
        self.graph_grid.addWidget(self.freq_graph,0,1)
        
    def style_count_graph(self):
        self.count_graph.setBackground('w')
        self.count_graph.setTitle("Count VS Time", color=(255,0,0), size="20px")
        self.count_graph.setLabel('left', "<font color='blue'>Count", "-")
        self.count_graph.setLabel('bottom', "<font color='blue'>Time", "s")
        self.count_graph.showGrid(x=True, y=True)
        self.graph_grid.addWidget(self.count_graph,0,2)
        
    def convert_to_db(self, x):
        self.graph.setLabel('left', "<font color='blue'>Amplitude", "dBV")
        for i in range(len(x)):
            try:
                x[i] = 20*math.log(x[i]/1e-6, 10)
            except ValueError:
                x[i] = -100
        return x

    # Calculates parameters
    @Slot()
    def calculate_trai(self):
        PRIDB = self._pridb_file_location
        TRADB = self._tradb_file_location
        trai = int(self.edit.text())
        cum_counts = []
        with vae.io.TraDatabase(TRADB) as tradb:
            y, t = tradb.read_wave(trai)
            data_idk = tradb.iread(trai=trai)
            for data in data_idk:
                treshold = data[4]
            max_amplitude = max(np.abs(y))
            i = 0
            for j in range(len(y)):
                if y[j] >= treshold and y[j-1] < treshold:
                    i += 1
                cum_counts.append(i)
                
            #print(tradb.columns())
        
        self.graph.clear()  
        self.graph.setTitle(f"Amplitude VS Time, TRAI={trai}", color=(255,0,0), size="20px")

        #calculate a scaled, rounded variance of each waveform
        scaled_var = np.var(y)*10**10
        data_value_widget = QTableWidgetItem(str(round(scaled_var,2)))
        #print(data_value_widget)
        self.table.setItem(12, 1, data_value_widget)
        
        pridb = vae.io.PriDatabase(PRIDB)
        df_hits = pridb.iread_hits(query_filter=f"TRAI = {trai}")
        #print(pridb.columns())
        #print(pridb.fieldinfo())
        self.data_array = dict()
        for i in df_hits:
            for (index, data_value) in enumerate(i[0:12]):
                self.data_array[self.data[index]] = data_value
                data_value_widget = QTableWidgetItem()
                data_value_widget.setData(Qt.DisplayRole, data_value)
                self.table.setItem(index, 1, data_value_widget)
                if index == 8: 
                    self.graph.addLegend()
                    self.graph.plot(t, y, pen=self.pen_main,name="data", symbol="o",symbolSize=4)
                    self.graph.plot(t, len(t)*[data_value], pen=self.pen_treshold, name="treshold")
                    self.graph.plot(t, len(t)*[-data_value], pen=self.pen_treshold)
            
            # ignore waves with count 1 to avoid infinitely small rise times
            if i[11] > 1:
                CountsoverlogRiseTime = i[11]/np.log10(i[9]/10**(-8))
            else:
                CountsoverlogRiseTime = 0
            data_value_widget = QTableWidgetItem(str(round(CountsoverlogRiseTime,5)))
            self.table.setItem(13, 1, data_value_widget)
            self.data_array[self.data[12]] = scaled_var
            self.data_array[self.data[13]] = CountsoverlogRiseTime
        
        #print(self.data_array)
        data_str = QTableWidgetItem(str(max_amplitude))
        self.table.setItem(3, 1, data_str)
        
        yf = fft(y)
        dt = t[1] - t[0]
        freq = fftfreq(len(y), dt)
        freq_0 = []
        amplitude_spectrum_0 = []
        amplitude_spectrum = 2*np.abs(yf)
        for i in range(len(freq)):
            if freq[i] >= 0:
                freq_0.append(freq[i])
                amplitude_spectrum_0.append(amplitude_spectrum[i])
                
        yf = fft(y)
        xf = fftfreq(len(t), dt)[:len(t)//2]
        freq_0 = xf
        amplitude_spectrum_0 = 2.0/len(t) * np.abs(yf[0:len(t)//2])

        # Create a new PlotWidget for frequency plot
        self.freq_graph.clear()
        
        self.freq_graph.plot(freq_0, amplitude_spectrum_0, pen=self.pen_main)
        self.freq_graph.addLegend()
        
        self.count_graph.clear()
        self.count_graph.plot(t, cum_counts, pen=self.pen_main)
        self.count_graph.addLegend()

        # # Clear the layout and add the frequency PlotWidget
        # for i in reversed(range(self.freq_layout.count())): 
        #     self.freq_layout.itemAt(i).widget().setParent(None) 
        # self.freq_layout.addWidget(self.freq_graph)
        
        # for i in reversed(range(self.count_layout.count())): 
        #     self.count_layout.itemAt(i).widget().setParent(None) 
        # self.count_layout.addWidget(self.count_graph)

        # Refresh the main layout
        #self.graph_grid.addWidget(self.count_graph, 0, 1)
        #self.graph_grid.addWidget(self.freq_graph, 0, 2)

    @Slot()
    def set_open_tradb(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select tradb file",
                                                  self._open_tradb_label.text(),
                                                  "Tradb (*.tradb)", "")
        if fileName:
            self._open_tradb_label.setText(fileName)
        self._tradb_file_location = fileName
        with open('settings.yml', 'w') as file:
            databases = {
                'tradb': self._tradb_file_location,
                'pridb': self._pridb_file_location
            }
            yaml.dump(databases, file, sort_keys=False)

    @Slot()
    def set_open_pridb(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select pridb file",
                                                  self._open_tradb_label.text(),
                                                  "Pridb (*.pridb)", "")
        if fileName:
            self._open_pridb_label.setText(fileName)
        self._pridb_file_location = fileName
        with open('settings.yml', 'w') as file:
            databases = {
                'tradb': self._tradb_file_location,
                'pridb': self._pridb_file_location
            }
            yaml.dump(databases, file, sort_keys=False)

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form 
    form = Form()
    form.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
    form.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
    form.setWindowTitle("VAEsualizer")
    form.show()
    
    # Run the main Qt loop
    sys.exit(app.exec())
