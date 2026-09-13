import webview
import time
import threading

w = webview.create_window(
    'TestTransparent',
    html='<body style="background: rgba(10, 20, 40, 0.7); color: white; display: flex; align-items: center; justify-content: center; height: 100vh;"><h1>TRANSPARENCY TEST</h1></body>',
    transparent=True,
    frameless=True,
    on_top=True
)

def auto_close():
    time.sleep(2)
    w.destroy()

threading.Thread(target=auto_close, daemon=True).start()
webview.start()
print('Transparency test completed without error')
