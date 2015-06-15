import pythoncom, pyHook
import win32gui, win32ui, win32con, win32api
from sift_test2 import find_buildings

def OnKeyboardEvent(event):
    
    if(event.Key =='Escape'):
        exit()
    if(event.Key =='Snapshot'):
        print 'WindowName:',event.WindowName
        print 'Ascii:', event.Ascii, chr(event.Ascii)
        print 'Key:', event.Key
        #print 'Obs#:', self.n

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
    # return True to pass the event to other handlers

        img3=find_buildings("C:\\sc2centaur\\observations\\observation.bmp")
        print("image collected")

    return True


"""

"""
# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()
