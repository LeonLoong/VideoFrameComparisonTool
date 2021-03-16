from PyQt5 import QtGui, QtCore, QtWidgets
from win32api import GetSystemMetrics
import queue as queue
import xml.etree.ElementTree as xml
import sys, os, subprocess, time

Demo_Global_Directory = ("A:\Demo\Global\Data\Demo_CheckFrameTool")
Demo_CheckFrameTool_Directory = os.path.join('C:', os.environ['HOMEPATH'], 'Demo', 'Data',
                                            'Demo_CheckFrameTool')
UserInfo_Path = ("User_Info.xml")

def copy_File(src, dst):
    from shutil import copyfile
    copyfile(src, dst)


def create_Demo():
    if not os.path.exists(Demo_CheckFrameTool_Directory):
        os.makedirs(Demo_CheckFrameTool_Directory)

    src = ("%s\%s" % (Demo_Global_Directory, UserInfo_Path))
    dst = ("%s\%s" % (Demo_CheckFrameTool_Directory, UserInfo_Path))
    if not os.path.exists(dst):
        print (src, dst)
        copy_File(src, dst)


create_Demo()

userInfo_dataPath = ("%s\%s" % (Demo_CheckFrameTool_Directory, UserInfo_Path))
userInfo_dataTree = xml.parse(userInfo_dataPath)
userInfo_dataRoot = userInfo_dataTree.getroot()


def get_UserInfo():
    for userInfo_data in userInfo_dataRoot:
        comp_Dir = userInfo_data.find("COMP_DIR").text
        anm_Dir = userInfo_data.find("ANM_DIR").text
        return comp_Dir, anm_Dir


def comp_Dir():
    comp_Dir = get_UserInfo()[0]
    return comp_Dir


def anm_Dir():
    anm_Dir = get_UserInfo()[1]
    return anm_Dir


def get_Different(anm_list, comp_list):
    return (list(set(anm_list) - set(comp_list)))


def get_frame(file):
    cmd = (
            'A:/Demo/Global/vendor/ffmpeg-20180808-90dc584-win64-static/bin/ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 %s' % (
        file))
    output = subprocess.check_output(
        cmd,

        shell=True,
        stderr=subprocess.STDOUT
    )
    return output


class FrameCheckingTool(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        resolution_width = (GetSystemMetrics(0) / 4)
        resolution_height = (GetSystemMetrics(1) / 2)
        self.setObjectName('FrameCheckingTool')
        self.setWindowTitle('FrameCheckingTool')
        self.setMinimumSize(int(resolution_width), int(resolution_height))
        self.initUI()

    def initUI(self):
        ### define
        self.widget = QtWidgets.QWidget(self)
        self.progressBar = QtWidgets.QProgressBar()
        self.verticalLayout_01 = QtWidgets.QVBoxLayout()
        self.verticalLayout_02 = QtWidgets.QVBoxLayout()
        self.textEdit_information = QtWidgets.QTextEdit()
        self.comboBox_comp = QtWidgets.QComboBox(editable=True)
        self.comboBox_comp.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.comboBox_anm = QtWidgets.QComboBox(editable=True)
        self.comboBox_anm.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.pushButton_check = QtWidgets.QPushButton("Check")

        ### setup
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Ready to Check')
        self.statusBar().addPermanentWidget(self.progressBar)
        self.widget.setLayout(self.verticalLayout_01)
        self.verticalLayout_01.addLayout(self.verticalLayout_02)
        self.verticalLayout_02.addWidget(self.comboBox_comp)
        self.verticalLayout_02.addWidget(self.comboBox_anm)
        self.verticalLayout_02.addWidget(self.pushButton_check)
        self.verticalLayout_02.addWidget(self.textEdit_information)
        self.textEdit_information.toHtml()

        ### execute
        self.pre_update()

        ### signal_textEdit
        self.comboBox_comp.lineEdit().returnPressed.connect(self.post_update)
        self.comboBox_anm.lineEdit().returnPressed.connect(self.post_update)
        self.pushButton_check.clicked.connect(self.start_updateThread)

        self.updateTextEditThread = UpdateThread()
        self.updateTextEditThread.signal_textEdit.connect(self.updateTextEdit)

        self.updateProgressBarThread = UpdateThread()
        self.updateProgressBarThread.signal_progressBar.connect(self.updateProgressBar)

    def pre_update(self):
        self.comboBox_comp.lineEdit().setText(comp_Dir())
        self.comboBox_anm.lineEdit().setText(anm_Dir())

        global comp_mov_dir
        comp_mov_dir = self.comboBox_comp.currentText()
        global anm_mov_dir
        anm_mov_dir = self.comboBox_anm.currentText()

        global comp_mov_list
        comp_mov_list = []
        for comp_mov in os.listdir(comp_mov_dir):
            if comp_mov.endswith(".mov"):
                comp_mov_list.append(comp_mov)

        global anm_mov_list
        anm_mov_list = []
        for anim_mov in os.listdir(anm_mov_dir):
            if anim_mov.endswith(".mov"):
                anm_mov_list.append(anim_mov)

        self.textEdit_information.append("<u>composition directory</u>")
        self.textEdit_information.append(comp_mov_dir)

        self.textEdit_information.append("\n")

        self.textEdit_information.append("<u>animation directory</u>")
        self.textEdit_information.append(anm_mov_dir)

        self.textEdit_information.append("\n")

        if get_Different(anm_mov_list, comp_mov_list):
            self.textEdit_information.append("<u>video files doesn't exist.</u>")
            for file in sorted(get_Different(anm_mov_list, comp_mov_list)):
                remove_comp_mov = comp_mov_list[0].split(".")[0].split("_")[-1]
                comp_mov = comp_mov_list[0].split(remove_comp_mov)[0]
                if file.startswith(comp_mov):
                    self.textEdit_information.append("%s doesn't exist." % (file))

        self.textEdit_information.append("\n")

        get_anm_totalFile = len(set(anm_mov_list).intersection(comp_mov_list))
        get_comp_totalFile = len(set(comp_mov_list).intersection(anm_mov_list))
        time = get_anm_totalFile + get_comp_totalFile / 116.2609238451935 * 60
        minutes, seconds = divmod(time, 60)
        self.textEdit_information.append(
            "<u>total query files: %s estimate time: %02d m %02d s</u>" % (get_anm_totalFile * 2, minutes, seconds))

        self.textEdit_information.append("\n")

    def post_update(self):
        self.textEdit_information.clear()
        del comp_mov_list[:], anm_mov_list[:]
        for comp_dir in userInfo_dataRoot.iter('COMP_DIR'):
            comp_dir.text = str(self.comboBox_comp.currentText())
        for anm_dir in userInfo_dataRoot.iter('ANM_DIR'):
            anm_dir.text = str(self.comboBox_anm.currentText())
        userInfo_dataTree.write(userInfo_dataPath)
        self.pre_update()

    def start_updateThread(self):
        self.updateTextEditThread.start()
        self.updateProgressBarThread.start()

    def updateTextEdit(self, text, value):
        self.textEdit_information.append(text)
        self.progressBar.setValue(value)
        get_totalFile = len(set(anm_mov_list).intersection(comp_mov_list))
        if value != get_totalFile*2:
            self.statusBar().showMessage('Querying ...')
        else:
            self.statusBar().showMessage('Finished ~')

    def updateProgressBar(self, value):
        self.progressBar.setMaximum(value)

class UpdateThread(QtCore.QThread):
    signal_textEdit = QtCore.pyqtSignal(str, int)
    signal_progressBar = QtCore.pyqtSignal(int)

    def run(self):
        get_totalFile = len(set(anm_mov_list).intersection(comp_mov_list))
        self.signal_progressBar.emit(get_totalFile*2)

        progressBar_value = -1

        anm_value = 0
        self.signal_textEdit.emit("<u>query animation video frame</u>", progressBar_value + 1)
        anm_mov_frame_list = []
        for mov in sorted(set(anm_mov_list).intersection(comp_mov_list)):
            anm_value = anm_value + 1
            progressBar_value = progressBar_value + 1
            anm_mov_frame = get_frame("%s/%s" % (anm_mov_dir, mov)).rstrip()
            anm_mov_frame_list.append([("%s/%s" % (anm_mov_dir, mov)), anm_mov_frame])
            self.signal_textEdit.emit("%03d total: %03d frame anm: %s" % (anm_value, int(anm_mov_frame), mov), progressBar_value + 1)

        self.signal_textEdit.emit("\n", progressBar_value + 1)
        self.signal_textEdit.emit("<u>animation video frame queried</u>", progressBar_value + 1)
        self.signal_textEdit.emit("\n", progressBar_value + 1)

        comp_value = 0
        self.signal_textEdit.emit("<u>query composition video frame</u>", progressBar_value + 1)
        comp_mov_frame_list = []
        for mov in sorted(set(anm_mov_list).intersection(comp_mov_list)):
            comp_value = comp_value + 1
            progressBar_value = progressBar_value + 1
            comp_mov_frame = get_frame("%s/%s" % (comp_mov_dir, mov)).rstrip()
            comp_mov_frame_list.append([("%s/%s" % (comp_mov_dir, mov)), comp_mov_frame])
            self.signal_textEdit.emit("%03d total: %03d frame comp: %s" % (comp_value, int(comp_mov_frame), mov), progressBar_value + 1)

        self.signal_textEdit.emit("\n", progressBar_value + 1)
        self.signal_textEdit.emit("<u>composition video frame queried</u>", progressBar_value + 1)
        self.signal_textEdit.emit("\n", progressBar_value + 1)

        notSync_anm_mov_list = [i for i, j in zip(anm_mov_frame_list, comp_mov_frame_list) if i[-1] != j[-1]]
        notSync_comp_mov_list = [i for i, j in zip(comp_mov_frame_list, anm_mov_frame_list) if i[-1] != j[-1]]
        for notSync_anm_mov, notSync_comp_mov in zip(notSync_anm_mov_list, notSync_comp_mov_list):
            notSync_comp_mov_path = notSync_comp_mov[0].replace("//", "\\")
            notSync_differentFrame = (abs(int(notSync_anm_mov[-1]) - int(notSync_comp_mov[-1])))
            compile_info = "%s ~ not match %s frame" % (notSync_comp_mov_path, notSync_differentFrame)
            self.signal_textEdit.emit(compile_info, progressBar_value + 1)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = FrameCheckingTool()
    ui.show()
    sys.exit(app.exec_())