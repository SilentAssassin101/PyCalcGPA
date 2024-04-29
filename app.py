from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, \
    QTableWidgetItem, QTableWidget, QPushButton, QDialog, \
    QLineEdit
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QPalette, QColor

overallGrades = {
    "overallGPA": 0.0,
    "freshmanGPA": 0.0,
    "sophomoreGPA": 0.0,
    "juniorGPA": 0.0,
    "seniorGPA": 0.0
}


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
        self.credWidget.setColumnCount(7)
        self.credWidget.setHorizontalHeaderLabels(
            ["Course", "Credits", "Grade", "GPA", "Year", "Remove", "Edit"]
        )

        titleLabel = QLabel("Credits")

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(self.credWidget)

        self.setLayout(layout)
        self.setMinimumSize(QSize(750, 0))

        # Testing
        self.addEntry("CSC 101", 3, 97)

    def addEntry(self, course, credits, grade, year="Default"):
        # Add a new row
        rowPosition = self.credWidget.rowCount()
        self.credWidget.insertRow(rowPosition)
        self.credWidget.setItem(rowPosition, 0, QTableWidgetItem(str(course)))
        self.credWidget.setItem(rowPosition, 1, QTableWidgetItem(str(credits)))
        self.credWidget.setItem(rowPosition, 2, QTableWidgetItem(str(grade)))
        self.credWidget.setItem(rowPosition, 3, QTableWidgetItem("0.0"))
        self.credWidget.setItem(rowPosition, 4, QTableWidgetItem(str(year)))
        self.credWidget.setCellWidget(
            rowPosition, 5, EditButton(self, rowPosition)
        )
        self.credWidget.setCellWidget(
            rowPosition, 6, RemoveButton(self, rowPosition)
        )

    def removeEntry(self, row):
        self.credWidget.removeRow(row)

    def editEntry(self, row):
        course = self.credWidget.item(row, 0).text()
        credits = int(self.credWidget.item(row, 1).text())
        grade = int(self.credWidget.item(row, 2).text())
        year = self.credWidget.item(row, 4).text()
        EditCreditWindow(self, row, course, year, credits, grade).exec()


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
    def __init__(self, credList):
        super(GradeList, self).__init__()

        self.credList = credList

        titleLabel = QLabel("Grades")
        gradeWidget = QListWidget()

        gradeWidget.addItem(
            "Overall GPA: " + str(overallGrades["overallGPA"])
        )
        gradeWidget.addItem(
            "Freshman GPA: " + str(overallGrades["freshmanGPA"])
        )
        gradeWidget.addItem(
            "Sophomore GPA: " + str(overallGrades["sophomoreGPA"])
        )
        gradeWidget.addItem(
            "Junior GPA: " + str(overallGrades["juniorGPA"])
        )
        gradeWidget.addItem(
            "Senior GPA: " + str(overallGrades["seniorGPA"])
        )

        addCreditButton = QPushButton("Add Credit")
        addCreditButton.setStyleSheet("background-color: green")
        addCreditButton.clicked.connect(self.addCredit)

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(gradeWidget)
        layout.addWidget(addCreditButton)

        self.setLayout(layout)

    def addCredit(self):
        addCreditWindow = AddCreditWindow(self)
        addCreditWindow.submitted.connect(self.credList.addEntry)
        addCreditWindow.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("GPA Calculator")

        mainLayout = QHBoxLayout()

        theCredList = CredList()

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(GradeList(theCredList))
        mainLayout.addLayout(leftLayout)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(theCredList)
        mainLayout.addLayout(rightLayout)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)


class AddCreditWindow(QDialog):
    submitted = pyqtSignal(str, int, int)

    def __init__(self, credList):
        super(AddCreditWindow, self).__init__()

        self.setWindowTitle("Add Credit")

        layout = QVBoxLayout()

        courseLabel = QLabel("Course")
        self.courseEntry = QLineEdit()

        creditsLabel = QLabel("Credits")
        self.creditsEntry = QLineEdit()

        gradeLabel = QLabel("Grade")
        self.gradeEntry = QLineEdit()

        submitButton = QPushButton("Submit")
        submitButton.clicked.connect(self.onSubmit)

        layout.addWidget(courseLabel)
        layout.addWidget(self.courseEntry)
        layout.addWidget(creditsLabel)
        layout.addWidget(self.creditsEntry)
        layout.addWidget(gradeLabel)
        layout.addWidget(self.gradeEntry)
        layout.addWidget(submitButton)

        self.setLayout(layout)

    def onSubmit(self):
        self.submitted.emit(
            self.courseEntry.text(),
            int(self.creditsEntry.text()),
            int(self.gradeEntry.text())
        )
        self.close()


class EditCreditWindow(QDialog):
    def __init__(
        self, credList, row, oldCourse, oldYear, oldCredits, oldGrade
    ):
        super(EditCreditWindow, self).__init__()

        self.setWindowTitle("Edit Credit")
        self.credList = credList
        self.row = row

        layout = QVBoxLayout()

        courseLabel = QLabel("Course")
        self.courseEntry = QLineEdit()
        self.courseEntry.setText(oldCourse)

        creditsLabel = QLabel("Credits")
        self.creditsEntry = QLineEdit()
        self.creditsEntry.setText(str(oldCredits))

        gradeLabel = QLabel("Grade")
        self.gradeEntry = QLineEdit()
        self.gradeEntry.setText(str(oldGrade))

        yearLabel = QLabel("Year")
        self.yearEntry = QLineEdit()
        self.yearEntry.setText(oldYear)

        submitButton = QPushButton("Submit")
        submitButton.clicked.connect(self.onSubmit)

        layout.addWidget(courseLabel)
        layout.addWidget(self.courseEntry)
        layout.addWidget(creditsLabel)
        layout.addWidget(self.creditsEntry)
        layout.addWidget(gradeLabel)
        layout.addWidget(self.gradeEntry)
        layout.addWidget(yearLabel)
        layout.addWidget(self.yearEntry)
        layout.addWidget(submitButton)

        self.setLayout(layout)

    def onSubmit(self):
        self.credList.removeEntry(self.row)
        self.credList.addEntry(
            self.courseEntry.text(),
            self.creditsEntry.text(),
            self.gradeEntry.text(),
            self.yearEntry.text()
        )
        self.close()


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
