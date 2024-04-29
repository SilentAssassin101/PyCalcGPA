from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, \
    QTableWidgetItem, QTableWidget, QPushButton
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class CredList(QWidget):
    def __init__(self):
        super(CredList, self).__init__()

        self.credWidget = QTableWidget()
        self.credWidget.setColumnCount(6)
        self.credWidget.setHorizontalHeaderLabels(
            ["Course", "Credits", "Grade", "GPA", "Remove", "Edit"]
            )

        titleLabel = QLabel("Credits")

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(self.credWidget)

        self.setLayout(layout)
        self.setMinimumSize(QSize(650, 0))

        # Testing
        self.addEntry("CSC 101", 3, 97)

    def addEntry(self, course, credits, grade):
        # Add a new row
        rowPosition = self.credWidget.rowCount()
        self.credWidget.insertRow(rowPosition)
        self.credWidget.setItem(rowPosition, 0, QTableWidgetItem(course))
        self.credWidget.setItem(rowPosition, 1, QTableWidgetItem(str(credits)))
        self.credWidget.setItem(rowPosition, 2, QTableWidgetItem(str(grade)))
        self.credWidget.setItem(rowPosition, 3, QTableWidgetItem("0.0"))
        self.credWidget.setCellWidget(
            rowPosition, 4, RemoveButton(self, rowPosition)
            )
        self.credWidget.setCellWidget(
            rowPosition, 5, EditButton(self, rowPosition)
            )

    def removeEntry(self, row):
        self.credWidget.removeRow(row)

    def editEntry(self, row):
        course = self.credWidget.item(row, 0).text()
        credits = int(self.credWidget.item(row, 1).text())
        grade = int(self.credWidget.item(row, 2).text())
        # To be implemented
        self.removeEntry(row)
        self.addEntry(course, credits, grade)


class RemoveButton(QPushButton):
    def __init__(self, credList, row):
        super(RemoveButton, self).__init__()
        self.setText("Remove")
        self.setStyleSheet("background-color: red")
        self.clicked.connect(lambda: credList.removeEntry(row))


class EditButton(QPushButton):
    def __init__(self, credList, row):
        super(EditButton, self).__init__()
        self.setText("Edit")
        self.setStyleSheet("background-color: blue")
        self.clicked.connect(lambda: credList.editEntry(row))


class GradeList(QWidget):
    def __init__(self):
        super(GradeList, self).__init__()

        titleLabel = QLabel("Grades")
        gradeWidget = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(gradeWidget)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("GPA Calculator")

        mainLayout = QHBoxLayout()

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(GradeList())
        mainLayout.addLayout(leftLayout)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(CredList())
        mainLayout.addLayout(rightLayout)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
