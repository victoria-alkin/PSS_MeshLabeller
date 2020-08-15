import sys
import vtk
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtWidgets import QShortcut ,  QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import csv
import json
import os
import pickle
import pandas as pd
import trimesh
import meshparty
from meshparty import trimesh_io, trimesh_vtk

class MainWindow(Qt.QMainWindow):
    def __init__(self, parent = None):

        self.curId = 0000000
        self.curKeyValue = ''
        self.curIndex = 0
        self.hotkeys = []
        self.keylabels = []
        self.curActor1 = None
        self.curActor2 = None
        self.meshopacity = 0.5

        #self.LABELS = [[],[]]
        self.LABELS={}
        #inits
        Qt.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Mesh Labeller')
        self.frame = Qt.QFrame()

        #define layout`
        self.vl = Qt.QGridLayout()
        self.vl.setSpacing(10)

        self.add_title_left('Mesh File Directory:',1,0)
        self.add_title_left('CSV for ids:',2,0)
        self.add_title_left('Output File:',3,0)
        self.add_title_left('Hot Key File (CSV):',4,0)
        self.add_title_left('Mesh Opacity',5,0)
        self.meshdirectoryline = self.add_editor("data/meshes/EXPT1",1,1,1,1)
        self.dataframe_filename = self.add_editor(r"V3_labeled.pkl",2,1,1,1)
        self.outputline = self.add_editor("output.json",3,1,1,1)
        self.hotkeyline = self.add_editor("data/hotkeys.csv",4,1,1,1)
        self.opacityline = self.add_editor("0.5",5,1,1,1)
        #self.opacityline.returnPressed.connect(self.testing123())



        self.add_load_button('LOAD',6,1)
        self.add_title('Current Hot Keys:',7,1)
        self.hotkeyvalueline= self.add_title('',8,1)

        self.add_backward_button('<<',9,0)
        self.add_vtk_window(9,1)
        self.add_forward_button('>>',9,2)

        #self.filenameline = self.add_title('DEFAULT',10,1)
        self.filenameline = self.add_editor_center("DEFAULT",10,1)
        self.add_button('Continue Labelling',11,1)
        self.add_save_button('SAVE!',12,1)
        self.add_help_button('HELP',13,2)

        #set layout for frame
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        self.show()



    def keyPressEvent(self, event):
         if type(event) == QtGui.QKeyEvent:
             #here accept the event and do something
             print (event.text())

             self.curKeyValue = event.text()
             if event.text() == "d":
                 del self.LABELS[self.curUniqueId]
                 if self.curIndex < self.df.shape[0]-1:
                     self.curIndex +=1
                     self.set_vtk_window()
                 else:
                     print("This is the last mesh. Please save your work!")
             if event.text() == "ENTER":
                 set_vtk_window()
             if event.text() in self.hotkeys:
                add_annotation_and_advance(self)
             event.accept()
         else:
             event.ignore()

    def add_title_left(self,string,x,y,w=1,h=1):

        label = QLabel(string)
        label.setAlignment(QtCore.Qt.AlignLeft)
        self.vl.addWidget(label,x,y,w,h)

    def add_title(self,string,x,y,w=1,h=1):

        label = QLabel(string)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.vl.addWidget(label,x,y,w,h)
        return label

    def add_editor(self,str,x,y,w=1,h=1):
        line = QLineEdit(str)
        self.vl.addWidget(line, x,y,w,h)
        return line

    def add_editor_center(self,str,x,y,w=1,h=1):
        line = QLineEdit(str)
        line.setAlignment(QtCore.Qt.AlignCenter)
        self.vl.addWidget(line, x,y,w,h)
        return line

    def add_button(self,string,x,y,w=1,h=1):
            mybutton = QPushButton(string)
            self.vl.addWidget(mybutton, x,y,w,h)



    def add_forward_button(self,string,x,y,w=1,h=1):
            mybutton = QPushButton(string)
            mybutton.clicked.connect(lambda:on_forward_button_clicked(self))
            self.vl.addWidget(mybutton, x,y,w,h)

    def add_backward_button(self,string,x,y,w=1,h=1):
            mybutton = QPushButton(string)
            mybutton.clicked.connect(lambda:on_backward_button_clicked(self))
            self.vl.addWidget(mybutton, x,y,w,h)

    def add_help_button(self,string,x,y,w=1,h=1):
            mybutton = QPushButton(string)
            mybutton.clicked.connect(lambda:on_help_button_clicked(self))
            self.vl.addWidget(mybutton, x,y,w,h)

    def add_load_button(self,string,x,y,w=1,h=1):
        mybutton = QPushButton(string)
        #mybutton.clicked.connect(on_load_button_clicked())
        mybutton.clicked.connect(lambda:on_load_button_clicked(self))
        self.vl.addWidget(mybutton, x,y,w,h)

    def add_save_button(self,string,x,y,w=1,h=1):
            mybutton = QPushButton(string)
            mybutton.clicked.connect(lambda:on_save_button_clicked(self))
            self.vl.addWidget(mybutton, x,y,w,h)

    def set_vtk_window(self):      
        self.curId = get_filename(self)
        filename_local = self.meshdirectoryline.text()+'/'+self.curId+'/'+'locmesh_' + self.curFilenumber + '.off'
        filename_spine = self.meshdirectoryline.text()+'/'+self.curId+'/'+'spine_' + self.curFilenumber + '.off'
        self.curUniqueId = self.curId + '_' + self.curFilenumber
        if self.curUniqueId in self.LABELS.keys():
            labeltext = "Current Label = %s"%self.LABELS[self.curUniqueId][0]
        else :
            labeltext = "No Current Label"
        currentIndex = "Current Index: " + str(self.curIndex)
        self.filenameline.setText (filename_local + ", " + filename_spine + ", " + labeltext + ", " + currentIndex)
        print("this is filename")
        print(filename_local + ", " + filename_spine)
        
        # Create an actor for local mesh
        local_mesh = trimesh.exchange.load.load_mesh(filename_local)
        actor_local = trimesh_vtk.mesh_actor(local_mesh)
        if self.curUniqueId in self.LABELS.keys():
            actor_local.GetProperty().SetColor(0.0, 0.8, 0.0)
        else:
            actor_local.GetProperty().SetColor(1.0, 0.0, 0.0)
        actor_local.GetProperty().SetOpacity(float(self.opacityline.text()))
        print(actor_local.GetProperty().GetColor())

        # Create an actor for spine mesh
        spine_mesh = trimesh.exchange.load.load_mesh(filename_spine)
        actor_spine = trimesh_vtk.mesh_actor(spine_mesh)
        if self.curUniqueId in self.LABELS.keys():
            actor_spine.GetProperty().SetColor(1.0, 0.0, 0.0)
        else:
            actor_spine.GetProperty().SetColor(0.0, 1.0, 0.0)
        actor_spine.GetProperty().SetOpacity(float(self.opacityline.text()))
        print(actor_spine.GetProperty().GetColor())

        #render
        self.ren.RemoveActor(self.curActor1)
        self.ren.RemoveActor(self.curActor2)
        self.curActor1 = actor_local
        self.curActor2 = actor_spine
        self.ren.AddActor(actor_local)
        self.ren.AddActor(actor_spine)
        self.ren.ResetCamera()
        self.ren.SetBackground((.1,.1,.1))
        self.iren.Initialize()
        self.iren.Start()

    def add_vtk_window(self,x,y,w=1,h=1):
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget, x,y,w,h)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.curActor1 = actor

        #render
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.iren.Initialize()
        self.iren.Start()

def on_load_button_clicked(self):
    self.curIndex = 0
    self.df = load_filenames(self.dataframe_filename.text())
  
    self.hotkeys,self.keyvalues = load_HotKeys(self.hotkeyline.text())
    hkv_str = ''
    for i in range(0,len(self.hotkeys)):
        hkv_str = hkv_str +  "%s - %s ; "%(self.hotkeys[i], self.keyvalues[i])

    self.hotkeyvalueline.setText (hkv_str[:-2])


    outfile = self.outputline.text()
    if os.path.exists(outfile):
        load_labels(self,outfile)
        print (self.LABELS)
    print("Labels Activated!")
    self.set_vtk_window()

def setKeyValue(self,kv):
    self.curKeyValue = kv

def on_forward_button_clicked(self):
    if self.curIndex < self.df.shape[0]-1:
        self.curIndex +=1
        self.set_vtk_window()
    else:
        print("This is the last mesh. Please save your work!")
    #self.curIndex +=1
    #self.set_vtk_window()

def on_backward_button_clicked(self):
    if self.curIndex > 0 :
        self.curIndex -= 1
        self.set_vtk_window()
    else:
        print("This is the first mesh!")

def on_save_button_clicked(self):
    outfilename = self.outputline.text()
    with open(outfilename, 'w') as fp:
        json.dump(self.LABELS ,fp)
    print("LABELS: ",  self.LABELS)
    for key in self.LABELS:
        # self.LABELS[key][0] - label
        # self.LABELS[key][1] - index in dataframe
        self.df.iloc[self.LABELS[key][1], 4] = self.LABELS[key][0]
    # write down data frame in pickle file
    self.df.to_csv(r"labels.csv")
    labels_file = open(r"labels.pkl","wb")
    pickle.dump(self.df, labels_file)
    labels_file.close()
    #with open(r"labels.pkl","ab") as fpickle:
    #    pickle.dump(self.df, fpickle)

def on_help_button_clicked(self):
    showhelpdialog(self)

def load_HotKeys(filename):
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        keys = []
        keyvalues = []
        for row in readCSV:
            keys.append(row[0])
            keyvalues.append(row[1])
    return keys,keyvalues

def load_labels(self,filename):
    if filename:
        with open(filename, 'r') as f:
            self.LABELS = json.load(f)

def load_filenames(filename):
    v3features_file = open(filename,"rb")
    v3features_db = pickle.load(v3features_file)
    v3features_file.close()
    v3features_df = pd.DataFrame(v3features_db)
    return v3features_df

def get_filename(self):
    full_path = self.df.iloc[self.curIndex,3]
    start = full_path.find("EXPT1/")
    end = full_path.find("/spine")
    end2 = full_path.find("_ae_model")
    curId = full_path[start+6 : end]
    self.curFilenumber = full_path[end+7 : end2]
    return curId

def add_annotation_and_advance(self):
    #This uses a dict which means that you can overwrite the value by going back and forth
    self.LABELS.update( {self.curUniqueId : [self.curKeyValue, self.curIndex]} )
    print(self.LABELS)
    print(self.LABELS.keys())
    print(self.LABELS.values())
    if self.curIndex < self.df.shape[0]-1:
        self.curIndex +=1
        self.set_vtk_window()
    else:
        print("This is the last mesh. Please save your work!")

def showhelpdialog(self):
   msg = QMessageBox()

   helptext = ''
   helptext = helptext + 'Meshlabeller Shortcuts: \n'
   helptext = helptext + 'd : delete label \n'
   helptext = helptext + 'arrow keys : next or previous images \n'

   helptext = helptext + '\n\n'
   helptext = helptext + 'VTK Window Shortcuts: \n'
   helptext = helptext + 'j : joystick mode \n'
   helptext = helptext + 't : mouse mode \n'
   helptext = helptext + '3 : purple \n'
   helptext = helptext + 'w : wireframe \n'
   helptext = helptext + 's : wireframe \n'




   msg.setText("Mesh Labeller Hot keys Information")
   msg.setInformativeText(helptext)
   msg.setWindowTitle("Mesh Labeller HELP ")

   msg.setStandardButtons(QMessageBox.Ok )


   retval = msg.exec_()
   #print ("value of pressed message box button:", retval)

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    sys.exit(app.exec_())
