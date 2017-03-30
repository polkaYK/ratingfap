# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 12:57:53 2017

@author: polka
"""

import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread

import urllib.request
import requests
from bs4 import BeautifulSoup as Bs

player_id = '60926'


class Indicator():
    def __init__(self):
        self.app = 'test123'
        iconpath = "/home/polka/github/ratingfap/owl.png"
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        string = self.get_rating()
        self.indicator.set_label(string, self.app)
        #the thread:
        self.update = Thread(target=self.show_seconds)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def get_rating(self):
        url = 'http://rating.chgk.info/player/60926/'
        req = urllib.request.Request(url,headers=
            {'User-Agent': 'Mozilla/5.0'})
        html =  urllib.request.urlopen(req).read()
        soup = Bs(html,'lxml')
        table = soup.find('table', {'id':'ratings'})
        num = int(list(list(table.children)[5].children)[5].text.split()[0])
        return str(num)
        
    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1
        item_1 = Gtk.MenuItem('Menu item')
        
        item_1.connect('activate', self.open_settings)
        menu.append(item_1)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def open_settings(self, source):
        window = builder.get_object('window1')
        window.connect('delete-event', lambda w, e: w.hide() or True)
        
        entry1 = builder.get_object('entry1')
        entry1.connect('activate', self.show_player, entry1.get_text())
        
        window.show_all()
        
    def show_player(self, entry, entry_data):
        label = builder.get_object('label3')
        if entry.get_text() == player_id:
           label.set_text('Kolodko')
        else:
           label.set_text(entry.get_text()) 
            

    def show_seconds(self):
        t = 2
        while True:
            time.sleep(1)
            mention = str(t)+" Monkeys"
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                mention, self.app,
                priority=GObject.PRIORITY_DEFAULT
                )
            t += 1

    def stop(self, source):
        Gtk.main_quit()

builder = Gtk.Builder()
builder.add_from_file("window.glade")


ind = Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)

Gtk.main()