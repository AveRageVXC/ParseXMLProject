import tkinter as tk
from tkinter import *
import pymysql
# from config import host, user, password, db_name, port
import xml.etree.cElementTree as ET
import urllib.request
import logging
logging.basicConfig(filename="sample.log", level=logging.INFO, filemode="w")


try:
    host = ""
    user = ""
    password = ""
    db_name = ""
    port = 0

    goods = []
    goods_countries = []
    goods_colours = []
    goods_income = []
    goods_sales = []
    page = 1
    table = 1
    columns = 4

    try:
        global connection
        connection = pymysql.connect(
            host=host,
            user=user,
            port=port,
            passwd=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as ex:
        #print("Refused")
        #print(ex)
        pass

    def deepParser(root, add):
        global connection
        for child in root:

            # #print(child.tag, child.attrib, child.text)

            if child.tag.find("ObjectDeletion") != -1:
                deepParser(child, False)
            else:
                deepParser(child, add)

            if add:
                if child.tag.find("СтраныТоваров") != -1:
                    with connection.cursor() as cursor:
                        insert_query = "INSERT IGNORE INTO `goods_countries` (ref, code, description) VALUES ('{0}', '{1}', '{2}');".format(child[0].text, child[2].text, child[3].text)
                        # #print(insert_query)
                        cursor.execute(insert_query)
                        connection.commit()

                if child.tag.find("ЦветаТовара") != -1:
                    with connection.cursor() as cursor:
                        insert_query = "INSERT IGNORE INTO `goods_colours` (ref, code, description) VALUES ('{0}', '{1}', '{2}');".format(child[0].text, child[2].text, child[3].text)
                        # #print(insert_query)
                        cursor.execute(insert_query)
                        connection.commit()

                if child.tag.find("Товары") != -1:
                    with connection.cursor() as cursor:
                        insert_query = "INSERT IGNORE INTO `goods` (ref, code, description, colour, country) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(child[0].text, child[2].text, child[3].text, child[4].text, child[5].text)
                        # #print(insert_query)
                        cursor.execute(insert_query)
                        connection.commit()

                if child.tag.find("ОстаткиТоваров") != -1:
                    st = str(child[0][0].attrib.keys())
                    sub = st[st.find("{") + 1: st.find("}")]
                    # print(sub)
                    date_s = ""
                    with urllib.request.urlopen("{0}".format(sub)) as url:
                        s2 = str(url.read())
                        pos = s2.find("Date")
                    # print(s2)
                    with connection.cursor() as cursor:
                        s = str(child[0][0].attrib)
                        nul = "no date"
                        if s.find("ПродажаТоваров") != -1:
                            if pos != -1:
                                date_s = s2[pos + 6:pos + 25]
                                insert_query = "INSERT IGNORE INTO `goods_sales` (ref, date) VALUES ('{0}', '{1}');".format(child[0][0].text, date_s)
                            else:
                                logging.error("No such a date")
                                insert_query = "INSERT IGNORE INTO `goods_sales` (ref, date) VALUES ('{0}', '{1}');".format(child[0][0].text, nul)
                        if s.find("ПоступлениеТоваров") != -1:
                            if pos != -1:
                                date_s = s2[pos + 6:pos + 25]
                                insert_query = "INSERT IGNORE INTO `goods_income` (ref, date) VALUES ('{0}', '{1}');".format(child[0][0].text, date_s)
                            else:
                                logging.error("No such a date")
                                insert_query = "INSERT IGNORE INTO `goods_income` (ref, date) VALUES ('{0}', '{1}');".format(child[0][0].text, nul)
                        # #print(insert_query)
                        cursor.execute(insert_query)
                        connection.commit()

            if not add:
                s = str(child.attrib)

                if s.find("СтраныТоваров") != -1:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM `goods_countries` WHERE ref = '{0}';".format(child.text)
                        # #print("delete_query = ", delete_query)
                        cursor.execute(delete_query)
                        connection.commit()

                if s.find("ЦветаТовара") != -1:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM `goods_colours` WHERE ref = '{0}';".format(child.text)
                        # #print("delete_query = ", delete_query)
                        cursor.execute(delete_query)
                        connection.commit()

                if s.find("Товары") != -1:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM `goods` WHERE ref = '{0}';".format(child.text)
                        # #print("delete_query = ", delete_query)
                        cursor.execute(delete_query)
                        connection.commit()

                if s.find("ПродажаТоваров") != -1:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM `goods_sales` WHERE ref = '{0}';".format(child.text)
                        # #print("delete_query = ", delete_query)
                        cursor.execute(delete_query)
                        connection.commit()

                if s.find("ПоступлениеТоваров") != -1:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM `goods_income` WHERE ref = '{0}';".format(child.text)
                        # #print("delete_query = ", delete_query)
                        cursor.execute(delete_query)
                        connection.commit()


    def parseXML(xml_file):
        try:
            tree = ET.ElementTree(file=xml_file)
            root = tree.getroot()
            try:
                connection = pymysql.connect(
                    host=host,
                    user=user,
                    port=port,
                    passwd=password,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                try:

                    # create table

                    with connection.cursor() as cursor:
                        create_table_query = "CREATE TABLE IF not EXISTS `goods_countries`(ID int NOT NULL AUTO_INCREMENT," \
                                             " ref varchar(64) NOT NULL UNIQUE," \
                                             " code varchar(64)," \
                                             " description varchar(64)," \
                                             " PRIMARY KEY (ID));"
                        cursor.execute(create_table_query)
                        create_table_query = "CREATE TABLE IF not EXISTS `goods_sales`(ID int NOT NULL AUTO_INCREMENT," \
                                             " ref varchar(64) NOT NULL UNIQUE," \
                                             " date varchar(64)," \
                                             " PRIMARY KEY (ID));"
                        cursor.execute(create_table_query)
                        create_table_query = "CREATE TABLE IF not EXISTS `goods_income`(ID int NOT NULL AUTO_INCREMENT," \
                                             " ref varchar(64) NOT NULL UNIQUE," \
                                             " date varchar(64)," \
                                             " PRIMARY KEY (ID));"
                        cursor.execute(create_table_query)
                        create_table_query = "CREATE TABLE IF not EXISTS `goods_colours`(ID int NOT NULL AUTO_INCREMENT," \
                                             " ref varchar(64) NOT NULL UNIQUE," \
                                             " code varchar(64)," \
                                             " description varchar(64)," \
                                             " PRIMARY KEY (ID));"
                        cursor.execute(create_table_query)
                        create_table_query = "CREATE TABLE IF not EXISTS `goods`(ID int NOT NULL AUTO_INCREMENT," \
                                             " ref varchar(64) NOT NULL UNIQUE," \
                                             " code varchar(64)," \
                                             " description varchar(64)," \
                                             " colour varchar(64)," \
                                             " country varchar(64)," \
                                             " PRIMARY KEY (ID));"
                        cursor.execute(create_table_query)

                finally:
                    connection.close()
            except Exception as ex:
                pass
            deepParser(root, True)

        except Exception as ex:
            logging.error("{0}".format(ex))



    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            port=port,
            passwd=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as ex:
        #print("Refused")
        #print(ex)
        pass
    class config_class(tk.Toplevel):
        def __init__(self, parent):
            self.conf = tk.Toplevel(parent)
            self.conf.title("Connection")
            self.conf.geometry("360x131")
            self.conf.resizable(False, False)
            self.host_entry = tk.Entry(self.conf)
            self.port_entry = tk.Entry(self.conf)
            self.user_entry = tk.Entry(self.conf)
            self.password_entry = tk.Entry(self.conf, show="*")
            self.database_entry = tk.Entry(self.conf)
            self.save_but = tk.Button(self.conf, command = self.save_everything, text = "Сохранить", height = 1, width = 50)

            self.host_entry.grid(row = 0, column = 0, sticky = 'nsew')
            self.port_entry.grid(row = 1, column = 0, sticky = 'nsew')
            self.user_entry.grid(row = 2, column = 0, sticky = 'nsew')
            self.password_entry.grid(row = 3, column = 0, sticky = 'nsew')
            self.database_entry.grid(row = 4, column = 0, sticky = 'nsew')
            self.save_but.grid(row = 5, column = 0, sticky = 'nsew', columnspan = 2)

            self.host_label= tk.Label(self.conf, text = "Host")
            self.port_label = tk.Label(self.conf, text = "Port")
            self.user_label = tk.Label(self.conf, text = "User")
            self.database_label = tk.Label(self.conf, text = "Database")
            self.password_label = tk.Label(self.conf, text = "Password")

            self.host_label.grid(row = 0, column = 1, sticky = 'nsew')
            self.port_label.grid(row = 1, column = 1, sticky = 'nsew')
            self.user_label.grid(row = 2, column = 1, sticky = 'nsew')
            self.password_label.grid(row = 3, column = 1, sticky = 'nsew')
            self.database_label.grid(row = 4, column = 1, sticky = 'nsew')
        def save_everything(self):
            global user, password, db_name, port, host, connection
            host = self.host_entry.get()
            try:
                port = int(self.port_entry.get())
            except Exception as ex:
                logging.error("{0}".format(ex))
            user = self.user_entry.get()
            password = self.password_entry.get()
            db_name = self.database_entry.get()
            try:
                global  connection
                connection = pymysql.connect(
                    host=host,
                    user=user,
                    port=port,
                    passwd=password,
                    database=db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                self.conf.destroy()
                # update_command()
                # reload_page()
            except Exception as ex:
                logging.error("{0}".format(ex))

    def comm_goods():
        global page
        page = 1
        table_goods()

    def comm_goods_countries():
        global page
        page = 1
        table_goods_countries()

    def comm_goods_colours():
        global page
        page = 1
        table_goods_colours()

    def comm_goods_income():
        global page
        page = 1
        table_goods_income()

    def comm_goods_sales():
        global page
        page = 1
        table_goods_sales()

    def table_goods():
        global table
        table = 1
        global labels, connection, rows, columns, frame_main, page, goods, rows_show, frame_right
        with connection.cursor() as cursor:
            for i in range(0, 11):
                #print(i)
                for k in range(0, columns):
                    labels[i][k].destroy()
            columns = 4
            labels = [[Label(frame_main, width=20, height=2) for j in range(4)] for i in range(11)]
            for i in range(11):
                for k in range(4):
                    labels[i][k].grid(row = i, column = k, sticky = 'nsew')
            labels[0][0] = Label(frame_main, width=20, height=2, text = "Товар")
            labels[0][1] = Label(frame_main, width=20, height=2, text = "Страна")
            labels[0][2] = Label(frame_main, width=20, height=2, text = "Цвет")
            labels[0][3] = Label(frame_main, width=20, height=2, text = "Код")
            labels[0][0].grid(row=0, column=0, sticky='news')
            labels[0][1].grid(row=0, column=1, sticky='news')
            labels[0][2].grid(row=0, column=2, sticky='news')
            labels[0][3].grid(row=0, column=3, sticky='news')

            for i in range(1, min(rows_show, len(goods) + 1 - (page - 1) * 10)):
                labels[i][0] = Label(frame_main, width=20, height=2, text = goods[i - 1 + (page - 1) * 10]["description"])
                labels[i][0].grid(row=i, column=0, sticky='news')
                select_query = "SELECT description FROM `goods_countries` WHERE ref='{0}'".format(goods[i - 1 + (page - 1) * 10]["country"])
                cursor.execute(select_query)
                got_country = cursor.fetchall()
                if len(got_country) == 0:
                    logging.error("{0}: No such country".format(goods[i - 1 + (page - 1) * 10]["country"]))
                    labels[i][1] = Label(frame_main, width=20, height=2, text = "NULL")
                else:
                    labels[i][1] = Label(frame_main, width=20, height=2, text = got_country[0]["description"])
                labels[i][1].grid(row=i, column=1, sticky='news')

                select_query = "SELECT description FROM `goods_colours` WHERE ref='{0}'".format(goods[i - 1 + (page - 1) * 10]["colour"])
                cursor.execute(select_query)
                got_colour = cursor.fetchall()
                if len(got_colour) == 0:
                    logging.error("{0}: No such colour".format(goods[i - 1 + (page - 1) * 10]["colour"]))
                    labels[i][2] = Label(frame_main, width=20, height=2, text="NULL")
                else:
                    labels[i][2] = Label(frame_main, width=20, height=2, text=got_colour[0]["description"])
                labels[i][2].grid(row=i, column=2, sticky='news')
                labels[i][3] = Label(frame_main, width=20, height=2, text = goods[i - 1 + (page - 1) * 10]["code"])
                labels[i][3].grid(row=i, column=3, sticky='news')

            frame_main.update_idletasks()
            reload_buttons()

    def table_goods_countries():
        global table
        table = 2
        global labels, connection, rows, columns, frame_main, page, goods_countries, rows_show
        with connection.cursor() as cursor:
            for i in range(0, 11):
                for k in range(0, columns):
                    labels[i][k].destroy()
            # #print("countries", goods_countries)
            columns = 2
            labels = [[Label(frame_main, width=20, height=2) for j in range(4)] for i in range(11)]
            for i in range(11):
                for k in range(4):
                    labels[i][k].grid(row=i, column=k, sticky = 'nsew')
            labels[0][0] = Label(frame_main, width=20, height=2, text="Страна")
            labels[0][1] = Label(frame_main, width=20, height=2, text="Код")
            labels[0][0].grid(row=0, column=0, sticky='news')
            labels[0][1].grid(row=0, column=1, sticky='news')
            for i in range(1, min(rows_show, len(goods_countries) + 1 - (page - 1) * 10)):
                labels[i][0] = Label(frame_main, width=20, height=2, text=goods_countries[i - 1 + (page - 1) * 10]["description"])
                labels[i][0].grid(row=i, column=0, sticky='news')
                labels[i][1] = Label(frame_main, width=20, height=2, text=goods_countries[i - 1 + (page - 1) * 10]["code"])
                labels[i][1].grid(row=i, column=1, sticky='news')

            frame_main.update_idletasks()
            reload_buttons()

    def table_goods_colours():
        global table
        table = 3
        global labels, connection, rows, columns, frame_main, page, goods_colours, rows_show
        with connection.cursor() as cursor:
            for i in range(0, 11):
                for k in range(0, columns):
                    labels[i][k].destroy()
            columns = 2
            labels = [[Label(frame_main, width=20, height=2) for j in range(4)] for i in range(11)]
            for i in range(11):
                for k in range(4):
                    labels[i][k].grid(row=i, column=k, sticky = 'nsew')
            labels[0][0] = Label(frame_main, width=20, height=2, text="Цвет")
            labels[0][1] = Label(frame_main, width=20, height=2, text="Код")
            labels[0][0].grid(row=0, column=0, sticky='news')
            labels[0][1].grid(row=0, column=1, sticky='news')
            # #print("colours", goods_colours)
            for i in range(1, min(rows_show, len(goods_colours) + 1 - (page - 1) * 10)):
                labels[i][0] = Label(frame_main, width=20, height=2,
                                     text=goods_colours[i - 1 + (page - 1) * 10]["description"])
                labels[i][0].grid(row=i, column=0, sticky='news')
                labels[i][1] = Label(frame_main, width=20, height=2, text=goods_colours[i - 1 + (page - 1) * 10]["code"])
                labels[i][1].grid(row=i, column=1, sticky='news')

            frame_main.update_idletasks()
            reload_buttons()

    def table_goods_income():
        global table
        table = 4
        global labels, connection, rows, columns, frame_main, page, goods_income, rows_show
        with connection.cursor() as cursor:
            for i in range(0, 11):
                for k in range(0, columns):
                    labels[i][k].destroy()
            columns = 2
            labels = [[Label(frame_main, width=20, height=2) for j in range(4)] for i in range(11)]
            for i in range(11):
                for k in range(4):
                    labels[i][k].grid(row=i, column=k, sticky = 'nsew')
            labels[0][0] = Label(frame_main, width=20, height=2, text="Дата")
            labels[0][1] = Label(frame_main, width=20, height=2, text="Номер")
            labels[0][0].grid(row=0, column=0, sticky='news')
            labels[0][1].grid(row=0, column=1, sticky='news')
            # #print("goods_income", goods_income)
            for i in range(1, min(rows_show, len(goods_income) + 1 - (page - 1) * 10)):
                labels[i][0] = Label(frame_main, width=20, height=2,
                                     text=goods_income[i - 1 + (page - 1) * 10]["date"])
                labels[i][0].grid(row=i, column=0, sticky='news')

                select_query = "SELECT code FROM `goods` WHERE ref='{0}'".format(
                    goods_income[i - 1 + (page - 1) * 10]["ref"])
                cursor.execute(select_query)
                got_code = cursor.fetchall()
                ##print(got_code)
                if len(got_code) == 0:
                    logging.error("{0}: No such product".format(goods_income[i - 1 + (page - 1) * 10]["ref"]))
                    labels[i][1] = Label(frame_main, width=20, height=2, text="NULL")
                else:
                    labels[i][1] = Label(frame_main, width=20, height=2, text=got_code[0]["code"])
                labels[i][1].grid(row=i, column=1, sticky='news')

            frame_main.update_idletasks()
            reload_buttons()

    def table_goods_sales():
        global table
        table = 5
        global labels, connection, rows, columns, frame_main, page, goods_sales, rows_show
        with connection.cursor() as cursor:
            for i in range(0, 11):
                for k in range(0, columns):
                    labels[i][k].destroy()
            columns = 2
            labels = [[Label(frame_main, width=20, height=2) for j in range(4)] for i in range(11)]
            for i in range(11):
                for k in range(4):
                    labels[i][k].grid(row=i, column=k, sticky='nsew')
            labels[0][0] = Label(frame_main, width=20, height=2, text="Дата")
            labels[0][1] = Label(frame_main, width=20, height=2, text="Номер")
            labels[0][0].grid(row=0, column=0, sticky='news')
            labels[0][1].grid(row=0, column=1, sticky='news')
            # #print("goods_income", goods_income)
            for i in range(1, min(rows_show, len(goods_sales) + 1 - (page - 1) * 10)):
                labels[i][0] = Label(frame_main, width=20, height=2,
                                     text=goods_sales[i - 1 + (page - 1) * 10]["date"])
                labels[i][0].grid(row=i, column=0, sticky='news')

                select_query = "SELECT code FROM `goods` WHERE ref='{0}'".format(
                    goods_sales[i - 1 + (page - 1) * 10]["ref"])
                cursor.execute(select_query)
                got_code = cursor.fetchall()
                #print(select_query)
                #print(got_code)
                if len(got_code) == 0:
                    logging.error("{0}: No such product".format(goods_sales[i - 1 + (page - 1) * 10]["ref"]))
                    labels[i][1] = Label(frame_main, width=20, height=2, text="NULL")
                else:
                    labels[i][1] = Label(frame_main, width=20, height=2, text=got_code[0]["code"])
                labels[i][1].grid(row=i, column=1, sticky='news')

            frame_main.update_idletasks()
            reload_buttons()

    def create_page_control():
        global frame_left_bottom, frame_right

        but_first = Button(frame_right, text = 1, width = 4, height = 2, command = first)
        but_left = Button(frame_right, text = "🠔", width = 4, height = 2, command = left)
        but_now = Button(frame_right, text = page, width = 4, height = 2, command = now)
        but_right = Button(frame_right, text = "🠖", width = 4, height = 2, command = right)
        but_last = Button(frame_right, text = "1", width = 4, height = 2, command = last)

        but_first.pack(side = LEFT)
        but_left.pack(side = LEFT)
        but_now.pack(side = LEFT)
        but_right.pack(side = LEFT)
        but_last.pack(side = LEFT)
        last_but_conf(but_last)
        frame_right.update_idletasks()
        return but_first, but_left, but_now, but_right, but_last

    def last_but_conf(but_last):
        global table
        global goods, goods_countries, goods_colours, goods_income, goods_sales
        if table == 1:
            txt = (len(goods) + 9) // 10
        if table == 2:
            txt = (len(goods_countries) + 9) // 10
        if table == 3:
            txt = (len(goods_colours) + 9) // 10
        if table == 4:
            txt = (len(goods_income) + 9) // 10
        if table == 5:
            txt = (len(goods_sales) + 9) // 10
        but_last.config(text = txt)

    def reload_buttons():
        global but_now, but_left, but_first, but_right, but_last, frame_right
        global goods, goods_countries, goods_colours, goods_income, goods_sales
        #print("reloading buttons")
        but_first.destroy()
        but_left.destroy()
        but_now.destroy()
        but_right.destroy()
        but_last.destroy()
        but_first, but_left, but_now, but_right, but_last = create_page_control()
        if but_last.cget('text') == 0:
            but_first.destroy()
            but_left.destroy()
            but_now.config(text = page)
            but_right.destroy()
            but_last.destroy()
        elif but_last.cget('text') == 1:
            but_first.destroy()
            but_left.destroy()
            but_right.destroy()
            but_last.destroy()
            frame_right.update_idletasks()
        elif page == 1:
            but_first.destroy()
            but_left.destroy()
            but_now.config(text = page)
            frame_right.update_idletasks()
        elif table == 1 and page * 10 >= len(goods):
            but_right.destroy()
            but_last.destroy()
            but_now.config(text = page)
            frame_right.update_idletasks()
        elif table == 2 and page * 10 >= len(goods_countries):
            but_right.destroy()
            but_last.destroy()
            but_now.config(text=page)
            frame_right.update_idletasks()
        elif table == 3 and page * 10 >= len(goods_colours):
            but_right.destroy()
            but_last.destroy()
            but_now.config(text=page)
            frame_right.update_idletasks()
        elif table == 4 and page * 10 >= len(goods_income):
            but_right.destroy()
            but_last.destroy()
            but_now.config(text=page)
            frame_right.update_idletasks()
        elif table == 5 and page * 10 >= len(goods_sales):
            but_right.destroy()
            but_last.destroy()
            but_now.config(text=page)
            frame_right.update_idletasks()
        else:
            but_first.destroy()
            but_left.destroy()
            but_now.destroy()
            but_right.destroy()
            but_last.destroy()
            but_first, but_left, but_now, but_right, but_last = create_page_control()

    def reload_page():
        global but_now, but_left, but_first, but_right, but_last, frame_right, table
        #print("reloading page")
        if table == 1:
            table_goods()
        if table == 2:
            table_goods_countries()
        if table == 3:
            table_goods_colours()
        if table == 4:
            table_goods_income()
        if table == 5:
            table_goods_sales()

        reload_buttons()

    def first():
        global page
        page = 1
        reload_page()

    def left():
        global page
        page -= 1
        reload_page()

    def now():
        pass

    def right():
        global page
        page += 1
        reload_page()

    def last():
        global page, but_last
        page = but_last.cget('text')
        reload_page()

    def update_command():
        parseXML("DataFrom1C.xml")
        global goods, goods_countries, goods_colours, goods_income, goods_sales, connection
        with connection.cursor() as cursor:
            # goods
            try:
                select_all_rows = "SELECT * FROM `goods`"
                cursor.execute(select_all_rows)
                goods = cursor.fetchall()
            except Exception as ex:
                logging.error("{0}".format(ex))
                pass
            # goods_countries
            try:
                select_all_rows = "SELECT * FROM `goods_countries`"
                cursor.execute(select_all_rows)
                goods_countries = cursor.fetchall()
            except Exception as ex:
                logging.error("{0}".format(ex))
                #print("Refused")
                #print(ex)
                pass
            # goods_colours
            try:
                select_all_rows = "SELECT * FROM `goods_colours`"
                cursor.execute(select_all_rows)
                goods_colours = cursor.fetchall()
            except Exception as ex:
                logging.error("{0}".format(ex))
                #print("Refused")
                #print(ex)

            # goods_income
            try:
                select_all_rows = "SELECT * FROM `goods_income`"
                cursor.execute(select_all_rows)
                goods_income = cursor.fetchall()
            except Exception as ex:
                logging.error("{0}".format(ex))
                #print("Refused")
                #print(ex)

            # goods_sales
            try:
                select_all_rows = "SELECT * FROM `goods_sales`"
                cursor.execute(select_all_rows)
                goods_sales = cursor.fetchall()
            except Exception as ex:
                logging.error("{0}".format(ex))
                #print("Refused")
                #print(ex)
        reload_page()

    def update_config():
        global root
        config_root = config_class(root)

    def endlog():
        logging.info("End of working")
        root.destroy()

    root = tk.Tk()
    root.title("Xml обмен данными")
    root.protocol("WM_DELETE_WINDOW", endlog)
    logging.info("Start working")
    root.columnconfigure((0, 1), weight = 1)
    root.rowconfigure(0, weight = 1)
    root.rowconfigure(1, weight = 0)

    frame_main = tk.Frame(root, bg="gray")
    frame_main.grid(column = 1, row = 0, sticky='news')

    frame_right = Frame(root, bg="gray")
    frame_right.grid(column = 1, row = 1, sticky = 'news')
    #print(table)


    frame_left = Frame(root, bg = "grey")
    frame_left.grid(column = 0, row = 0, sticky='news')

    frame_left_bottom = Frame(root, bg = "blue")
    frame_left_bottom.grid(column = 0, row = 1, sticky='news')

    but_first, but_left, but_now, but_right, but_last = create_page_control()

    but_goods = Button(frame_left, text="Товары", command=comm_goods)
    but_goods_countries = Button(frame_left, text="Страны товаров", command=comm_goods_countries)
    but_goods_colours = Button(frame_left, text="Цвета товаров", command=comm_goods_colours)
    but_goods_income = Button(frame_left, text="Поступление товаров", command=comm_goods_income)
    but_goods_sales = Button(frame_left, text="Продажа товаров", command=comm_goods_sales)

    but_goods.pack(side=TOP, fill=BOTH)
    but_goods_countries.pack(side=TOP, fill=BOTH)
    but_goods_colours.pack(side=TOP, fill=BOTH)
    but_goods_income.pack(side=TOP, fill=BOTH)
    but_goods_sales.pack(side=TOP, fill=BOTH)

    but_update = Button(frame_left_bottom, text="Обновить", command=update_command)
    but_config = Button(frame_left_bottom, text="Соединение", command=update_config)
    but_update.pack(side=LEFT, fill=BOTH, expand=True)
    but_config.pack(side=LEFT, fill=BOTH, expand=True)

    rows = 11
    columns = 4
    rows_show = 11
    labels = [[Label() for j in range(columns)] for i in range(rows)]

    for i in range(columns):
        frame_main.grid_columnconfigure(i, weight = 1)
    for i in range(rows_show):
        frame_main.grid_rowconfigure(i, weight = 1)

    for i in range(0, rows):
        for j in range(0, columns):
            labels[i][j] = Label(frame_main, width = 20, height = 2)
            labels[i][j].grid(row=i, column=j, sticky='news')

    frame_main.update_idletasks()

    first5columns_width = sum([labels[0][j].winfo_width() for j in range(0, columns)])
    first5rows_height = sum([labels[i][0].winfo_height() for i in range(0, min(rows_show, rows))])

    frame_main.config(width=first5columns_width,
                        height=first5rows_height)
    #print(table)
    if user != "":
        update_command()
        comm_goods()

    root.mainloop()
except Exception as ex:
    #print(ex)
    logging.error("{0}".format(ex))

