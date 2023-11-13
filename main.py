from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit, \
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, \
    QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu
import sys
# import sqlite3
import mysql.connector


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="Kamal123##", database="school"):    #database_file = "database.db"):
        self.host = host
        self.user = user
        self.password =password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)   #sqlite3.connect(self.database_file)
        return connection
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Create File menu
        file_menu_item = self.menuBar().addMenu("&File")
        # Create Help menu
        help_menu_item = self.menuBar().addMenu("&Help")
        # Create Edit menu
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add menu item to File menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)  # Menu item created
        file_menu_item.addAction(add_student_action)  # Menu item added to menu list
        add_student_action.triggered.connect(self.insert)  # Inserts a dialogue box to add student menu item.

        # Add menu item to Help menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)  # This line of code is for Mac users
        about_action.triggered.connect(self.about)

        # Add menu item to Edit menu
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)
        # about_action.setMenuRole(QAction.MenuRole.NoRole) # if hel menu is not visible

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)

        toolbar.addAction(add_student_action)

        toolbar.addAction(search_action)

        self.addToolBar(toolbar)

        # Create a table widget/structure
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)

        self.setCentralWidget(self.table)

        # Create a status bar (with edit and delete buttons in the stats bar through cell_clicked method)
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        # self.statusbar.addWidget(self.statusbar)

        # hello = QLabel("Hello There!")
        # statusbar.addWidget(hello)
        #
        # hello = QLabel("Hello World!")
        # statusbar.addWidget(hello)

        # Detect a cell click and add status bar elements - Edit Record, and Delete Record buttons
        self.table.cellClicked.connect(self.cell_clicked)

    # status bar elements - edit button, and delete button added. These button become visible upon a cell clicked
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        # Establish connection to edit dialog box
        edit_button.clicked.connect(self.edit)  # Once edit button is clicked, edit method is executed-which is linked to EditDialog class

        delete_button = QPushButton("Delete Record")
        # Establish connection to delete dialog box
        delete_button.clicked.connect(self.delete)  # Once delete button is clicked, delete method is executed-which is linked to DeleteDialog class
        # Removes duplicate buttons/widgets from the status bar. In the absence of this code, Edit Record and
        # Delete Record buttons get accumulated instead of just having two buttons
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Edit button and delete button widgets are added to the status bar defined in the main window. These codes
        # should always be placed after cleanup by children above, otherwise they will disappear from status bar:-

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    # Loading data from database table and populate the table that was created in the above stage
    def load_data(self):
        connection = DatabaseConnection().connect()  # sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students") # When printed as a list, Returns a list of row tuples (without column header-which is defined in the main window class, without row number-just id is there)
        data = cursor.fetchall()
        # print(list(data)) # a list of row tuples
        self.table.setRowCount(0)  # It resets the table and load data as fresh to avoid duplicate data.
        for row_number, row_data in enumerate(data):  # Breaks into the list of row tuples, row number is generated on enumeration, data doesn't have row number. As list has tuples, it is asumed to have row numbers for each tuple
            # print(row_number)
            # print(row_data)
            self.table.insertRow(row_number) # Row is created in the main window table
            for column_number, cell_data in enumerate(row_data): # Breaks into the each tuple in the list, Column number is generated on enumeration, it is not in the row_data. As tuple has only one row, it is asumed to have column number.
                # print(column_number)
                # print(cell_data)
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(cell_data)))
        connection.close()

    # Create methods for main menus in the menu bar:-
    # Create a insert dialogue box to insert new student registration data in the table through\
    # file menu item-Add Student
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    # Create a insert dialogue box to insert new student registration data in the table through edit menu item-Search
    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    # Method for help menu bar item - About
    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    # Create methods for status bar buttons:-
    # Method for edit record at status bar
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    # Method for delete record at status bar
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the training. Please feel free to modify it.
        """
        self.setText(content)


class EditDialog(QDialog): # THIS CLASS HAS 3 MAIN STEPS(1ST AND 2ND STEPS ARE FUNDAMENTAL PARTS OF A CLASS):-
    def __init__(self):  # STEP 1. INPUT GENERATION: This method initialises variables and selects data from main window table and place them into the edit dialog box
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()  # Current selected row

        student_name = main_window.table.item(index, 1).text()  # Get student name-this gets feed into update
                                                                       # dialog box which will eventually update database below

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()  # Get student id--this gets feed into update
                                                                       # dialog box which will eventually update database below

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")   # If name is empty then this is the default

        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()  # Get course name--this gets feed into update
                                                                       # dialog box which will eventually update database below
        self.courses_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.courses_name.addItems(courses) # This adds courses in the combo box in order-with Biology being displayed
        self.courses_name.setCurrentText(course_name) # This sets correct course name for selected row as displayed

        layout.addWidget(self.courses_name)

        # Add mobile widget
        mobile = main_window.table.item(index, 3).text()  # Get mobile number--this gets feed into update
                                                                       # dialog box which will eventually update database below
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")  # If mobile is empty then this is the default

        layout.addWidget(self.mobile)

        # Add an update button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)

        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):  # STEP 2. INPUT PROCESSING AND DELIVERING OUTPUT: This method updates database
        connection = DatabaseConnection().connect()  # sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s", #"UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.courses_name.itemText(self.courses_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()  # & STEP 3.This code loads data back into main window table from database to reflect
                                 # updated data after edit


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        # self.setFixedWidth(300)
        # self.setFixedHeight(300)

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        index = main_window.table.currentRow()  # Returns number (selected row number) only.(Row number begins with 0,                            # while student id begins with 1)
        print("delete index:", index)
        self.student_id = main_window.table.item(index, 0).text()  # Returns number (selected student id number) only.
        print("student id:", self.student_id)

        yes.clicked.connect(self.delete_student) # Method for yes button defined, not for no button.

    def delete_student(self): # 3 main steps:-
        # 1. Get student id of selected row by first getting the index from main window table

        ## MOVED TO CLASS ##################################################################
        # index = main_window.table.currentRow()  # Returns number (selected row number) only.(Row number begins with 0,
        #                                         # while student id begins with 1)
        # print("delete index:", index)
        # student_id = main_window.table.item(index, 0).text()  # Returns number (selected student id number) only.
        # print("student id:", student_id)
        #####################################################################################

        connection = DatabaseConnection().connect()  # sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (self.student_id,))  # 2. delete the row from database
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()  # 3. This code loads data back into main window table from database to reflect
                                 # updated data after delete

        # Closing the window
        self.close() # Closes delete dialog box only(not main window), and shows confirmation widget as defined below:-

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


# Class to add new student registration data to the database through file menu
class InsertDialog(QDialog):  # 1. Create Dialog box with empty fields where you can write name, course and phone number of a new student
    def __init__(self):       # (This is unlike edit dialog box-where fields are populated from main window table, (then edited, and finally database is updated))
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)

        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")

        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)

        layout.addWidget(button)

        self.setLayout(layout)

    # Method to add new student data to database table
    def add_student(self):  # 2. Executed on clicking Register button to update database with new student details
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect() # sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)", #(?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        # Retrieves updated data from database to show in the online table
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()

        self.student_name = QLineEdit()  # Empty field, to be manually updated for search
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text() # Name is extracted from the manually filled in data

        # THIS FEW LINES WERE NOT USED:-#################
        # Database connection for illustration-possibly.
        connection = DatabaseConnection().connect() #sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        data = cursor.fetchall()
        rows = list(data)
        print(rows)
        ######################################################

        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)  # This returns list of mathing names
        print("items: ", items)  # These are name objects
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)  # This highlights all matched names greyed out

        # cursor.close()
        # connection.close()


# Programme main loop/running loop of app:-
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
