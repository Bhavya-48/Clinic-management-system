import mysql.connector as sqltor
import datetime
from tabulate import tabulate
def setup_database():
    try:
        tempcon = sqltor.connect(host="localhost", user="root", password="root")
        tempcur = tempcon.cursor()
        tempcur.execute("CREATE DATABASE IF NOT EXISTS clinicdb")
        tempcon.commit()
        tempcon.close()

        # Reconnect to clinicdb
        global mycon, cur
        mycon = sqltor.connect(host="localhost", user="root", password="root", database="clinicdb")
        cur = mycon.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS patients(
        PatientID int primary key auto_increment, Name varchar(100), Age int,
        Gender char(3), Phone varchar(15), Address varchar(250))""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors(
        DoctorID int primary key auto_increment, Name varchar(100),
        Specialization varchar(100), Contact varchar(15))""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS appointment(
        AppID int primary key auto_increment, PatientID int references Patients(PatientID), DoctorID int references Doctors(DoctorID),
        App_Date date, App_Time time, Status varchar(50))""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS billing(
        BillID int primary key auto_increment, AppID int references Appointment(AppID), PatientID int references Patients(PatientID),
        DoctorID int references Doctors(DoctorID),
        Amount decimal(10,2), Payment_Mode varchar(20), Bill_Date date)""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_history(
        HisID int primary key auto_increment, PatientID int references Patients(PatientID), AppID int references Appointment(AppID),
        Diagnosis varchar(255), Report_Date date)""")
        mycon.commit()
    except sqltor.Error as e:
        print("Error setting up database", e)
        exit()
        
# Validation functions
def input_int(prompt="Enter a number: "):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")
def input_phone(prompt="Enter phone number: "):
    while True:
        phone = input(prompt).strip()
        if phone.isdigit() and len(phone) == 10:
            return phone
        print("Invalid phone number. Please enter a 10-digit number.")
def input_name(prompt="Enter your name: "):
    while True:
        name = input(prompt).strip()
        if name.replace(" ", "").isalpha() and len(name) > 0:
            return name
        print("Invalid name. Please use only letters and spaces.")
        
# Patient interface
def new_patient():
    try: 
        print("\t New Patient Registration")
        name=input_name("Enter your full name: ")
        age=input_int("Enter your age: ")
        gender=input("Enter your gender (M/F/0): ")
        phone=input_phone("Enter your phone number: ")
        add=input("Enter your address: ")
        cur.execute("INSERT INTO patients(Name,Age,Gender,Phone,Address) VALUES ('{}',{},'{}',{},'{}')".format(name,age,gender,phone,add))
        mycon.commit()
    except ValueError as e:
        print("Invalid input. Please re-check")
    
def patient_login():
    try:
        name=input_name("Enter your name: ")
        phone=input_phone("Enter your phone number: ")
        x="SELECT PatientID FROM patients WHERE name='{}' and phone='{}'"
        cur.execute(x.format(name,phone))
        data=cur.fetchone()
        if data:
             patientID=data[0]
             return patientID
        else:
             print("Patient not found")
    except sqltor.Error as e:
        print("Database error",e)
        
def patient_menu(patientID):
    while True:
        print("\n\t Patient Menu:")
        print("1. View my details")
        print("2. View my appointments")
        print("3. View my bills")
        print("4. View my medical hisory")
        print("5. Exit to main menu")
        choice=input_int("Enter your choice: ")
        try:
            if choice==1:
                cur.execute("SELECT * FROM patients WHERE PatientID={}".format(patientID,))
                data=cur.fetchall()
                if data:
                    headers = [i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==2:
                cur.execute("SELECT * FROM appointment WHERE PatientID={}".format(patientID,))
                data=cur.fetchall()
                if data:
                    headers = [i[0] for i in cur.description]
                    data = [(d[0], d[1], d[2], d[3].strftime("%d-%m-%Y"), 
                            (datetime.datetime.min + d[4]).time() if isinstance(d[4], datetime.timedelta) else d[4],
                             d[5]) for d in data]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                else:
                    print("No appointments found")
                    
            elif choice==3:
                cur.execute("SELECT * FROM billing WHERE PatientID={}".format(patientID,))
                data=cur.fetchall()
                if data:
                     headers = [i[0] for i in cur.description]
                     print(tabulate(data, headers=headers, tablefmt="grid"))
                else:
                    print("No bills found")
                    
            elif choice==4:
                cur.execute("SELECT * FROM patient_history WHERE PatientID={}".format(patientID,))
                data=cur.fetchall()
                if data:
                    headers = [i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                else:
                    print("No medical history found")
                    
            elif choice==5:
                print("Returning to main menu")
                break
            
            else:
                print("Invalid choice. Please select a number between 1 and 5")
        except sqltor.Error as e:
            print("Database error",e)

# Doctor interface        
def doctor_login():
    try:
        name=input("Enter your name: ")
        contact=input_phone("Enter your contact number: ")
        cur.execute("SELECT DoctorID FROM doctors WHERE Name='{}' AND Contact='{}'".format(name,contact))
        data=cur.fetchone()
        if data:
            doctorID=data[0]
            return doctorID
        else:
            print("Doctor not found")
    except sqltor.Error as e:
        print("Database error",e)
def doctor_menu(doctorID):
    while True:
        print("\n\t Doctor Menu:")
        print("1. View my details")
        print("2. View my appointments")
        print("3. Update appointment status")
        print("4. Add patient history")
        print("5. View patient history")
        print("6. Exit to main menu")
        choice=input_int("Enter your choice: ")
        try:
            if choice==1:
                cur.execute("SELECT * FROM doctors WHERE DoctorID={}".format(doctorID,))
                data=cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==2:
                cur.execute("SELECT * FROM appointment WHERE DoctorID={}".format(doctorID,))
                data=cur.fetchall()
                if data:
                    headers = [i[0] for i in cur.description]
                    data = [(d[0], d[1], d[2], d[3].strftime("%d-%m-%Y"), 
                            (datetime.datetime.min + d[4]).time() if isinstance(d[4], datetime.timedelta) else d[4],
                             d[5]) for d in data]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==3:
                AppID=int(input("Enter appointment ID: "))
                cur.execute("UPDATE appointment SET Status='Completed' WHERE AppID={}".format(AppID,))
                mycon.commit()
                cur.execute("SELECT * FROM appointment WHERE AppID={}".format(AppID,))
                data=cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                print("Successfully updated status to Completed")
                
            elif choice==4:
                PatID=input_int("Enter patient ID: ")
                AppID=input_int("Enter appointment ID: ")
                Diag=input("Enter diagnosis: ")
                cur.execute("INSERT INTO patient_history(PatientID, AppID, Diagnosis, Report_Date) VALUES ({},{},'{}', curdate())".format(PatID, AppID, Diag))
                mycon.commit()
                cur.execute("SELECT * FROM patient_history WHERE PatientID={} AND AppID={}".format(PatID, AppID))
                data=cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    data=[(d[0],d[1],d[2],d[3],d[4].strftime("%d-%m-%Y")) for d in data]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==5:
                PatID=input_int("Enter patient ID: ")
                cur.execute("SELECT * FROM patient_history WHERE PatientID={}".format(PatID,))
                data=cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    data=[(d[0],d[1],d[2],d[3],d[4].strftime("%d-%m-%Y")) for d in data]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==6:
                print("Returning to main menu")
                break
            else:
                print("Invalid choice. Please select a number between 1 and 6")
        except sqltor.Error as e:
            print("Database error",e)

# Staff interface
def staff_menu():
    while True:
        print("\n\t Staff Menu:")
        print("1. View Patient details")
        print("2. Update patient information")
        print("3. Delete Patient")
        print("4. Add doctor")
        print("5. View Doctor details")
        print("6. Update Doctor information")
        print("7. Schedule appointment")
        print("8. View appointment")
        print("9. Update appointment status")
        print("10. Generate bill")
        print("11. Generate income summary")
        print("12. View bills")
        print("13. Add patient history")
        print("14. View history")
        print("15. Exit to main menu")
        choice=input_int("Enter your choice: ")
        try:
            if choice==1:
                cur.execute("SELECT * FROM patients")
                data = cur.fetchall()
                headers = [i[0] for i in cur.description]
                print(tabulate(data, headers=headers, tablefmt="grid"))
                
            elif choice==2:
                PatID=input_int("Enter Patient ID to update: ")
                Name=input("Enter new Name: ")
                Age=input_int("Enter new Age: ")
                Gen=input("Enter new Gender (M/F/O): ")
                Ph=input_phone("Enter new Phone: ")
                Add=input("Enter new Address: ")
                cur.execute("UPDATE patients SET Name='{}', Age={}, Gender='{}', Phone={}, Address='{}'WHERE PatientID={}".format(Name,Age,Gen,Ph,Add,PatID))
                mycon.commit()
                print("Updation successful")
                cur.execute("SELECT * FROM patients WHERE PatientID={}".format(PatID,))
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==3:
                Name=input('Enter Patient Name which is to be deleted: ')
                cur.execute("DELETE FROM patients WHERE Name='{}'".format(Name,))
                print('Deleted successfully')
                
            elif choice==4:
                DocID=input_int('Enter Doctor ID: ')
                DocName=input("Enter the Doctor's Name: ")
                spec=input('Enter the Specialization: ')
                con=input('Enter the Contact info: ')
                cur.execute("INSERT INTO doctors values('{}',{},{},{})".format(DocID,DocName,spec,con))
                mycon.commit()
                print('Successfully added Doctor')
                
            elif choice==5:
                 cur.execute("SELECT * FROM doctors")
                 data = cur.fetchall()
                 headers = [i[0] for i in cur.description]
                 print(tabulate(data, headers=headers, tablefmt="grid"))
                 
            elif choice==6:
                DocID=input_int("Enter Doctor ID to update: ")
                DocName=input("Enter new Name: ")
                spec=input('Enter the Specialization: ')
                con=input('Enter the Contact info: ')
                cur.execute("UPDATE doctors SET Name='{}', Specialization='{}', Contact='{}' WHERE DoctorID={}".format(DocName,spec,con,DocID))
                mycon.commit()
                print("Updation successful")
                cur.execute("SELECT * FROM doctors WHERE DoctorID={}".format(DocID,))
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==7:
                AppID=input_int('Enter Appointment ID: ')
                PatID=input_int('Enter Patient ID: ')
                DocID=input_int('Enter Doctor ID: ')
                Date=input('Enter the Date (YYYY-MM-DD): ')
                Time=input('Enter the Time (HH:MM:SS): ')
                Stat=input('Enter the Current status: ')
                cur.execute("INSERT INTO appointment values ({},{},{},'{}','{}','{}')".format(AppID,PatID,DocID,Date,Time,Stat))
                data = cur.fetchall()
                mycon.commit()
                print("Insertion successfull")
                    
            elif choice==8:
                cur.execute("SELECT * FROM appointment ")
                data=cur.fetchall()
                if data:
                    headers = [i[0] for i in cur.description]
                    data = [(d[0], d[1], d[2], d[3].strftime("%d-%m-%Y"), 
                            (datetime.datetime.min + d[4]).time() if isinstance(d[4], datetime.timedelta) else d[4],   d[5]) for d in data]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==9:
                AppID=input_int('Enter Appointment ID: ')
                PatID=input_int('Enter Patient ID: ')
                DocID=input_int('Enter Doctor ID: ')
                Date=input('Enter the Date (YYYY-MM-DD): ')
                Time=input('Enter the Time (HH:MM:SS): ')
                Stat=input('Enter the Current status: ')
                cur.execute("UPDATE appointment SET PatientID={}, DoctorID={}, App_Date='{}',App_Time='{}',Status='{}' WHERE AppID={}".format(PatID,DocID,Date,Time,Stat,AppID))
                mycon.commit()
                print("Updation successful")
                cur.execute("SELECT * FROM doctors WHERE DoctorID={}".format(DocID,))
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==10:
                BillID=input_int('Enter Billing ID: ')
                cur.execute('SELECT * FROM billing WHERE BillID={}'.format(BillID,))
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==11:
                Date=input('Enter Billing Date (YYYY-MM-DD): ')
                cur.execute("SELECT SUM(Amount) AS daily_income FROM billing WHERE DATE(bill_date) = '{}'".format(Date))
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))

            elif choice==12:
                cur.execute('SELECT * FROM billing')
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==13:
                HisID=input_int('Enter Patient History ID: ')
                PatID=input_int('Enter Patient ID: ')
                AppID=input_int('Enter Appointment ID: ')
                Dia=input("Enter Patient's Diagnosis: ")
                RDate=input('Enter Report Date: ')
                cur.execute("INSERT INTO patient_history values({},{},{},'{}','{}')".format(HisID,PatID,AppID,Dia,RDate))
                data = cur.fetchall()
                mycon.commit()
                print("Insertion successfull")
                    
            elif choice==14:
                cur.execute('SELECT * FROM patient_history')
                data = cur.fetchall()
                if data:
                    headers=[i[0] for i in cur.description]
                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    
            elif choice==15:
                print("Returning to main menu")
                break
            else:
                print("Invalid choice. Please select a number between 1 and 15")
                
                
        except sqltor.Error as e:
            print("Database error",e)
            
# Menu for different interfaces                
def main_menu():
    while True:
        print("\n\t WELCOME TO SMARTCARE ENT CLINIC")
        print("Select your role: ")
        print("1. Patient")
        print("2. Doctor")
        print("3. Staff")
        print("4. Exit")
        role=input_int("Enter your role: ")
        if role==1:
            while True:
                setup_database()
                print("\n Are you an existing patient or a new patient?")
                print("1. Existing patient")
                print("2. New patient")
                ch=input_int("Enter your choice: ")
                if ch==1: 
                    patientID=patient_login()
                    if patientID:
                        patient_menu(patientID)
                        break
                elif ch== 2:
                    new_patient()
                    print("\nRegistration successful!")
                    print("Please visit the staff to schedule your first appointment.")
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2")
                    
        elif role==2:
            while True:
                setup_database()
                doctorID=doctor_login()
                if doctorID:
                    doctor_menu(doctorID)
                    break
                
        elif role==3:
            while True:
                setup_database()
                staff_menu()
                break
            
        elif role==4:
            print("Exiting system. Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 4.")
            
# Main program                
main_menu()
                
