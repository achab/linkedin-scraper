#!/usr/bin/python
# -*- coding: utf-8 -*-


from fetch_contacts import fetch_contacts
import wx, sys, os


def reexec_with_pythonw():
    if sys.platform == 'darwin' and not sys.executable.endswith('MacOS/Python'):
        print >> sys.stderr, 're-executing using pythonw'
        os.execvp('pythonw',['pythonw',__file__] + sys.argv[1:])


class MainWindow(wx.Dialog):

    def __init__(self, *args, **kw):
        super(MainWindow, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):

        pnl = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        st1 = wx.StaticText(pnl, label='Username')
        st2 = wx.StaticText(pnl, label='Password')

        self.tc1 = wx.TextCtrl(pnl, size=(180, -1))
        self.tc2 = wx.TextCtrl(pnl, size=(180, -1))

        button_send = wx.Button(pnl, label='Launch')

        hbox1.Add(st1, flag=wx.LEFT, border=10)
        hbox1.Add(self.tc1, flag=wx.LEFT, border=35)
        hbox2.Add(st2, flag=wx.LEFT, border=10)
        hbox2.Add(self.tc2, flag=wx.LEFT, border=37)
        vbox.Add(hbox1, flag=wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.TOP, border=10)
        vbox.Add(button_send, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        self.Bind(wx.EVT_BUTTON, self.OnSend, button_send)
        pnl.SetSizer(vbox)

        self.SetSize((350, 150))
        self.SetTitle('LinkedIn scraper')
        self.Centre()
        self.ShowModal()
        self.Show(True)
        self.Destroy()

    def OnSend(self, e):
        username = self.tc1.GetValue()
        password = self.tc2.GetValue()
        fetch_contacts(username=username, password=password)
        self.Close()


class FinalMessage(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(FinalMessage, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        wx.FutureCall(10, self.ShowMessage)

        self.SetSize((300, 200))
        self.SetTitle('Message box')
        self.Centre()
        self.Show(True)

    def ShowMessage(self):
        wx.MessageBox('Les données de tous les contacts ont été récupérées !', 'Info', wx.OK | wx.ICON_INFORMATION)


def main():

    reexec_with_pythonw()
    ex = wx.App()
    MainWindow(None)
    #FinalMessage(None)
    ex.MainLoop()


if __name__ == '__main__':
    main()
