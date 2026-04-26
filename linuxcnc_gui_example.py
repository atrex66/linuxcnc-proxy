import linuxcnc_remote as linuxcnc
import time

s = linuxcnc.stat()
c = linuxcnc.command()
e = linuxcnc.error()

try:
    for _ in range(3):
        s.poll()
        print('State:', s.state)
        print('Position:', s.position)
        print('Homed:', s.homed)
        time.sleep(1)

    # Example: Home axis 0
    c.home(0)

    # Example: Send an MDI command (move to X10 Y20 Z30)
    c.mode(linuxcnc.MODE_MDI)
    c.wait_complete()
    c.mdi("G0 X10 Y20 Z30")
    c.wait_complete()

    # Poll for errors
    print('Error:', e.get())
finally:
    s.close()
    c.close()
    e.close()