import sys,os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from main import Sync

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        self.isset_credentials = False
        self.sync = Sync()

        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Moodle Sync')
        self.setWindowIcon(QIcon('moodle.png'))   
        self.create_menu()
        self.create_status_bar()
        self._init_frames()
        self.show_login_frame()

        self.logged_in = False

    def _init_frames(self):
        self.login_frame = QWidget()
        self.main_frame = QWidget()

        ###################### Login Frame ###########################
        vbox = QVBoxLayout()

        viewer = QLabel()
        viewer.setPixmap(QPixmap(os.getcwd() + "/moodle_large.png"))

        # Login Credentials :: Group Box
        qg = QGroupBox("Enter your login credentials :")
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
        self.login_button = QPushButton("&Login")


        qvbox.addWidget(ulabel,0,0)
        qvbox.addWidget(self.username_tb,0,1)
        qvbox.addWidget(plabel,1,0)
        qvbox.addWidget(self.password_tb,1,1)
        qvbox.addWidget(self.save_credentials,2,1)
        qvbox.addWidget(self.login_button,3,1)

        qg.setLayout(qvbox)
        vbox.addWidget(viewer)
        vbox.addWidget(qg)

        self.login_frame.setLayout(vbox)

        self.connect( self.login_button, SIGNAL("clicked()"), self.initiate_login)

        ####################### Main Frame ###############################
        self.main_frame_box = QVBoxLayout()

        view = QListView()
        self.model = QStandardItemModel()
        view.setModel(self.model)

        self.start_sync_button = QPushButton("&Start Sync")

        self.pdfGet = QCheckBox("Get PDFs as well")
        self.pdfGet.setCheckState(Qt.Checked)
        self.pdfGet.setCheckable(True)

        self.main_frame_box.addWidget(view)
        self.main_frame_box.addWidget(self.start_sync_button)
        self.main_frame_box.addWidget(self.pdfGet)

        self.main_frame.setLayout(self.main_frame_box)


        self.connect( self.start_sync_button, SIGNAL("clicked()"), self.start_sync )

        ####################### THREAD CONNECTORS ########################
        self.connect(self.sync, SIGNAL("finished()"), self.updateUi)
        self.connect(self.sync, SIGNAL("terminated()"), self.updateUi)
        self.connect(self.sync, SIGNAL("login_status(QString)"), self.login_done)
        self.connect(self.sync, SIGNAL("courses(PyQt_PyObject)"), self.load_courses)
        self.connect(self.sync, SIGNAL("sync_courses(QString)"), self.sync_done)

    def on_about(self):
        msg = """ 
        MBox v0.1

         * Mbox is used to sync files from moodle
         * Set your username and password
         * Next select the folders to be synced
         * Voila :)
        """
        QMessageBox.about(self, "MBox v0.1", msg.strip())

    def updateUi(self):
        self.start_sync_button.setEnabled(True)
        try:
            self.login_button.setEnabled(True)
        except RuntimeError:
            print "No Login button"

    def show_login_frame(self):
        self.main_frame.hide()
        self.setCentralWidget(self.login_frame)
        self.login_frame.show()

        try:
            if not self.isset_credentials:
                print "Trying to load credentials from past"
                f = open("./.msync","r")
                contents = f.read()
                self.u,self.p = contents.split('|')
                self.username_tb.setText(self.u)
                self.password_tb.setText(self.p)
        except:
            print "Failed to load credentials :: Loading login frame"

    def login_done(self, msg):
        self.status_text.setText(msg)
        if msg == "Logged In":
            self.logged_in = True
            self.show_main_frame()

    def load_courses(self,courses_list):
        print courses_list
        try:
            f = open("./.selected_list","r")
            selected_list = f.read().split("|")
        except:
            selected_list = []

        print "Selected List"
        print selected_list
        self.checkboxes = []
        
        for item in courses_list:
            cb = QStandardItem(item)
            check = Qt.Checked if item in selected_list else Qt.Unchecked
            cb.setCheckState(check)
            cb.setCheckable(True)
            self.checkboxes.append(cb)
            self.model.appendRow(cb)

    def show_main_frame(self):
        print "Loading Main Frame"
        if not self.logged_in:
            self.show_login_frame()
            return

        self.login_frame.hide()
        self.sync.listCourses()



        self.setCentralWidget(self.main_frame)
        self.main_frame_box.addWidget(self.pdfGet)
        self.main_frame.show()

    def initiate_login(self):
        self.login_button.setEnabled(False)
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
        print "Now firing thread request"
        self.sync.loginCredentials(u,p)

    def start_sync(self):
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
        self.start_sync_button.setEnabled(False)
        self.status_text.setText("Syncing ... ")
        self.sync.syncCourses(checklist, folderNames, (self.pdfGet.checkState()==Qt.Checked))
        print "Completed GUI"

    def sync_done(self, msg):
        self.status_text.setText("Syncing ... ")
        self.start_sync_button.setEnabled(True)

    def create_status_bar(self):
        self.status_text = QLabel("Idle")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        #settings_action = self.create_action("&Settings", slot=self.get_login,
        #    shortcut="Ctrl+S", tip="Configure MBox")

        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu, (quit_action,))
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About Moodle Sync')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action( self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
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
