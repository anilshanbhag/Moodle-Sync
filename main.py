#!/usr/bin/python

import mechanize
import os
import math, random, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Sync(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.auth_set = False
        self.logged_in = False

        self.br = mechanize.Browser()
        self.courses = {}  
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')]

    def loginCredentials(self, username, password):
        self.username = username
        self.password = password
        self.method = "loginCredentials"
        print "starting thread"
        self.start()

    def loginCredentialsRun(self):
        username = self.username
        password = self.password
        self.auth_set = True
        try:
            self.login()
            if self.logged_in:
                self.emit(SIGNAL("login_status(QString)"), "Logged In")
            else:
                self.emit(SIGNAL("login_status(QString)"), "Login Failed") 
        except:
            self.emit(SIGNAL("login_status(QString)"), "Error")

    def login(self):
        self.br.open("http://moodle.iitb.ac.in")
        print self.br.title()
        assert self.br.viewing_html()
        self.br.select_form(nr=1)
        for i in range(3):
            self.br.form.controls[i].readonly = False
        self.br["username"] = self.username
        self.br["password"] = self.password
        self.br.submit()
        
        # Title of login page is "Login to Moodle"
        # If no Login in title => We are not on login page
        # Assuming we landed inside moodle
        if not "Login" in self.br.title():
           self.logged_in = True
           print "Logged In"
        
        assert self.br.viewing_html()

    def listCourses(self):
        self.method = "listCourses"
        self.start()

    def listCoursesRun(self):
        check = ('title', 'Click to enter this course')
        for link in self.br.links():
            if check in link.attrs:
                text = link.text.split(':')
                self.courses[text[0].strip()] = link
        self.emit(SIGNAL("courses(PyQt_PyObject)"), self.courses.keys()) 

    def syncCourses(self, storedCourses, folderNames, getpdf):
        self.storedCourses = storedCourses
        self.folderNames = folderNames
        self.getpdf = getpdf
        self.method = "syncCourses"
        self.start()

    def syncCoursesRun(self):
        for course in self.storedCourses:
            self.br.open(self.courses[course].url)
            assert self.br.viewing_html()
            allFiles = {}

            for link in self.br.links():
                if "mod/resource/view" in link.url:
                    name=link.text.replace('[IMG]','')
                    allFiles[name] = link
            if(not(os.path.isdir(course))):
                os.mkdir(course)

            storedFiles=os.listdir(self.folderNames[course])
            for i in xrange(0,len(storedFiles)):
                storedFiles[i] = storedFiles[i].rsplit('.',1)[0].strip()

            for afile in allFiles:
                if afile.split()[-1] == "document":
                    afilename=afile.rsplit(' ',2)[0].strip()
                else:
                    afilename=afile
                    print [afilename]
                if (not(afilename in storedFiles)):
                    response=self.br.open(allFiles[afile].url)
                    if(self.getpdf):
                        if (response.info()["Content-type"].split(";")[0]=="text/html"):
                            for link in self.br.links():
                                if (link.url.find("pluginfile.php")!=-1):
                                    response=self.br.open(link.url)
                    extension=response.geturl().rsplit('.',1)[1]
                    save_path=os.path.join(self.folderNames[course]+'/',afilename+'.'+extension)
                    output=open(save_path,'w')
                    output.write(response.read())
                    output.close()

        self.emit(SIGNAL("sync_courses(QString)"), "done")


    def run(self):
        if self.method == "listCourses":
            self.listCoursesRun()
        elif self.method == "syncCourses":
            self.syncCoursesRun()
        elif self.method == "loginCredentials":
            self.loginCredentialsRun()

    def __del__(self):
    
        self.exiting = True
        self.wait()
