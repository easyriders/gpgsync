import sys
from PyQt4 import QtCore, QtGui

from endpoint_selection import EndpointSelection
from edit_endpoint import EditEndpoint
from endpoint import Endpoint

class PGPSync(QtGui.QWidget):
    def __init__(self, app):
        super(PGPSync, self).__init__()
        self.app = app
        self.setWindowTitle('PGP Sync')

        # List of configured endpoints
        self.current_endpoint = None
        self.endpoints = []
        # todo: load these from file

        # Endpoint selection GUI
        self.endpoint_selection = EndpointSelection()
        endpoint_selection_wrapper = QtGui.QWidget()
        endpoint_selection_wrapper.setLayout(self.endpoint_selection)

        self.endpoint_selection.add_endpoint_signal.connect(self.add_endpoint)
        self.endpoint_selection.endpoint_list.itemClicked.connect(self.endpoint_clicked)

        # Edit endpoint GUI
        self.edit_endpoint = EditEndpoint()
        self.edit_endpoint_wrapper = QtGui.QWidget()
        self.edit_endpoint_wrapper.setLayout(self.edit_endpoint)
        self.edit_endpoint_wrapper.hide() # starts out hidden

        self.edit_endpoint.save_signal.connect(self.save_endpoint)
        self.edit_endpoint.delete_signal.connect(self.delete_endpoint)

        # Layout
        layout = QtGui.QHBoxLayout()
        layout.addWidget(endpoint_selection_wrapper)
        layout.addWidget(self.edit_endpoint_wrapper)
        self.setLayout(layout)
        self.show()

    def add_endpoint(self):
        e = Endpoint()
        print e.fingerprint
        self.endpoints.append(e)
        self.endpoint_selection.refresh(self.endpoints)

        # Click on the newest endpoint
        count = self.endpoint_selection.endpoint_list.count()
        item = self.endpoint_selection.endpoint_list.item(count-1)
        self.endpoint_selection.endpoint_list.setCurrentItem(item)
        self.endpoint_selection.endpoint_list.itemClicked.emit(item)

    def save_endpoint(self):
        # Get values for endpoint
        fingerprint = str(self.edit_endpoint.fingerprint_edit.text())
        url         = str(self.edit_endpoint.url_edit.text())
        keyserver   = str(self.edit_endpoint.keyserver_edit.text())
        use_proxy   = self.edit_endpoint.use_proxy.checkState() == QtCore.Qt.Checked
        proxy_host  = str(self.edit_endpoint.proxy_host_edit.text())
        proxy_port  = str(self.edit_endpoint.proxy_port_edit.text())

        self.endpoints[self.current_endpoint].update(fingerprint=fingerprint,
            url=url, keyserver=keyserver,
            use_proxy=use_proxy, proxy_host=proxy_host, proxy_port=proxy_port)

        # Unselect endpoint
        self.endpoint_selection.endpoint_list.setCurrentItem(None)
        self.edit_endpoint_wrapper.hide()
        self.current_endpoint = None

        # Refresh the display
        self.endpoint_selection.refresh(self.endpoints)

    def delete_endpoint(self):
        self.edit_endpoint_wrapper.hide()
        self.endpoints.remove(self.endpoints[self.current_endpoint])
        self.endpoint_selection.refresh(self.endpoints)
        self.current_endpoint = None

    def endpoint_clicked(self, item):
        try:
            i = self.endpoints.index(item.endpoint)
        except ValueError:
            print 'ERROR: Invalid endpoint'
            return

        # Clicking on an already-selected endpoint unselects it
        if i == self.current_endpoint:
            self.edit_endpoint_wrapper.hide()
            self.endpoint_selection.endpoint_list.setCurrentItem(None)
            self.current_endpoint = None

        # Select new endpoint
        else:
            self.current_endpoint = i
            self.edit_endpoint.set_endpoint(item.endpoint)
            self.edit_endpoint_wrapper.show()

def main():
    app = QtGui.QApplication(sys.argv)
    gui = PGPSync(app)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()