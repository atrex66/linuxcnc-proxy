# This script sets up symlinks so that 'linuxcnc' can be imported as a drop-in replacement for the real API.
# Run this script from the example directory.
import os
import sys

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '../linuxcnc_remote'))
DST = os.path.abspath(os.path.join(os.path.dirname(__file__), 'linuxcnc'))

for name in ['stat.py', 'command.py', 'error.py']:
    src_file = os.path.join(SRC, name)
    dst_file = os.path.join(DST, name)
    if not os.path.exists(dst_file):
        os.symlink(src_file, dst_file)

init_src = os.path.join(SRC, '__init__.py')
init_dst = os.path.join(DST, '__init__.py')
if not os.path.exists(init_dst):
    os.symlink(init_src, init_dst)

print('Symlinks created. You can now import linuxcnc as usual.')
