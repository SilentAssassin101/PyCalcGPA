from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, \
    QTableWidgetItem, QTableWidget, QPushButton, QDialog, \
    QLineEdit
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import sqlite3
from typing import List, Dict, Tuple

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
    (course TEXT, credits FLOAT, grade INTEGER, year TEXT)"""
)


def fetchGrades() -> Tuple[Dict[str, List[int]], Dict[str, List[float]]]:
    """Fetches the grades from the database and returns them in a dictionary.
    Format: {year: [grades], year: [credits]}

    Returns:
        Tuple[Dict[str, List[int]], Dict[str, List[float]]]: Grades & Credits
    """
    res = cur.execute("SELECT * FROM grades")

    totalGrades = {
        "freshman": [],
        "sophomore": [],
        "junior": [],
        "senior": []
    }
    totalCredits = {
        "freshman": [],
        "sophomore": [],
        "junior": [],
        "senior": []
    }

    for row in res.fetchall():
        gradeColumn = row[2]
        creditColumn = row[1]
        yearColumn = row[3].lower()

        totalGrades[yearColumn].append(gradeColumn)
        totalCredits[yearColumn].append(creditColumn)

    return totalGrades, totalCredits


def updateGPA():
    """Updates the GPA values in the overallGrades dictionary
    """
    totalGrades, totalCredits = fetchGrades()
    global overallGrades

    totalGPA = {
        "overallGPA": 0.0,
        "freshmanGPA": 0.0,
        "sophomoreGPA": 0.0,
        "juniorGPA": 0.0,
        "seniorGPA": 0.0
    }

    # These 2 lists will be divided to get the actual GPA
    allGrades = []  # List of all the weighted GPA values
    allCredits = []  # List of all the credits

    for year, yearValue in totalGrades.items():
        try:
            theseGrades = 0

            # Adds up all the grades for the year
            # Converts each grade to a GPA value
            # Weights each GPA value depending on credits
            for i, grade in enumerate(yearValue):
                theseGrades += (convertGrade(grade) * totalCredits[year][i])

            # Divides the total weighted GPA value by the total credits
            totalGPA[year + "GPA"] = theseGrades / sum(totalCredits[year])

            # Adds values to master lists for overall GPA calculation
            allGrades.append(theseGrades)
            allCredits.append(sum(totalCredits[year]))
        except ZeroDivisionError:
            totalGPA[year + "GPA"] = 0.0

    try:
        totalGPA["overallGPA"] = sum(allGrades) / sum(allCredits)
    except ZeroDivisionError:
        totalGPA["overallGPA"] = 0.0

    overallGrades = totalGPA


def convertGrade(grade: int) -> float:
    """Converts a grade to a GPA value.

    Args:
        grade (int): Grade value 1-100

    Raises:
        ValueError: Grade value outside range

    Returns:
        float: GPA value
    """

    conversionValues = {
        94: 4.0,
        90: 3.7,
        87: 3.3,
        84: 3.0,
        80: 2.7,
        77: 2.3,
        74: 2.0,
        70: 1.7,
        67: 1.3,
        64: 1.0,
        60: 0.7,
        0: 0.0
    }

    if grade < 60:
        return 0.0
    for key, value in conversionValues.items():
        if grade >= key:
            return value
    raise ValueError("Invalid grade")


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

    def addEntry(
        self,
        course: str,
        credits: float,
        grade: int,
        year="Freshman",
        save=True
    ):
        """Adds an entry to the table.
        Optionally commits it to the database.

        Args:
            course (str): _description_
            credits (float): _description_
            grade (int): _description_
            year (str, optional): _description_. Defaults to "Freshman".
            save (bool, optional): _description_. Defaults to True.

        Raises:
            ValueError: invalid year
            ValueError: invalid credits, course, or grade
        """

        if year not in ["Freshman", "Sophomore", "Junior", "Senior"]:
            raise ValueError("Invalid year")
        if course == "" or float(credits) == 0 or grade == "":
            raise ValueError("Invalid data")

        rowPosition = self.credWidget.rowCount()

        self.credWidget.insertRow(rowPosition)
        self.credWidget.setItem(rowPosition, 0, QTableWidgetItem(str(course)))
        self.credWidget.setItem(rowPosition, 1, QTableWidgetItem(str(credits)))
        self.credWidget.setItem(rowPosition, 2, QTableWidgetItem(str(grade)))

        gpa = convertGrade(int(grade))

        self.credWidget.setItem(rowPosition, 3, QTableWidgetItem(str(gpa)))
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

    def removeEntry(self, row: int):
        """Removes an entry from the table and the database.

        Args:
            row (int): row index to remove
        """
        try:
            course = self.credWidget.item(row, 0).text()
            self.credWidget.removeRow(row)
        except AttributeError:
            print("No course to remove")
        cur.execute("DELETE FROM grades WHERE course=?", (course,))
        con.commit()
        self.parentWindow.updateLeft()

    def editEntry(self, row: int):
        """Modifies an entry in the table and the database.

        Args:
            row (int): row index to edit
        """
        course = self.credWidget.item(row, 0).text()
        credits = float(self.credWidget.item(row, 1).text())
        grade = int(self.credWidget.item(row, 2).text())
        year = self.credWidget.item(row, 4).text()
        EditCreditWindow(self, row, course, year, credits, grade).exec()

    def setup(self):
        """initializes the table with data from the database
        """
        res = cur.execute("SELECT * FROM grades")
        for row in res.fetchall():
            self.addEntry(row[0], row[1], row[2], row[3], False)
        self.parentWindow.updateLeft()


class RemoveButton(QPushButton):
    def __init__(self, credList: CredList, row: int):
        super(RemoveButton, self).__init__()
        self.setText("Remove")
        self.setStyleSheet("background-color: red")
        self.clicked.connect(lambda: credList.removeEntry(row))


class EditButton(QPushButton):
    def __init__(self, credList: CredList, row: int):
        super(EditButton, self).__init__()
        self.setText("Edit")
        self.setStyleSheet("background-color: blue")
        self.clicked.connect(lambda: credList.editEntry(row))


class GradeList(QWidget):
    def __init__(self, credList: CredList):
        super(GradeList, self).__init__()

        self.credList = credList

        titleLabel = QLabel("Grades")
        self.gradeWidget = QListWidget()

        addCreditButton = QPushButton("Add Credit")
        addCreditButton.setStyleSheet("background-color: green")
        addCreditButton.clicked.connect(self.addCredit)

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(self.gradeWidget)
        layout.addWidget(addCreditButton)

        self.setLayout(layout)

    def addCredit(self):
        """Adds a credit to the list of credits (right bar)
        """
        addCreditWindow = AddCreditWindow(self)
        addCreditWindow.submitted.connect(self.credList.addEntry)
        addCreditWindow.exec()

    def updateSelf(self):
        """Updates the grade list with the current GPA values (left bar)
        """

        self.gradeWidget.clear()
        self.gradeWidget.addItem(
            "Overall GPA: " + str(
                (overallGrades["overallGPA"])
            )
        )
        self.gradeWidget.addItem(
            "Freshman GPA: " + str(
                (overallGrades["freshmanGPA"])
            )
        )
        self.gradeWidget.addItem(
            "Sophomore GPA: " + str(
                (overallGrades["sophomoreGPA"])
            )
        )
        self.gradeWidget.addItem(
            "Junior GPA: " + str(
                (overallGrades["juniorGPA"])
            )
        )
        self.gradeWidget.addItem(
            "Senior GPA: " + str(
                (overallGrades["seniorGPA"])
            )
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
        """Updates the stored GPA values then updates the grade list
        """
        updateGPA()  # Update the GPA values
        self.theGradeList.updateSelf()  # Update the grade list


class AddCreditWindow(QDialog):
    submitted = pyqtSignal(str, float, int)

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
        if (
            self.courseEntry.text() == "" or
            self.creditsEntry.text() == "" or
            self.gradeEntry.text() == ""
        ):
            return
        try:
            float(self.creditsEntry.text())
            int(self.gradeEntry.text())
        except ValueError:
            return

        try:
            testNum = float(self.creditsEntry.text())
            if testNum > 100:
                return
        except Exception as e:
            print(e)
            return

        self.submitted.emit(
            self.courseEntry.text(),
            float(self.creditsEntry.text()),
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
        # Data Validation
        data = [
            self.courseEntry.text(),
            self.creditsEntry.text(),
            self.gradeEntry.text(),
            self.yearEntry.text()
        ]
        for item in data:
            if item == "":
                return
        if self.yearEntry.text() not in [
            "Freshman", "Sophomore", "Junior", "Senior"
        ]:
            return
        try:
            float(self.creditsEntry.text())
            int(self.gradeEntry.text())
        except ValueError:
            return

        try:
            testNum = float(self.creditsEntry.text())
            if testNum > 100:
                return
        except Exception as e:
            print(e)
            return

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
