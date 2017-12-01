from tabulate import tabulate
import time
from datetime import datetime,date

import cx_Oracle
con=cx_Oracle.connect("system/aditya23@localhost/xe")
cur=con.cursor()

#initializing variables
c1=0
c2=0
c3=0
ch1="Y"
ch2="Y"
ch3="Y"


class Admin:
    def __init__(self):
        self.vacc=0
    @staticmethod
    def admin_validate():
        flag=0
        for i in range(0,3):
            vid=input("Enter ADMIN ID")    
            cur.execute('select adm_id from ADI.admin')
            row = cur.fetchall()
            num = list(sum(row, ()))
            if vid in num:
                vpw=raw_input("Enter password")
                cur.execute('select adm_pw from ADI.admin')
                res = cur.fetchall()
                num2=list(sum(res,()))
                if vpw not in num2:
                    print "Wrong Password"
                    continue
                else:
                    flag=1
                    break
            else:
                print "Wrong Input"
        if(flag==1):
            print "Successful login"
            return 1
        else:
            print "Cannot login"
            return 2
    def history(self):
        self.vacc=input("Enter your account number ")    
        cur.execute('select accno from ADI.closed')
        lt=cur.fetchall()
        num=list(sum(lt, ()))
        # to check if account is valid
        if self.vacc in num:
            cur.execute('''select dt_close,accno from ADI.closed where accno=:param1 order by dt_close''',{'param1':self.vacc})
            table=cur.fetchall()
            print tabulate(table, headers=['date','accno'])
        else:
            print "Invalid account number"
                   
        

   
def validate():
    flag=0
    p=0
    for i in range(0,3):
        vid=input("Enter customer id ")    
        cur.execute('select c_id from ADI.customer')
        row = cur.fetchall()
        num = list(sum(row, ()))
        if vid in num:
            vpw=raw_input("Enter your password:")
            cur.execute('select pwd from ADI.customer where c_id=:param1', {'param1': vid})
            res = cur.fetchall()
            num2=list(sum(res,()))
            if vpw not in num2:
                print "Wrong password"
                p=p+1
                if p is 3:
                     cur.execute('''INSERT INTO ADI.blocked(select * from ADI.customer where c_id=:param1)''',{'param1':vid})
                     cur.execute('''delete from ADI.customer where c_id=:param''',{'param':vid})
                     con.commit()
                else:
                    continue
            else:
                flag=1
                break
        else:
            print "Wrong input"
    if(flag==1):
        print "Successful login"
        return vid
    else:
        print "Cannot login"
        return "fail"    

class Account:
    def __init__(self,myacc):
        self.vacc=0
        self.myacc=myacc
    def validate_acc_depo(self):
        self.vacc=input("Enter your account:")    
        cur.execute('select accno from ADI.customer')
        lt=cur.fetchall()
        num=list(sum(lt, ()))
        if self.vacc in num:
            cur.execute('select typ from ADI.customer where accno=:param1',{'param1':self.vacc})
            re=cur.fetchone()
            return re[0]
        else:
            print "Invalid account number"
        
    def validate_acc_wdr(self,myacc):
        cur.execute('select typ from ADI.customer where accno=:param1',{'param1':self.myacc})
        re1=cur.fetchone()
        
        return re1[0]
        
    def printstatement(self):
        self.vacc=input("Enter your account number:")    
        cur.execute('select accno from ADI.customer')
        lt=cur.fetchall()
        num=list(sum(lt, ()))
        if self.vacc in num:
            date_from=raw_input("Enter date from in dd-mm-yyyy:")
            date_to=raw_input("enter date to in dd-mm-yyyy:")

            #comparing dates
            newdate_from=time.strptime(date_from,"%d-%m-%Y")
            newdate_to=time.strptime(date_to,"%d-%m-%Y")
            
            if newdate_from<newdate_to:
                cur.execute('''select * from ADI.mini where accno=:param1 and
                dot between to_date(:param2,'dd-mm-yyyy') and to_date(:param3,'dd-mm-yyyy')
                order by dot''',{'param1':self.vacc,'param2':date_from,'param3':date_to})
                table=cur.fetchall()
                print tabulate(table, headers=['accno','dot','t_typ','amount','balance'])
            else:
                print "date_from cannot be greater than date_to"
        else:
            print "invalid account number"
    def transfer(self,myacc):
        self.vacc=input("enter acc ")    
        cur.execute('select accno from ADI.customer')
        lt=cur.fetchall()
        num=list(sum(lt, ()))
        #if account you want to deposit in is valid
        if self.vacc in num:
            tnsfr_amt=input("Enter amount you want to transfer")
            #extract account type of depositer
            cur.execute('select typ from ADI.customer where accno=:param1',{'param1':self.myacc})
            
            a_typ=cur.fetchone()
            #now withdrawing balance from own account according to type

            if a_typ[0]==1:
                te="DEBIT"
                #extracting balance to check that withdrawl does not exceed balance
                cur.execute('select balance from ADI.customer where accno=:param1',{'param1':self.myacc})
                old_balance=cur.fetchone()

                if (tnsfr_amt<old_balance and tnsfr_amt>0):
                    cur.execute('update ADI.customer set balance=balance-:param1 where accno=:param2',{'param1':tnsfr_amt,'param2':self.myacc})
                    #extract new balance
                    cur.execute('select balance from ADI.customer where accno=:param1',{'param1':self.myacc})
                    num=cur.fetchone()
                    new_balance=int(num[0])
                    
                    #entering date
                    date1=raw_input("Enter date in this format:dd-mm-yyyy:")
                    statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
                    cur.execute(statement,(self.myacc,date1,te,tnsfr_amt,new_balance))
                    con.commit()
                else:
                    print"The amount to be withdrawn is greater than available balance"

            elif a_typ[0]==2:
                te="DEBIT"
                
                #extract balance to check if min is 5K
                cur.execute('select balance from ADI.customer where accno=:param1',{'param1':self.myacc})
                num=cur.fetchone()
                old_balance=int(num[0])

                if (tnsfr_amt<old_balance and (old_balance-tnsfr_amt>5000)and tnsfr_amt>0):
                    cur.execute('update ADI.customer set balance=balance-:param1 where accno=:param2',{'param1':tnsfr_amt,'param2':self.myacc})
                    #extract new balance
                    cur.execute('select balance from ADI.customer where accno=:param1',{'param1':self.myacc})
                    num=cur.fetchone()
                    new_balance=int(num[0])
                    #entering date
                    date1=raw_input("enter in this format:dd-mm-yyyy")
                    statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
                    cur.execute(statement,(self.myacc,date1,te,tnsfr_amt,new_balance))
                    con.commit()
                else:
                    print"The amount to be withdrawn is greater than available balance" 

            #now depositing in the given account

            te="CREDIT"
            #
            if tnsfr_amt>0:
                cur.execute('update ADI.customer set balance=balance+:param1 where accno=:param2',{'param1':tnsfr_amt,'param2':self.vacc})
                #extract new balance
                cur.execute('select balance from ADI.customer where accno=:param1',{'param1':self.vacc})
                num=cur.fetchone()
                new_balance=int(num[0])

                #entering date
                statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
                cur.execute(statement,(self.vacc,date1,te,tnsfr_amt,new_balance))
                con.commit()
                print "money transferred"
            else:
                print"Adding negative is balance not posssible"
        else:
            print "invalid account number"
    def close(self,myacc):
        date=raw_input("enter date in format:dd-mm-yyyy")
        #inputting into closed table
        cur.execute('''insert into ADI.closed values(:param,to_date(:param2,'dd-mm-yyyy'))''',{'param':self.myacc,'param2':date})
        #deleting from customer table
        cur.execute('''delete from ADI.customer where accno=:param1''',{'param1':self.myacc})
        con.commit()
       
               
class Savings(Account):
    def __init__(self,Account):
        pass
    def deposit(self,Account):
        te="CREDIT"            
        add_balance=input("Enter amount to be deposited")
        if add_balance>0:
            cur.execute('update ADI.customer set balance=balance+:param1 where accno=:param2',{'param1':add_balance,'param2':Account.vacc})
            #extract new balance
            cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.vacc})
            num=cur.fetchone()
            new_balance=int(num[0])
            
            #entering date
            date1=raw_input("Enter date in this format:dd-mm-yyyy:")
            statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
            cur.execute(statement,(Account.vacc,date1,te,add_balance,new_balance))
            print "money deposited"
            con.commit()
        else:
            print"Adding negative balance not possible"
    def wdraw(self,Account):
        te="DEBIT"
       
        sub_balance=input("Enter amount to be withdrawn")
        #extracting balance to check that withdrawl does not exceed balance
        cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.myacc})
        old_balance=cur.fetchone()

        if (sub_balance<old_balance and sub_balance>0):
            cur.execute('update ADI.customer set balance=balance-:param1 where accno=:param2',{'param1':sub_balance,'param2':Account.myacc})
            #extract new balance
            cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.myacc})
            num=cur.fetchone()
            new_balance=int(num[0])
            
            #entering date
            date1=raw_input("Enter date in this format:dd-mm-yyyy:")
            statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
            cur.execute(statement,(Account.myacc,date1,te,sub_balance,new_balance))
            print "money withdrawn"
            con.commit()
        else:
            print"The amount to be withdrawn is greater than available balance"
            

class Current(Account):
    def __init__(self,Account):
        pass
    def deposit(self,Account):
        te="CREDIT"
        add_balance=input("Enter amount to be deposited")
        if add_balance>0:
            cur.execute('update ADI.customer set balance=balance+:param1 where accno=:param2',{'param1':add_balance,'param2':Account.vacc})
            #extract new balance
            cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.vacc})
            num=cur.fetchone()
            new_balance=int(num[0])

            #entering date
            date1=raw_input("Enter in date this format:dd-mm-yyyy")
            statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
            cur.execute(statement,(Account.vacc,date1,te,add_balance,new_balance))
            print "money deposited"
            con.commit()
        else:
            print"Adding neg. balance not posssible"
    def wdraw(self,Account):
        te="DEBIT"
        sub_balance=input("Enter ammount to be withdrawn")
        #extract balance to check if min is 5K
        cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.myacc})
        num=cur.fetchone()
        old_balance=int(num[0])

        if (sub_balance<old_balance and (old_balance-sub_balance>5000) and sub_balance>0):
            cur.execute('update ADI.customer set balance=balance-:param1 where accno=:param2',{'param1':sub_balance,'param2':Account.myacc})
            #extract new balance
            cur.execute('select balance from ADI.customer where accno=:param1',{'param1':Account.myacc})
            num=cur.fetchone()
            new_balance=int(num[0])
            #entering date
            date1=raw_input("Enter date in this format:dd-mm-yyyy:")
            statement='''insert into ADI.mini(accno,dot,t_typ,amount,balance) values(:1,to_date(:2,'dd-mm-yyyy'),:3,:4,:5)'''
            cur.execute(statement,(Account.myacc,date1,te,sub_balance,new_balance))
            print "money withdrawn"
            con.commit()
        else:
            print"The amount to be withdrawn is greater than available balance"            

class Customer():
    def __init__(self):
        self.c_id=0
        self.fname=""
        self.lname=""
        self.adrs1=""
        self.adrs2=""
        self.city=""
        self.state=""
        self.pincode=248001
        self.typ=0
        self.balance=0
        self.pwd=""
        self.accno=0
    def inpt(self):
        pincode=123456
        print "enter details:"
        self.fname=raw_input("First name:")
        self.lname=raw_input("Last name:")
        self.adrs1=raw_input("address line 1")
        self.adrs2=raw_input("address line 2")
        self.city=raw_input("city:")
        self.state=raw_input("state:")
        while 1:
            pincode=input("enter 6 digit pin:")
            if len(str(pincode))==6:
                self.pincode=pincode
                break
            else:
                print "wrong input"
                continue           
        
        while 1:
            tp=input("enter 1 for savings, 2 for current:")
            if tp==1 or tp==2:
                self.typ=tp
                break
            else:
                print "wrong input try again"
                continue
        
        if self.typ==1:
            while 1:
                chk_bal1=input("enter balance:")
                if chk_bal1>=0:
                    self.balance=chk_bal1
                    print "you have a savings account"
                    break
                else:
                    print "enter positive balance" 
            
        elif self.typ==2:
            while 1:
                chk_bal=input("Enter balance at least 5000")
                if chk_bal>=5000:
                    self.balance=chk_bal
                    print "you have a current account"
                    break
                else:
                    print "wrong input try again"
                    continue

        while 1:
            chk_pwd=raw_input("enter your password")
            if len(chk_pwd)>=8:
                self.pwd=chk_pwd
                break
            else:
                print "enter min 8 characters"
        statement='''insert into ADI.customer(c_id,accno,fname,lname,adrs1,
                    adrs2,city,state,pincode,typ,balance,pwd) values
                    (ADI.cus_id.nextval,ADI.cus_id.currval,:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)'''
        cur.execute(statement,(self.fname,self.lname,self.adrs1,self.adrs2,self.city,self.state,self.pincode,self.typ,self.balance,self.pwd))
        cur.execute('''select max(accno) from ADI.customer''')
        uracc=cur.fetchone()
        print "your account number is ",uracc[0]
        con.commit()
    def address_change(self,r):
        pincode=123456
        self.adrs1=raw_input("enter adress line 1")
        self.adrs2=raw_input("enter adress line 2")
        self.city=raw_input("enter city")
        self.state=raw_input("enter state")
        while 1:
            pincode=input("enter 6 digit pin:")
            if len(str(pincode))==6:
                self.pincode=pincode
                break
            else:
                print "wrong input"
                continue
        cur.execute('''update ADI.customer set adrs1=:param1,
                    adrs2=:param2,city=:param3,state=:param4,pincode=:param5 where c_id=:param''',{'param':r,'param1':self.adrs1,'param2':self.adrs2,'param3':self.city,'param4':self.state,'param5':self.pincode})
        con.commit()
        
###OBJECT CALLING
o1=Customer()
        
while 1:
    print "1 for sign up"
    print "2 for sign in"
    print "3 to admin sign in"
    print "4 to quit"

    c1=input("enter your choice:")
    if c1==1:
        print "if new customer then sign up"
        o1.inpt()
    elif c1==2:
        print "signing in"
        sgnd_id=validate()
        objacc=Account(sgnd_id)
        sv1=Savings(objacc)
        cr1=Current(objacc)
        r1=str(sgnd_id)
        if r1.isdigit():
            while(ch2=="Y" or ch2=="y"):
                print "1.Address change"
                print "2.money deposit"
                print "3.money withdrawl"
                print "4.print statement"
                print "5.transfer money"
                print "6.account closure"
                print "7.customer logout"
                c2=input("enter your choice")
                if c2==1:
                    o1.address_change(sgnd_id)
                elif c2==2:
                    dep=objacc.validate_acc_depo()
                    
                    if dep==1:
                        sv1.deposit(objacc)
                    elif dep==2:
                        cr1.deposit(objacc)
                elif c2==3:
                    a_typ=objacc.validate_acc_wdr(sgnd_id)
                    if a_typ==1:
                        sv1.wdraw(objacc)
                    elif a_typ==2:
                        cr1.wdraw(objacc)
                elif c2==4:
                    objacc.printstatement()
                elif c2==5:
                    objacc.transfer(objacc)
                elif c2==6:
                    objacc.close(sgnd_id)
                    break
                elif c2==7:
                    break
                else:
                    print "wrong input"
                    continue
                ch2=raw_input("Press Y to continue as a logged in customer")    
        elif sgnd_id=="fail":
            print "You are not allowed to sign in"
    elif c1==3:
        objadm=Admin()
        print "admin sign in"
        chk=objadm.admin_validate()
        if chk==1:
            while (ch3=="Y" or ch3=="y"):
                print "Press 1 to print closed account"
                print "Press 2 to admin logout"
                c3=input("Press either 1 or 2")
                if c3==1:
                    objadm.history()
                elif c3==2:
                    break
                else:
                    print "wrong input"
                    continue
                ch3=raw_input("enter Y to continue as admin")
        else:
            print "you did not login"
            
    elif c1==4:
        print "quit"
        break
    else:
        print "invalid choice"
        continue
    
con.close()
print "end of program"

    

