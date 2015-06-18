import os
import pyHook
import pythoncom
import threading
import win32gui, win32ui, win32con, win32api
 
"""
Adapted from:
https://gist.github.com/jdiscar/9144923

"""

# Requires pyHook: http://sourceforge.net/apps/mediawiki/pyhook/
# Requires pyWin32: http://sourceforge.net/projects/pywin32/
 
# Kills the process if escape is pressed
class EscapeToKill(threading.Thread):
    
    def run(self):
        
        def onKeyboardEvent(event):
            asciiEscapeKey = 27
            if event.Ascii == asciiEscapeKey:
                os._exit(0)
            return True
 
        hm = pyHook.HookManager()
        hm.KeyDown = onKeyboardEvent
        hm.HookKeyboard()
        pythoncom.PumpMessages()
 
# Gets global input
class GlobalInput():
 
    def getMousePos(self):
        self.Active = True
        self.position = None
        
        def onclick(event):
            if( self.Active ):
                self.position = event.Position
            return True        
 
        hm = pyHook.HookManager()
        hm.SubscribeMouseAllButtonsDown(onclick)
        hm.HookMouse()
        hm.HookKeyboard()   # hm.UnhookMouse throws an error otherwise
        while self.position == None:
            pythoncom.PumpWaitingMessages()
        hm.UnhookMouse()
        hm.UnhookKeyboard()
        self.Active = False
        return self.position
        
    def getKey(self):
        self.Active = True
        self.key = None        
        self.bmpfile = None
        def onKeyboardEvent(event):
            if( self.Active ):
                self.key = event.Key
            if(event.Key =='Snapshot'):
                hwin = win32gui.GetForegroundWindow()
                width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
                height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
                left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
                top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
                hwindc = win32gui.GetWindowDC(hwin)
                srcdc = win32ui.CreateDCFromHandle(hwindc)
                memdc = srcdc.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(srcdc, width, height)
                memdc.SelectObject(bmp)
                memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
                bmp.SaveBitmapFile(memdc, 'observations\observation'+'.bmp')
                self.bmpfile = memdc
                print("image collected")     
            return True

        hm = pyHook.HookManager()
        hm.KeyDown = onKeyboardEvent
        hm.HookMouse()  # hm.UnhookMouse throws an error otherwise
        hm.HookKeyboard()
        while self.key == None:
            pythoncom.PumpWaitingMessages()
        hm.UnhookMouse()
        hm.UnhookKeyboard()
        return self.key      
 
if __name__ == "__main__":   
    t = GlobalInput()
    
    print "Click Mouse, print position: "
    print t.getMousePos()
    
    print "Press Key, print key's ascii code: "
    print t.getKey()
    
    print "Click Mouse, print position: "
    print t.getMousePos()
    
    print "Press Escape Key to Kill Process: "
    t2 = EscapeToKill()
    t2.start()