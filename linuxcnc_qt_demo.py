import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QTimer
import linuxcnc_remote as linuxcnc

class LinuxCNCQtDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxCNC Qt Demo")
        self.s = linuxcnc.stat()
        self.c = linuxcnc.command()
        self.e = linuxcnc.error()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)


    def init_ui(self):
        layout = QVBoxLayout()

        # Status indicators
        self.estop_label = QLabel("ESTOP: ---")
        self.machine_on_label = QLabel("Machine ON: ---")
        layout.addWidget(self.estop_label)
        layout.addWidget(self.machine_on_label)

        # Error channel display
        self.error_label = QLabel("Error: (none)")
        layout.addWidget(self.error_label)

        # Axis display
        self.axis_labels = []
        for i in range(3):
            lbl = QLabel(f"Axis {i}: ---")
            self.axis_labels.append(lbl)
            layout.addWidget(lbl)

        # Homing buttons
        home_layout = QHBoxLayout()
        for i in range(3):
            btn = QPushButton(f"Home Axis {i}")
            btn.clicked.connect(lambda checked, axis=i: self.home_axis(axis))
            home_layout.addWidget(btn)
        layout.addLayout(home_layout)

        # ESTOP and Machine ON buttons
        estop_layout = QHBoxLayout()
        estop_reset_btn = QPushButton("Reset ESTOP")
        estop_reset_btn.clicked.connect(self.reset_estop)
        estop_layout.addWidget(estop_reset_btn)

        machine_on_btn = QPushButton("Machine ON")
        machine_on_btn.clicked.connect(self.machine_on)
        estop_layout.addWidget(machine_on_btn)

        layout.addLayout(estop_layout)

        # MDI command
        self.mdi_input = QLineEdit()
        self.mdi_input.setPlaceholderText("Enter MDI command (e.g. G0 X10 Y10)")
        self.mdi_btn = QPushButton("Send MDI")
        self.mdi_btn.clicked.connect(self.send_mdi)
        mdi_layout = QHBoxLayout()
        mdi_layout.addWidget(self.mdi_input)
        mdi_layout.addWidget(self.mdi_btn)
        layout.addLayout(mdi_layout)

        self.setLayout(layout)
    def reset_estop(self):
        self.c.state(linuxcnc.STATE_ESTOP_RESET)

    def machine_on(self):
        self.c.state(linuxcnc.STATE_ON)

    def update_status(self):
        self.s.poll()
        # Update ESTOP and machine state
        estop_state = getattr(self.s, 'estop', None)
        task_state = getattr(self.s, 'task_state', None)
        self.estop_label.setText(f"ESTOP: {'ON' if estop_state else 'OFF' if estop_state is not None else '---'}")
        self.machine_on_label.setText(f"Machine ON: {'ON' if task_state == 3 else 'OFF' if task_state is not None else '---'}")

        # Update error channel
        error = self.e.get() if hasattr(self, 'e') else None
        self.error_label.setText(f"Error: {error if error else '(none)'}")

        # Update axes
        for i, lbl in enumerate(self.axis_labels):
            pos = self.s.position
            if pos and len(pos) > i:
                lbl.setText(f"Axis {i}: {pos[i]:.3f}")
            else:
                lbl.setText(f"Axis {i}: ---")

    def home_axis(self, axis):
        self.c.mode(linuxcnc.MODE_MANUAL)
        self.c.home(axis)

    def send_mdi(self):
        cmd = self.mdi_input.text().strip()
        if cmd:
            self.c.mode(linuxcnc.MODE_MDI)
            self.c.wait_complete()
            self.c.mdi(cmd)
            self.c.wait_complete()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LinuxCNCQtDemo()
    win.show()
    sys.exit(app.exec_())
