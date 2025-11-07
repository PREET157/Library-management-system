from tkinter import *
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
import datetime
import tkinter
class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1500x800+0+0")
        
        # --- ROLE STORAGE ---
        self.user_role = None  # Stores 'Admin', 'Librarian', 'Student', etc.
        self.logged_in_prn = None # Stores the student PRN used for filtering
        
        # --- TKINTER VARIABLE SETUP ---
        self.member_var=StringVar()
        self.prn_var=StringVar() 
        self.id_var=StringVar()  
        self.firstname_var=StringVar()
        self.lastname_var=StringVar()
        self.address1_var=StringVar()
        self.address2_var=StringVar()
        self.postcode_var=StringVar()
        self.mobile_var=StringVar()
        self.bookid_var=StringVar() 
        self.booktitle_var=StringVar()
        self.author_var=StringVar()
        self.dateborrowed_var=StringVar()
        self.datedue_var=StringVar()
        self.daysonbook_var=StringVar() 
        self.lateratefine_var=StringVar()
        self.dateoverdue_var=StringVar()
        self.finalprice_var=StringVar()
        
        # --- LOGIN SETUP ---
        self.root.withdraw() # Hide the main window immediately
        self.login_root = Toplevel(self.root)
        self.login_root.title("User Login - Library System")
        self.login_root.geometry("300x150+500+250")
        self.login_root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.login_window()

    def login_window(self):
        """Creates the initial Toplevel login window."""
        lbl_user = Label(self.login_root, text="Username:", font=("arial", 12))
        lbl_user.grid(row=0, column=0, padx=10, pady=5, sticky=W)
        entry_user = Entry(self.login_root, textvariable=self.username_var, font=("arial", 12))
        entry_user.grid(row=0, column=1, padx=10, pady=5)

        lbl_pass = Label(self.login_root, text="Password:", font=("arial", 12))
        lbl_pass.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        entry_pass = Entry(self.login_root, textvariable=self.password_var, show="*", font=("arial", 12))
        entry_pass.grid(row=1, column=1, padx=10, pady=5)

        btn_login = Button(self.login_root, text="Login", command=self.check_login, font=("arial", 12, "bold"), width=10, bg="blue", fg="white")
        btn_login.grid(row=2, columnspan=2, pady=10)

    def get_prn_by_username(self, conn, username):
        """
        Helper function to find a student's PRN if their username is not their PRN.
        (E.g., if username is 'rajj', look up the PRN where FirstName='rajj' in Member table).
        """
        try:
            my_cursor = conn.cursor()
            # This query is a good guess based on the data provided in the images ('rajj' is a first name)
            prn_query = "SELECT PRN_No FROM Member WHERE First_Name = %s OR Last_Name = %s"
            my_cursor.execute(prn_query, (username, username))
            result = my_cursor.fetchone()
            if result:
                return result[0] # Return the found PRN_No  
            return None
        except mysql.connector.Error as err:
            print(f"Error fetching PRN by username: {err}")
            return None



    
    def check_login(self):
        """Authenticates user against the Users database table and fetches their role."""
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return

        conn = None
        user_data = None
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="newdata")
            my_cursor = conn.cursor()

            query = "SELECT username, user_role FROM Users WHERE username = %s AND password_hash = %s"
            my_cursor.execute(query, (username, password))
            user_data = my_cursor.fetchone() 

            if user_data:
                self.user_role = user_data[1]    
                
                # --- PRN RESOLUTION LOGIC (Unchanged) ---
                if self.user_role == 'Student':
                    prn = username
                    member_check = "SELECT PRN_No FROM Member WHERE PRN_No = %s"
                    my_cursor.execute(member_check, (username,))
                    
                    if my_cursor.fetchone() is None:
                        prn = self.get_prn_by_username(conn, username)
                        if not prn:
                            messagebox.showerror("Login Error", f"Student user '{username}' found, but no matching PRN/Member record could be located.")
                            return
                        
                    self.logged_in_prn = prn
                else:
                    self.logged_in_prn = username 
                
                # Login SUCCESS 
                self.login_root.destroy()
                self.root.deiconify() 
                self.root.update()      
                self.root.lift()        
                
                self.setup_main_ui()
              
                self.fetch_data() 
                # **********************************************
                
                messagebox.showinfo("Login Success", f"Welcome, {username}! Role: {self.user_role} (PRN: {self.logged_in_prn})")
            else:
                # Login FAILURE
                messagebox.showerror("Login Failed", "Invalid Username or Password.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect or query Users table. Error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def setup_main_ui(self):
        """Sets up the main application UI components based on the user's role."""
        
        # ======================== TITLE LABEL ========================
        lbltitle_text = f"LIBRARY MANAGEMENT SYSTEM ({self.user_role} VIEW)"
        lbltitle = Label(self.root, text=lbltitle_text, bg="powder blue", fg="green", bd=10, relief=RIDGE, font=("times new roman", 40, "bold"),pady=3)
        lbltitle.pack(side=TOP, fill=X)

        # ======================== MAIN FRAME (Container for sub-frames) ========================
        frame=Frame(self.root, bd=10, relief=RIDGE, padx=10, bg="powder blue")
        frame.place(x=0, y=100, width=1350 , height=380)
        
        # ======================== Frame LEFT (Library Membership Info) ========================
        DataFrameLeft=LabelFrame(frame, text="Library Membership Info", bg="powder blue", fg="green", bd=12, relief=RIDGE, font=("times new roman", 20, "bold"))
        DataFrameLeft.place(x=0,y=5,width=860,height=350) 
        
      
     
        input_state = NORMAL if self.user_role in ('Admin', 'Librarian') else DISABLED
        # --- END RESTRICTION ---
        
        # Data Entry Fields (Layout unchanged from original)
        fields = [
            ("Member Type", 0, self.member_var, ttk.Combobox, ("Admin Staf","Student","Lecturer")),
            ("PRN No (Member ID)", 1, self.prn_var, Entry),
            ("ID No:", 2, self.id_var, Entry),
            ("FirstName", 3, self.firstname_var, Entry),
            ("Lastname", 4, self.lastname_var, Entry),
            ("Address1", 5, self.address1_var, Entry),
            ("Address2", 6, self.address2_var, Entry),
            ("Post Code", 7, self.postcode_var, Entry),
            ("Mobile", 8, self.mobile_var, Entry)
        ]

        for i, (text, row, var, widget, *values) in enumerate(fields):
            lbl = Label(DataFrameLeft, bg="powder blue", text=text, font=("times new roman", 12, "bold"), padx=1, pady=4)
            lbl.grid(row=row, column=0, sticky=W)
            if widget == ttk.Combobox:
                w = widget(DataFrameLeft, font=("times new roman", 12, "bold"), width=25, state=input_state, textvariable=var)
                w['value'] = values[0]
            else:
                w = widget(DataFrameLeft, font=("times new roman", 12, "bold"), width=25, state=input_state, textvariable=var)
            w.grid(row=row, column=1)

        # Book/Transaction Details (Right side of left frame)
        book_fields = [
            ("Book Id:", 0, self.bookid_var, Entry),
            ("Book Title:", 1, self.booktitle_var, Entry),
            ("Author Name:", 2, self.author_var, Entry),
            ("Date Borrowed:", 3, self.dateborrowed_var, Entry),
            ("Date Due:", 4, self.datedue_var, Entry),
            ("Days On Book:", 5, self.daysonbook_var, Entry),
            ("Late Return Fine:", 6, self.lateratefine_var, Entry),
            ("Date Over Due:", 7, self.dateoverdue_var, Entry),
            ("Actual Price:", 8, self.finalprice_var, Entry)
        ]

        for i, (text, row, var, widget) in enumerate(book_fields):
            lbl = Label(DataFrameLeft, bg="powder blue", text=text, font=("arial", 12, "bold"), padx=1, pady=4)
            lbl.grid(row=row, column=2, sticky=W)
            w = widget(DataFrameLeft, font=("arial", 12, "bold"), width=25, state=input_state, textvariable=var)
            w.grid(row=row, column=3)


        # ======================== Frame RIGHT (Book Details Listbox) =======================
        DataFrameRight=LabelFrame(frame, text="Book Details", bg="powder blue", fg="green", bd=12, relief=RIDGE, font=("times new roman", 20, "bold"))
        DataFrameRight.place(x=870,y=5,width=450,height=350) 

        self.txtBox=Text(DataFrameRight, font=("arial",10,"bold"),width=32,height=16,padx=2,pady=6)
        self.txtBox.grid(row=0,column=2)

        listScrollbar=Scrollbar(DataFrameRight)
        listScrollbar.grid(row=0,column=1,sticky="ns")

        listBoooks=['Head Firt Book','Learn Python The Hard Way','Python Programming','Secrete Rahshy','Python CookBook','Into to Machine','Machine tecno','My Python','Joss Ellif guru','Elite Jungle python','Jungli Python','Machine python','Advance Python','Inton Python','RedChilli Python','Ishq Python']

        def SelectBook(event=""):
            # Logic to populate fields when a book is selected from the list
            try:
                value=str(listBox.get(listBox.curselection()))
                x=value
                book_data = {
                    "Head Firt Book": ("BKID5454", "Python Manual", "Paul Berry", "Rs.50", "Rs.788"),
                    "Learn Python The Hard Way": ("BKID8796", "Basic Of Python", "ZED A. SHAW", "Rs.25", "Rs.725"),
                    "Python Programming": ("BKID1001", "Python Programming", "John M. Zelle", "Rs.30", "Rs.650"),
                    "Secrete Rahshy": ("BKID2002", "The Secret History", "Donna Tartt", "Rs.15", "Rs.550"),
                    "Python CookBook": ("BKID3003", "Python Cookbook", "David Beazley", "Rs.40", "Rs.910"),
                    "Into to Machine": ("BKID4004", "Intro to Machine Learning", "Andrew Ng", "Rs.60", "Rs.1200"),
                    "Machine tecno": ("BKID5005", "Machine Technology", "Robert W. Wait", "Rs.35", "Rs.750"),
                    "My Python": ("BKID6006", "My Python Journey", "Corey Schafer", "Rs.20", "Rs.499"),
                    "Joss Ellif guru": ("BKID7007", "Java Programming Guru", "Kathy Sierra", "Rs.30", "Rs.800"),
                    "Elite Jungle python": ("BKID8008", "Elite Python Guide", "Al Sweigart", "Rs.45", "Rs.950"),
                    "Jungli Python": ("BKID9009", "Jungle Book (Python Ed.)", "Rudyard K.", "Rs.10", "Rs.399"),
                    "Machine python": ("BKID1110", "Machine Learning with Python", "Pedro Domingos", "Rs.55", "Rs.1150"),
                    "Advance Python": ("BKID1211", "Advanced Python Guide", "Luciano Ramalho", "Rs.50", "Rs.1050"),
                    "Inton Python": ("BKID1312", "Introduction to Python", "Guido van Rossum", "Rs.25", "Rs.600"),
                    "RedChilli Python": ("BKID1413", "Web Dev with Django", "Simon W.", "Rs.40", "Rs.850"),
                    "Ishq Python": ("BKID1514", "Python Love Story", "V.K. Singh", "Rs.15", "Rs.450")
                }
                if x in book_data:
                    b_id, b_title, b_author, b_fine, b_price = book_data[x]
                    self.bookid_var.set(b_id)
                    self.booktitle_var.set(b_title)
                    self.author_var.set(b_author)
                    self.lateratefine_var.set(b_fine)
                    self.finalprice_var.set(b_price)

                    # Date calculations
                    d1 = datetime.date.today()
                    d2 = datetime.timedelta(days=15)
                    d3 = d1 + d2
                    self.dateborrowed_var.set(d1)
                    self.datedue_var.set(d3)
                    self.daysonbook_var.set("15") 
                    self.dateoverdue_var.set("NO")
            except IndexError:
              
                pass


        listBox=Listbox(DataFrameRight,font=("arial",10,"bold"),width=20,height=16)
        listBox.bind("<<ListboxSelect>>",SelectBook)
        listBox.grid(row=0,column=0,padx=4)
        listScrollbar.config(command=listBox.yview)

        for item in listBoooks:
          listBox.insert(END,item)
        
        # ========================Buttons Frame=======================
        Framebutton=Frame(self.root,bd=5,relief=RIDGE,padx=0,bg="powder blue")
        Framebutton.place(x=0,y=480,width=1530,height=50)

        # --- DYNAMIC BUTTON SETUP (Hides CRUD buttons for students) ---
        self.setup_buttons_by_role(Framebutton)
        # --- END DYNAMIC BUTTON SETUP ---

        
        # ======================== Information Frame (Display Table/Treeview) =======================
        FrameDetails=Frame(self.root,bd=12,relief=RIDGE,padx=20,bg="powder blue") 
        FrameDetails.place(x=0,y=530,width=1530,height=170)
        
        Table_frame=Frame(FrameDetails,bd=6,relief=RIDGE,bg="powder blue")
        Table_frame.place(x=0,y=2,width=1300,height=140)

        xscroll=ttk.Scrollbar(Table_frame,orient=HORIZONTAL)
        yscroll=ttk.Scrollbar(Table_frame,orient=VERTICAL)

        # Updated Treeview columns to match the JOIN query result order
        self.library_table=ttk.Treeview(Table_frame,column=("memebertype","prrno","title","firtname","lastname","adress1","adress2","postid","mobile","bookid","booktitle","auther","dateborrowed","datedue","days","laterreturnfine","dateoverdue","finalprice"),
                                            xscrollcommand=xscroll.set,yscrollcommand=yscroll.set)
        
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        self.library_table.grid(row=0, column=0, sticky="nsew")
        Table_frame.grid_rowconfigure(0, weight=1)
        Table_frame.grid_columnconfigure(0, weight=1)
        
        # COLUMN HEADINGS SETUP
        self.library_table.heading("memebertype",text="Member Type")
        self.library_table.heading("prrno",text="PRN No.")
        self.library_table.heading("title",text="Title")
        self.library_table.heading("firtname",text="First Name")
        self.library_table.heading("lastname",text="Last Name")
        self.library_table.heading("adress1",text="Address1")
        self.library_table.heading("adress2",text="Address2")
        self.library_table.heading("postid",text="Post ID")
        self.library_table.heading("mobile",text="Mobile Number")
        self.library_table.heading("bookid",text="Book ID")
        self.library_table.heading("booktitle",text="Book Title")
        self.library_table.heading("auther",text="Author")
        self.library_table.heading("dateborrowed",text="Date Borrowed")
        self.library_table.heading("datedue",text="Date Due")
        self.library_table.heading("days",text="Days On Book") # Calculated client-side
        self.library_table.heading("laterreturnfine",text="LateReturnFine")
        self.library_table.heading("dateoverdue",text="DateOverDue")
        self.library_table.heading("finalprice",text="Actual Price")

        self.library_table['show']="headings"
        xscroll.config(command=self.library_table.xview)
        yscroll.config(command=self.library_table.yview)

        # Set Column Widths
        for col in self.library_table['column']:
            self.library_table.column(col, width=100)
            
        # NOTE: fetch_data() is NOT called here anymore. It's called after successful login.
        self.library_table.bind("<ButtonRelease-1>",self.get_cursor)

    
    def setup_buttons_by_role(self, frame):
        """Conditionally creates buttons based on the user's role."""
        
        # Standard buttons visible to everyone
        Button(frame, text="Show Data", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.showData).grid(row=0, column=0)
        Button(frame, text="Exit", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.iExit).grid(row=0, column=5)
        
        # Buttons visible only to Admin/Librarian (CRUD functionality)
        if self.user_role in ('Admin', 'Librarian'):
            Button(frame, text="Add Transaction", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.add_data).grid(row=0, column=1)
            Button(frame, text="Update", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.update).grid(row=0, column=2)
            Button(frame, text="Delete Transaction", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.delete).grid(row=0, column=3)
            Button(frame, text="Reset", font=("arial", 11, "bold"), width=23, bg="blue", fg="white", command=self.reset).grid(row=0, column=4)
        else:
            
            Button(frame, text="Clear Form", font=("arial", 11, "bold"), width=23, bg="gray", fg="white", command=self.reset).grid(row=0, column=1)


    # ----------------------------------------------------------------------
    ## ➕ ADD DATA (Permissions Check)
    def add_data(self):
        if self.user_role not in ('Admin', 'Librarian'):
            messagebox.showwarning("Permission Denied", "Only administrators can add transactions.")
            return
            
        if not self.prn_var.get() or not self.bookid_var.get():
            messagebox.showerror("Error", "PRN No and Book ID fields cannot be empty for a transaction.")
            return

        conn = None
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="newdata")
            my_cursor = conn.cursor()
            
            # 1. Insert/Update Member details
            member_check = "SELECT PRN_No FROM Member WHERE PRN_No = %s"
            my_cursor.execute(member_check, (self.prn_var.get(),))
            
            member_values = (
                self.member_var.get(), self.id_var.get(), self.firstname_var.get(), self.lastname_var.get(), 
                self.address1_var.get(), self.address2_var.get(), self.postcode_var.get(), self.mobile_var.get(), 
                self.prn_var.get()
            )
            
            if my_cursor.fetchone() is None:
                # INSERT Member if they don't exist
                member_query = """
                    INSERT INTO Member (MemberType, Title, First_Name, Last_Name, Address1, Address2, Post_ID, Mobile_Number, PRN_No) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                my_cursor.execute(member_query, member_values)
            else:
                # UPDATE Member if they do exist
                member_update_query = """
                    UPDATE Member SET MemberType=%s, Title=%s, First_Name=%s, Last_Name=%s, 
                    Address1=%s, Address2=%s, Post_ID=%s, Mobile_Number=%s
                    WHERE PRN_No=%s
                """
                my_cursor.execute(member_update_query, member_values)

            
            # 2. Insert new Book Transaction
            transaction_query = """
                INSERT INTO BookTransaction (PRN_No, Book_ID, Date_Of_Borrow, Date_Due, DateOverDue, LateReturnFine)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            transaction_values = (
                self.prn_var.get(), self.bookid_var.get(), self.dateborrowed_var.get(), 
                self.datedue_var.get(), self.dateoverdue_var.get(), self.lateratefine_var.get()
            )
            my_cursor.execute(transaction_query, transaction_values)
            
            conn.commit()
            self.fetch_data()
            self.reset()    
            messagebox.showinfo("Success", "New Book Transaction recorded successfully.")
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to insert record. Ensure PRN/BookID are valid keys. Error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    # ----------------------------------------------------------------------
 
    def fetch_data(self):
        # Only proceed if a user role has been set (i.e., after successful login)
        if self.user_role is None:
            return 
            
        self.library_table.delete(*self.library_table.get_children()) 
        
        conn = None
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="newdata")
            my_cursor = conn.cursor()
            
            # Base JOIN Query (fetches 17 columns)
            base_query = """
                SELECT 
                    M.MemberType, M.PRN_No, M.Title, M.First_Name, M.Last_Name, M.Address1, M.Address2, M.Post_ID, M.Mobile_Number, 
                    B.Book_ID, B.Book_Title, B.Author, 
                    T.Date_Of_Borrow, T.Date_Due, T.LateReturnFine, T.DateOverDue, 
                    B.Actual_Price
                FROM 
                    Member M
                INNER JOIN 
                    BookTransaction T ON M.PRN_No = T.PRN_No
                INNER JOIN 
                    Book B ON T.Book_ID = B.Book_ID
            """
            
            parameters = []
            
            # --- CONDITIONAL FILTERING FOR STUDENT VIEW ---
            if self.user_role == 'Student' and self.logged_in_prn:
                # Student only sees records matching their PRN_No
                final_query = base_query + " WHERE M.PRN_No = %s"
                parameters.append(self.logged_in_prn)
            else:
                # Admin/Librarian sees all records
                final_query = base_query
            
            # --- DIAGNOSTIC PRINT ---
            if self.user_role == 'Student':
                print("-" * 50)
                print("ROLE:", self.user_role)
                print("LOGGED IN PRN (FILTER):", self.logged_in_prn)
                # Note: Using str(parameters) to handle the tuple/list printing cleanly for diagnosis
                try:
                    print("EXECUTING QUERY:", final_query % tuple(parameters))
                except TypeError:
                    print("EXECUTING QUERY:", final_query) # Handles case with no parameters
                print("-" * 50)
      
                
            my_cursor.execute(final_query, tuple(parameters))
            
            rows = my_cursor.fetchall()
            
            if len(rows) == 0 and self.user_role == 'Student':
                print(f"SQL returned 0 rows for PRN: {self.logged_in_prn}. Check your MySQL data.")
            
            if len(rows) != 0:
                for row in rows:
                    # Calculate 'Days On Book' (the 18th column) client-side
                    try:
                       
                        date_borrowed = datetime.datetime.strptime(str(row[12]), '%Y-%m-%d').date()
                        days_on_book = (datetime.date.today() - date_borrowed).days
                    except ValueError:
                        days_on_book = 'N/A' 
                    
                    # Construct the final row tuple for the 18 columns in the Treeview
                    final_row = list(row[:14]) + [days_on_book] + list(row[14:]) 
                    
                    self.library_table.insert("", END, values=final_row)
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching data: {err}")
            print(f"SQL ERROR DURING FETCH: {err}") 
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during fetch: {str(e)}")
            print(f"PYTHON ERROR DURING FETCH: {e}") 
        finally:
            if conn and conn.is_connected():
                conn.close()
 
    # ----------------------------------------------------------------------
    ## 🔄 UPDATE (Permissions Check)
    def update(self):
        if self.user_role not in ('Admin', 'Librarian'):
            messagebox.showwarning("Permission Denied", "Only administrators can update transactions.")
            return
            
        if not self.prn_var.get() or not self.bookid_var.get():
            messagebox.showerror("Error", "Both PRN No and Book ID must be selected to update a transaction record.")
            return

        conn = None
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="newdata")
            my_cursor = conn.cursor()
            
            # 1. Update Member details (if member info changed)
            member_update_query = """
                UPDATE Member SET 
                    MemberType=%s, Title=%s, First_Name=%s, Last_Name=%s, Address1=%s, 
                    Address2=%s, Post_ID=%s, Mobile_Number=%s
                WHERE PRN_No=%s
            """
            member_update_values = (
                self.member_var.get(), self.id_var.get(), self.firstname_var.get(), self.lastname_var.get(), 
                self.address1_var.get(), self.address2_var.get(), self.postcode_var.get(), self.mobile_var.get(), 
                self.prn_var.get()
            )
            my_cursor.execute(member_update_query, member_update_values)
            
            # 2. Update Book Transaction details (if dates/fine changed)
            transaction_update_query = """
                UPDATE BookTransaction SET 
                    Date_Of_Borrow=%s, Date_Due=%s, LateReturnFine=%s, DateOverDue=%s
                WHERE PRN_No=%s AND Book_ID=%s
            """
            transaction_update_values = (
                self.dateborrowed_var.get(), self.datedue_var.get(), self.lateratefine_var.get(), 
                self.dateoverdue_var.get(), self.prn_var.get(), self.bookid_var.get()
            )
            my_cursor.execute(transaction_update_query, transaction_update_values)
            
            conn.commit()
            self.fetch_data()
            self.reset()
            messagebox.showinfo("Success", "Member and Transaction records updated successfully")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update record. Error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    # ----------------------------------------------------------------------
    ## ❌ DELETE (Permissions Check)
    def delete(self):
        if self.user_role not in ('Admin', 'Librarian'):
            messagebox.showwarning("Permission Denied", "Only administrators can delete transactions.")
            return
            
        if not self.prn_var.get() or not self.bookid_var.get():
            messagebox.showerror("Error", "PRN No and Book ID must be selected to delete a transaction.")
            return
        
        iDelete = messagebox.askyesno("Library Management System", f"Confirm delete transaction for PRN {self.prn_var.get()} and Book ID {self.bookid_var.get()}?")
        if iDelete == NO:
            return

        conn = None
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="newdata")
            my_cursor = conn.cursor()
            
            # Delete the specific transaction record
            query = "DELETE FROM BookTransaction WHERE PRN_No=%s AND Book_ID=%s"
            value = (self.prn_var.get(), self.bookid_var.get())
            my_cursor.execute(query, value)
            
            conn.commit()
            self.fetch_data()
            self.reset()
            messagebox.showinfo("Success", "Book transaction deleted successfully.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete record. Error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if conn and conn.is_connected():
                conn.close()
            
    # ----------------------------------------------------------------------
    ## Helper Functions 

    def get_cursor(self, event=""):
        """Populates form fields when a row in the Treeview is selected."""
        cursor_row = self.library_table.focus()
        content = self.library_table.item(cursor_row)
        row = content['values']
        
        # Mapping must match the order of columns in fetch_data + the calculated DaysOnBook
        self.member_var.set(row[0])
        self.prn_var.set(row[1])
        self.id_var.set(row[2])
        self.firstname_var.set(row[3])
        self.lastname_var.set(row[4])
        self.address1_var.set(row[5])
        self.address2_var.set(row[6])
        self.postcode_var.set(row[7])
        self.mobile_var.set(row[8])
        self.bookid_var.set(row[9])
        self.booktitle_var.set(row[10])
        self.author_var.set(row[11])
        self.dateborrowed_var.set(row[12])
        self.datedue_var.set(row[13])
        self.daysonbook_var.set(row[14]) 
        self.lateratefine_var.set(row[15])
        self.dateoverdue_var.set(row[16])
        self.finalprice_var.set(row[17])

    def showData(self):
        """Displays current form data in the large text box."""
        self.txtBox.delete("1.0", END)
        self.txtBox.insert(END, "Member Type:\t\t" + self.member_var.get() + "\n")
        self.txtBox.insert(END, "PRN No:\t\t" + self.prn_var.get() + "\n")
        self.txtBox.insert(END, "ID No:\t\t" + self.id_var.get() + "\n")
        self.txtBox.insert(END, "Firstname:\t\t" + self.firstname_var.get() + "\n")
        self.txtBox.insert(END, "Lastname:\t\t" + self.lastname_var.get() + "\n")
        self.txtBox.insert(END, "Address1:\t\t" + self.address1_var.get() + "\n")
        self.txtBox.insert(END, "Address2:\t\t" + self.address2_var.get() + "\n")
        self.txtBox.insert(END, "Post Code:\t\t" + self.postcode_var.get() + "\n")
        self.txtBox.insert(END, "Mobile No:\t\t" + self.mobile_var.get() + "\n")
        self.txtBox.insert(END, "Book ID:\t\t" + self.bookid_var.get() + "\n")
        self.txtBox.insert(END, "Book Title:\t\t" + self.booktitle_var.get() + "\n")
        self.txtBox.insert(END, "Author:\t\t" + self.author_var.get() + "\n")
        self.txtBox.insert(END, "DateBorrowed:\t\t" + self.dateborrowed_var.get() + "\n")
        self.txtBox.insert(END, "DateDue:\t\t" + self.datedue_var.get() + "\n")
        self.txtBox.insert(END, "DaysOnBook:\t\t" + self.daysonbook_var.get() + "\n")
        self.txtBox.insert(END, "LateReturnFine:\t\t" + self.lateratefine_var.get() + "\n")
        self.txtBox.insert(END, "DateOverDue:\t\t" + self.dateoverdue_var.get() + "\n")
        self.txtBox.insert(END, "Actual Price:\t\t" + self.finalprice_var.get() + "\n")

    def reset(self):
        """Resets all input fields and the text box."""
        self.member_var.set("")
        self.prn_var.set("")
        self.id_var.set("")
        self.firstname_var.set("")
        self.lastname_var.set("")
        self.address1_var.set("")
        self.address2_var.set("")
        self.postcode_var.set("")
        self.mobile_var.set("")
        self.bookid_var.set("")
        self.booktitle_var.set("")
        self.author_var.set("")
        self.dateborrowed_var.set("")
        self.datedue_var.set("")
        self.daysonbook_var.set("")
        self.lateratefine_var.set("")
        self.dateoverdue_var.set("")
        self.finalprice_var.set("")
        self.txtBox.delete("1.0", END)

    def iExit(self):
        """Asks for confirmation before exiting."""
        iExit = tkinter.messagebox.askyesno("Library management System", "Do you want to exit")
        if iExit > 0:
            self.root.destroy()
            return
            
if __name__ == "__main__":
    root = Tk()
    obj = LibraryManagementSystem(root)
    root.mainloop()