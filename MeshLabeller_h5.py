import sys
import vtk
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtWidgets import QShortcut ,  QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import csv
import json
import os
import trimesh
import meshparty
from meshparty import trimesh_io, trimesh_vtk
import h5py
import numpy as np
import argschema

class MeshLabellerArgs(argschema.ArgSchema):
    mesh_dir = argschema.InputDir(default = "data/meshes", description="path to folder with [ID].h5 files")
    label_dir = argschema.InputDir(description= "path with folder of ID.h5 files with binary mask dataset")
    id_csv = argschema.InputFile(default = "data/ids.csv", description="path to csv of ids,prelabel file")
    output_file = argschema.OutputFile(default = "output.json", description= "path to save outptut json")
    hotkey_file = argschema.InputFile(default = "data/hotkeys.csv", description = "file with hotkeys")
    opacity = argschema.fields.Float(default=.5, description = "opacity of meshes")

class MyQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    def __init__(self, *args, **kwargs):
        rw = vtk.vtkRenderWindow()
        rw.SetStereoCapableWindow(False)
        rw.StereoRenderOff()
        rw.SetStereoTypeToCrystalEyes()
        super(MyQVTKRenderWindowInteractor, self).__init__(*args,rw=rw, **kwargs)


class MainWindow(Qt.QMainWindow):
    def __init__(self, parent = None,
                       mesh_dir = "data/meshes",
                       label_dir = "", 
                       id_csv = "data/ids.csv",
                       output_file = "output.json",
                       hotkey_file = "data/hotkeys.csv",
                       opacity = .5):

        self.curId = 0000000
        self.curKeyValue = ''
        self.curIndex = 0
        self.allids = []
        self.hotkeys = []
        self.keylabels = []
        self.curActor = None
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
        self.add_title_left('mesh_labels',4,0)
        self.add_title_left('Hot Key File (CSV):',5,0)
        self.add_title_left('Mesh Opacity',6,0)
        self.meshdirectoryline = self.add_editor(mesh_dir,1,1,1,1)
        self.idline = self.add_editor(id_csv,2,1,1,1)
        self.outputline = self.add_editor(output_file,3,1,1,1)
        self.labelline =  self.add_editor(label_dir,4,1,1,1)
        self.hotkeyline = self.add_editor(hotkey_file,5,1,1,1)
        
       
        self.opacityline = self.add_editor("0.5",6,1,1,1)
        #self.opacityline.returnPressed.connect(self.testing123())



        self.add_load_button('LOAD',6,1)
        self.add_title('Current Hot Keys:',7,1)
        self.hotkeyvalueline= self.add_title('',8,1)

        self.add_backward_button('<<',9,0)
        self.add_vtk_window(9,1)
        self.add_forward_button('>>',9,2)

        self.filenameline = self.add_title('DEFAULT',10,1)
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
                 del self.LABELS[self.curId]
                 if self.curIndex < len(self.allids)-1:
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
        self.curId = self.allids[self.curIndex]
        filename = self.meshdirectoryline.text()+'/'+self.curId+'.h5'
        label_dir = self.labelline.text()
        if len(label_dir)>0:
            label_file = os.path.join(label_dir, self.curId+".h5")
            with h5py.File(label_file, "r") as f:
                labels = np.array(f['mask'])
                print(labels.shape)
        else:
            labels = None
        if self.curId in self.LABELS.keys():
            labeltext = "Current Label = %s"%self.LABELS[self.curId]
        else :
            labeltext = "No Current Label"
        self.filenameline.setText (filename + ", " + labeltext)
        print("this is filename")
        print(filename)
        cvpath='https://storage.googleapis.com/neuroglancer/basil_v0/basil_full/seg-aug'
        mm = trimesh_io.MeshMeta()
        mesh = mm.mesh(filename=filename)
        print(mesh.vertices.shape)
        print(labels.dtype)
        #mesh_poly = trimesh_vtk.trimesh_to_vtk(mesh.vertices, mesh.faces, mesh.mesh_edges)
        #reader = vtk.vtkDataReader()
        #reader.SetFileName(filename)
        #mapper = vtk.vtkPolyDataMapper()
        #mapper.SetInputConnection(mesh_poly.GetOutputPort())

        # Create an actor
        # actor = vtk.vtkActor()
        actor = trimesh_vtk.mesh_actor(mesh, vertex_colors=labels.astype(np.float64), opacity=float(self.opacityline.text()))
        if self.curId in self.LABELS.keys():
            actor.GetProperty().SetColor(0.5, 0.5, 0.0)
        else:
            actor.GetProperty().SetColor(0.0, 0.5, 0.5)
        # actor.GetProperty().SetOpacity(float(self.opacityline.text()))
        # actor.SetMapper(mapper)
        

        #render
        self.ren.RemoveActor(self.curActor)
        self.curActor = actor
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        cam1 = self.ren.GetActiveCamera()
        cam1.Zoom(1.4)
        self.ren.SetBackground((1.0,1.0,1.0))
        self.iren.Initialize()
        self.iren.Start()

    def add_vtk_window(self,x,y,w=1,h=1):
        def vtkKeyPress(obj, event):
            key = obj.GetKeySym()
            self.curKeyValue = key
            if key in self.hotkeys:
                add_annotation_and_advance(self)
            return

        self.vtkWidget = MyQVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget, x,y,w,h)
        self.vtkWidget.GetRenderWindow().SetStereoCapableWindow(False)
        self.vtkWidget.GetRenderWindow().StereoRenderOff()
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
        self.curActor = actor

        #renderse
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.iren.AddObserver("KeyPressEvent", vtkKeyPress)

        self.iren.Initialize()
        self.iren.Start()

def on_load_button_clicked(self):
    self.curIndex = 0
    self.allids = load_ids(self.idline.text())
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
    if self.curIndex < len(self.allids)-1:
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

def load_ids(filename):
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        ids = []
        labels = []
        for row in readCSV:
            ids.append(row[0])

    return ids[1:]

def add_annotation_and_advance(self):
    #This uses a dict which means that you can overwrite the value by going back and forth
    self.LABELS.update( {self.curId : self.curKeyValue} )
    print(self.LABELS)
    print(self.LABELS.keys())
    print(self.LABELS.values())
    if self.curIndex < len(self.allids)-1:
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
    mod = argschema.ArgSchemaParser(schema_type = MeshLabellerArgs)
    mod.args.pop('log_level')
    mod.args.pop('input_json')
    app = Qt.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow(**mod.args)
    sys.exit(app.exec_())
