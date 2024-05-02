from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, \
    QTableWidgetItem, QTableWidget, QPushButton, QDialog, \
    QLineEdit
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import sqlite3

overallGrades = {
    "overallGPA": 0.0,
    "freshmanGPA": 0.0,
    "sophomoreGPA": 0.0,
    "juniorGPA": 0.0,
    "seniorGPA": 0.0
}

con = sqlite3.connect("grades.db")
cur = con.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS grades
    (course TEXT, credits INTEGER, grade INTEGER, year TEXT)"""
)


def updateGPA():
    res = cur.execute("SELECT * FROM grades")

    totalGrades = {
        "freshman": 0.0,
        "sophomore": 0.0,
        "junior": 0.0,
        "senior": 0.0
    }

    totalCredits = {
        "freshman": 0,
        "sophomore": 0,
        "junior": 0,
        "senior": 0
    }

    for row in res.fetchall():
        totalGrades[row[3].lower()] += row[2]
        totalCredits[row[3].lower()] += row[1]

    totalGPA = {
        "overallGPA": 0.0,
        "freshmanGPA": 0.0,
        "sophomoreGPA": 0.0,
        "juniorGPA": 0.0,
        "seniorGPA": 0.0
    }

    sumGrades = 0
    sumCredits = 0

    for year in totalGrades:
        try:
            totalGPA[year] = totalGrades[year] / totalCredits[year]
        except ZeroDivisionError:
            totalGPA[year] = 0.0
        sumGrades += totalGrades[year]
        sumCredits += totalCredits[year]

    try:
        totalGPA["overallGPA"] = sumGrades / sumCredits
    except ZeroDivisionError:
        totalGPA["overallGPA"] = 0.0

    for key in totalGPA:
        overallGrades[key] = totalGPA[key]
        print(f"{key}: {totalGPA[key]}")


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class CredList(QWidget):
    def __init__(self, parentWindow):
        super(CredList, self).__init__()

        self.parentWindow = parentWindow

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

    def addEntry(self, course, credits, grade, year="Freshman", save=True):
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
        if save:
            cur.execute(
                "INSERT INTO grades VALUES (?, ?, ?, ?)",
                (course, credits, grade, year)
            )
            con.commit()
            self.parentWindow.updateLeft()

    def removeEntry(self, row):
        course = self.credWidget.item(row, 0).text()
        self.credWidget.removeRow(row)
        cur.execute("DELETE FROM grades WHERE course=?", (course,))
        con.commit()
        self.parentWindow.updateLeft()

    def editEntry(self, row):
        course = self.credWidget.item(row, 0).text()
        credits = int(self.credWidget.item(row, 1).text())
        grade = int(self.credWidget.item(row, 2).text())
        year = self.credWidget.item(row, 4).text()
        EditCreditWindow(self, row, course, year, credits, grade).exec()

    def setup(self):
        res = cur.execute("SELECT * FROM grades")
        for row in res.fetchall():
            self.addEntry(row[0], row[1], row[2], row[3], False)
        self.parentWindow.updateLeft()


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
        self.gradeWidget = QListWidget()

        self.updateSelf()

        addCreditButton = QPushButton("Add Credit")
        addCreditButton.setStyleSheet("background-color: green")
        addCreditButton.clicked.connect(self.addCredit)

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(self.gradeWidget)
        layout.addWidget(addCreditButton)

        self.setLayout(layout)

    def addCredit(self):
        addCreditWindow = AddCreditWindow(self)
        addCreditWindow.submitted.connect(self.credList.addEntry)
        addCreditWindow.exec()

    def updateSelf(self):
        self.gradeWidget.clear()
        self.gradeWidget.addItem(
            "Overall GPA: " + str(overallGrades["overallGPA"])
        )
        self.gradeWidget.addItem(
            "Freshman GPA: " + str(overallGrades["freshmanGPA"])
        )
        self.gradeWidget.addItem(
            "Sophomore GPA: " + str(overallGrades["sophomoreGPA"])
        )
        self.gradeWidget.addItem(
            "Junior GPA: " + str(overallGrades["juniorGPA"])
        )
        self.gradeWidget.addItem(
            "Senior GPA: " + str(overallGrades["seniorGPA"])
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("GPA Calculator")

        mainLayout = QHBoxLayout()

        theCredList = CredList(self)
        self.theGradeList = GradeList(theCredList)
        theCredList.setup()

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.theGradeList)
        mainLayout.addLayout(leftLayout)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(theCredList)
        mainLayout.addLayout(rightLayout)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def updateLeft(self):
        updateGPA()
        self.theGradeList.updateSelf()


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


def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
