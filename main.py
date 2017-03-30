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

class Indicator():    
    
    def __init__(self, team, player):
        self.app = 'ratingfap0.1'
        iconpath = "/home/polka/github/ratingfap/owl.png"
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        
        self.team = team
        self.player = player
        
        self.update_ratings()
        self.indicator.set_label(self.label, self.app)
        
        #the thread:
        self.update = Thread(target=self.refresh_ratings)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()
        
    def make_soup(self, url):
        req = urllib.request.Request(url,headers=
            {'User-Agent': 'Mozilla/5.0'})
        html =  urllib.request.urlopen(req).read()
        soup = Bs(html,'lxml')
        return soup
        
    def get_rating(self, parameter):
        if parameter == 'player':
            url = 'http://rating.chgk.info/player/{0}/'.format(self.player.id)
        if parameter == 'team':
            url = 'http://rating.chgk.info/team/{0}/'.format(self.team.id)

        soup = self.make_soup(url) 
        table = soup.find('table', {'id':'ratings'})
        data = []
        rows = table.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) 
            
        if parameter == 'player':    
            player_rate = data[1][2]
            return player_rate
        if parameter == 'team':
            team_rate = data[1][3]
            return team_rate
                
    def create_menu(self):
        menu = Gtk.Menu()
        
        item_1 = Gtk.MenuItem('Menu item')
        item_1.connect('activate', self.menu_open_settings)
        menu.append(item_1)

        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.menu_stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def menu_open_settings(self, source):
        window = builder.get_object('settings_window')
        window.connect('delete-event', lambda w, e: w.hide() or True)
        
        members = [self.team, self.player]
        entries = []
        buttons = []
        labels = []
        for i, member in enumerate(members):
            entries.append(builder.get_object('entry_{}'.format(member.str)))
            entries[i].set_text(member.id)
            entries[i].connect('activate', self.find_name, member.str)
            
            buttons.append(builder.get_object(
                'button_open_{}_page'.format(member.str)))
            buttons[i].connect('clicked', self.goto_page, member.str)
            
            labels.append(builder.get_object('label_{}_name'.format(member.str)))
            labels[i].set_text()
                 
        window.show_all()
    
    def activated_entry(self):
        
    def find_name(self, entry, parameter):
        if parameter == 'team':
            self.team.id = entry.get_text()
            url = 'http://rating.chgk.info/{0}/{1}/'.format(
                parameter, self.team.id)
            self.update_ratings()
            
        elif parameter == 'player':
            self.player.id == entry.get_text()
            url = 'http://rating.chgk.info/{0}/{1}/'.format(
                parameter, self.player.id)
            self.update_ratings()
            
        soup = self.make_soup(url)
        title = soup.find('title')
        name = ' '.join(title.text.split()[:-8])
        label = builder.get_object('label_{}_name'.format(parameter))
        label.set_text(name)
        
    def goto_page(self, button, parameter):
        if parameter == 'team':
            url = 'http://rating.chgk.info/{0}/{1}/'.format(
                parameter, self.team.id)
        elif parameter == 'player':
            url = 'http://rating.chgk.info/{0}/{1}/'.format(
                parameter, self.player.id)
        webbrowser.open(url,new=2)               
            
    def refresh_ratings(self):
        while True:
            time.sleep(3600)
            self.update_ratings()
            
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                self.label, self.app,
                priority=GObject.PRIORITY_DEFAULT
                )
    
    def update_ratings(self):
        player_rating = self.get_rating('player')
        team_rating = self.get_rating('team')
        self.label = '{}|{}'.format(team_rating, player_rating)            
        
            
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