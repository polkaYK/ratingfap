# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 05:28:52 2017

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
import webbrowser

class Member():
    def __init__(self, type_string, ID):
        self.str = type_string
        self.id = ID            
        self.update_rating()
        
    @property
    def url(self):
        return 'http://rating.chgk.info/{0}/{1}/'.format(self.str, self.id)
            
    def update_rating(self):
        req = urllib.request.Request(self.url,
                                     headers={'User-Agent': 'Mozilla/5.0'})
        html =  urllib.request.urlopen(req).read()
        soup = Bs(html,'lxml')

        table = soup.find('table', {'id':'ratings'})
        data = []
        rows = table.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) 
            
        if self.str == 'player':    
            self.rating = data[1][2]
            
        elif self.str == 'team':
            self.rating = data[1][3]
        
        title = soup.find('title')
        self.name = ' '.join(title.text.split()[:-8])
        
        del html, soup, table, data, title

class Indicator():    
    
    def __init__(self, team, player):
        self.app = 'ratingfap0.1'
        iconpath = "/home/polka/github/ratingfap/big_owl.png"
        self.indicator = AppIndicator3.Indicator.new(self.app, 
                                                     iconpath,
                                                     AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        
        self.team = team
        self.player = player
        self.update_label() 
        self.indicator.set_label(self.label, self.app)
        
        #the thread:
        self.update = Thread(target=self.refresh_ratings)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()
    
    def update_label(self):
        self.team.update_rating()
        self.player.update_rating()
        self.label = '{}|{}'.format(self.team.rating, self.player.rating)
            
    def create_menu(self):
        menu = Gtk.Menu()
        
        item_1 = Gtk.MenuItem('Настройки')
        item_1.connect('activate', self.menu_open_settings)
        menu.append(item_1)

        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        
        item_quit = Gtk.MenuItem('Выход')
        item_quit.connect('activate', self.menu_stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def menu_open_settings(self, source):
        window = builder.get_object('settings_window')
        window.connect('delete-event', lambda w, e: w.hide() or True)
        
        label_team = builder.get_object('label_team_name')
        label_team.set_text(self.team.name)  
        #label_team.connec

        entry_team = builder.get_object('entry_team')
        entry_team.set_text(self.team.id)
        entry_team.connect('activate', self.update_name, self.team, label_team)

        
        button_team = builder.get_object('button_open_team_page')
        button_team.connect('clicked', self.goto_page, self.team)
#-----------------------------------------------------------              
        label_player = builder.get_object('label_player_name')
        label_player.set_text(self.player.name)        
        
        entry_player = builder.get_object('entry_player')
        entry_player.set_text(self.player.id)
        entry_player.connect('activate', self.update_name, self.player, label_player)
        
        button_player = builder.get_object('button_open_player_page')
        button_player.connect('clicked', self.goto_page, self.player)
        
        window.show_all()
    
        
    def update_name(self, entry, member, label):
        member.id = entry.get_text()
        member.update_rating()
        label.set_text(member.name)
        self.update_label()
        GObject.idle_add(self.indicator.set_label,
                         self.label, 
                         self.app,
                         priority=GObject.PRIORITY_DEFAULT)
        
    def goto_page(self, button, member):
        webbrowser.open(member.url,new=2)               
            
    def refresh_ratings(self):
        while True:
            time.sleep(3600)
            self.update_label()
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(self.indicator.set_label,
                             self.label, 
                             self.app,
                             priority=GObject.PRIORITY_DEFAULT)
             
    def menu_stop(self, source):
        Gtk.main_quit()

builder = Gtk.Builder()
builder.add_from_file("window.glade")

team = Member('team','48913')    
player = Member('player','60926')

ind = Indicator(team, player)
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)


Gtk.main()