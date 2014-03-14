import subprocess

class WindowHelper(object):


    def get_active_window(self):
        cmd = "xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2"
        window_id = subprocess.check_output(cmd, shell=True).strip()

        return window_id

    def resize_window(self, id, x, y, w, h):
        cmd = 'wmctrl -i -r {id} -e 0,{x},{y},{w},{h}'.format(id=id, x=x, y=y, w=w, h=h)
        subprocess.call(cmd, shell=True)
