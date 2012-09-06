import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from main import *

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        self.isset_credentials = False

        QMainWindow.__init__(self, parent)
        self.setWindowTitle('MBox')

        self.create_menu()
        self.create_status_bar()
        self._init_frames()
        self.create_main_frame()

    def _init_frames(self):
        ####################### Main Frame ############################

        self.main_frame = QWidget()
        self.main_frame_box = QVBoxLayout()

        self.start_sync = QPushButton("&Start Sync")
        QObject.connect( self.start_sync, SIGNAL("clicked()"), self.sync )

        self.main_frame.setLayout(self.main_frame_box)

        ###################### Login Frame ###########################

        self.login_frame = QWidget()
        vbox = QVBoxLayout()

        # Login Credentials :: Group Box 
        qg = QGroupBox("Login Credentials")
        qvbox = QGridLayout()
        
        # Fields
        
        ulabel = QLabel("Username:")
        plabel = QLabel("Password:")

        self.username_tb = QLineEdit()
        self.username_tb.setMinimumWidth(200)
        self.password_tb = QLineEdit()
        self.password_tb.setEchoMode(QLineEdit.Password)
        self.password_tb.setMinimumWidth(200)
        
        self.save_credentials = QCheckBox("Remember Me")
        self.save_settings = QPushButton("&Login")
        QObject.connect( self.save_settings, SIGNAL("clicked()"), self.save)

        qvbox.addWidget(ulabel,0,0)
        qvbox.addWidget(self.username_tb,0,1)
        qvbox.addWidget(plabel,1,0)
        qvbox.addWidget(self.password_tb,1,1)
        qvbox.addWidget(self.save_credentials,2,1)
        qvbox.addWidget(self.save_settings,3,1)

        qg.setLayout(qvbox)
        vbox.addWidget(qg)

        self.login_frame.setLayout(vbox)
        

    def on_about(self):
        msg = """ MBox v0.1

         * Mbox is used to sync files from moodle
         * Set your username and password 
         * Next select the folders to be synced
         * Voila :) 
        """
        QMessageBox.about(self, "MBox v0.1", msg.strip())

    def get_login(self):
        self.main_frame.hide()
        self.setCentralWidget(self.login_frame)
        self.login_frame.show()

    def create_main_frame(self):
        try:
            if not self.isset_credentials:
                print "Trying to load credentials from past"
                f = open("./.msync","r")
                contents = f.read()
                self.u,self.p = contents.split('|')
        except:
            print "Failed to load credentials :: Loading login frame"
            self.get_login()
            return
        
        print "Loading Main Frame"
        self.sync_handler = Sync(self.u,self.p)
        if not self.sync_handler.logged_in:
            print "Login Failed :: Try again"
            return 

        self.login_frame.hide()
        courses_list =self.sync_handler.listCourses()
        print courses_list
        try:
            f = open("./.selected_list","r")
            selected_list = f.read().split("|")
        except:
            selected_list = []
        
        print "Selected List" 
        print selected_list
        self.checkboxes = []
        model = QStandardItemModel()
        for item in courses_list:
            cb = QStandardItem(item)
            check = Qt.Checked if item in selected_list else Qt.Unchecked
            cb.setCheckState(check)
            cb.setCheckable(True)
            self.checkboxes.append(cb)
            model.appendRow(cb)

        view = QListView()
        view.setModel(model)
        self.main_frame_box.addWidget(view)

        self.pdfGet = QCheckBox("Get PDFs as well")
        self.pdfGet.setCheckState(Qt.Checked)
        self.pdfGet.setCheckable(True)
        self.setCentralWidget(self.main_frame)
        self.main_frame_box.addWidget(self.pdfGet)
        self.main_frame_box.addWidget(self.start_sync)
        self.main_frame.show()

    def save(self):
        print "Adding Credentials"
        u = self.username_tb.text()
        p = self.password_tb.text()
        print u,p
        if self.save_credentials.isChecked():
            print "Saving Credentials"
            f = open("./.msync","w")
            f.write("%s|%s" % (u,p))
            f.close()

        self.isset_credentials = True
        self.u = u
        self.p = p
        self.create_main_frame()
    
    def sync(self):
        checklist = []
        for box in self.checkboxes:
            if box.checkState() == Qt.Checked:
                checklist.append(str(box.text()))
        
        print checklist
        f = open("./.selected_list","w")
        f.write("|".join(checklist))
        f.close()
        folderNames={}
        for i in checklist:
            folderNames[i]=i
        self.sync_handler.syncCourses(checklist,folderNames,(self.pdfGet.checkState()==Qt.Checked))
        print "Completed GUI"

    def create_status_bar(self):
        self.status_text = QLabel("Idle")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")

        settings_action = self.create_action("&Settings", slot=self.get_login, 
            shortcut="Ctrl+S", tip="Configure MBox")

        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, (settings_action,quit_action,))
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
    del form
