from django.test import TestCase
from django.test import Client
from django.contrib.auth import models, authenticate,login
from django.contrib.auth.models import User
import requests
import unittest
from Como33.views import comparationPlot, ytube, wikipedia, classificationPlot, calendarPlot, speedPlot, comparationPlot
from datetime import datetime 
import fastf1

class ViewTestCase(TestCase):
   
    def setUp(self):
        u = User.objects.create_user(username="testeo", password="testpassed")
        u.save()

    def test_loginSuccessful(self):
        username = "testeo"
        password = "testpassed"
        user = authenticate(username=username,password=password)
        self.assertIsNotNone(user)    
    
    def test_loginUnsuccessful(self):
        username = "test1"
        password = "testnopass"
        user = authenticate(username=username,password=password)
        self.assertIsNone(user)  

    def test_youtubeValid(self):
        video = ytube("Fernando Alonso")
        response = requests.get(video)
        self.assertEqual(response.status_code, 200)

    def test_youtubeNotValid(self):
        video = ytube("")
        self.assertIsNone(video)  

    def test_wikipediaValid(self):
        summary = wikipedia("Yuki Tsunoda")
        self.assertEqual(summary, "Yuki Tsunoda (Japanese: 角田 裕毅, Tsunoda Yūki, pronounced [tsɯnoda jɯ̟ᵝːkʲi]; born 11 May 2000) is a Japanese racing driver currently competing in Formula One for Scuderia AlphaTauri. Supported by Honda since 2016 through the Honda Formula Dream Project, he was the 2018 Japanese F4 champion and in 2019 also received backing from Red Bull. He finished third in the 2020 Formula 2 Championship and made his Formula One debut in 2021 for AlphaTauri.") 

    def test_wikipediaNotValid(self):
        summary = wikipedia("")
        self.assertIsNone(summary) 
 
    def test_Classification(self):
        plot = classificationPlot(2022)
        self.assertEqual(plot.shape,(22,4))
        self.assertEqual(plot.loc[0,"Name"], "Max Verstappen")
        self.assertEqual(plot.loc[0,"Team"], "Red Bull")
        self.assertEqual(plot.loc[8,"Name"], "Fernando Alonso")
        self.assertEqual(plot.loc[8,"Team"], "Alpine F1 Team")
        self.assertEqual(plot.loc[8,"Points"], 81.0)

    def test_Calendar(self):
        plot = calendarPlot()   
        fecha = datetime.strptime("2023-09-24", "%Y-%m-%d")
        self.assertEqual(plot.loc[14,"Country"], "Italy")
        self.assertEqual(plot.loc[14,"City"], "Monza")
        self.assertEqual(plot.loc[16,"Date"], fecha)

    def test_Speed(self):
        session = fastf1.get_session(int(2020), 'Hungaroring', 'R')
        session.load(weather=False, messages=False)
        plot = speedPlot("Carlos Sainz",session ,int(2020))
        self.assertIsNotNone(plot)
        session = fastf1.get_session(int(2020), 'Hungaroring', 'R')
        session.load(weather=False, messages=False)
        plot = speedPlot("Armandito",session ,int(2020))
        self.assertIsNone(plot)

    def test_Comparation(self):
        session = fastf1.get_session(int(2020), 'Hungaroring', 'R')
        session.load(weather=False, messages=False)
        plot = comparationPlot("Carlos Sainz","Max Verstappen",session ,int(2020))
        self.assertIsNotNone(plot)
        session = fastf1.get_session(int(2020), 'Hungaroring', 'R')
        session.load(weather=False, messages=False)
        plot = comparationPlot("Armandito","Juan",session ,int(2020))
        self.assertIsNone(plot)





