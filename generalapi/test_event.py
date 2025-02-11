from PyQt5.QtCore import QThread, QEvent, QCoreApplication, QObject, pyqtSignal
import sys


# Custom event class to send messages
class StringEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, message):
        QEvent.__init__(self, StringEvent.EVENT_TYPE)  # Explicit QEvent constructor
        self.message = message


# Worker that receives an event and emits a signal in response
class Worker(QObject):
    messageProcessed = pyqtSignal(str)  # Signal emitted when an event is processed

    def __init__(self, name):
        super(Worker, self).__init__()
        self.name = name

    def event(self, event):
        if event.type() == StringEvent.EVENT_TYPE:
            print "[{}] Received message: {}".format(self.name, event.message)
            # Emit a signal when event is processed
            self.messageProcessed.emit("Processed by {}: {}".format(self.name, event.message))
            return True
        return super(Worker, self).event(event)


# Thread class that runs an event loop
class WorkerThread(QThread):
    def __init__(self, name):
        super(WorkerThread, self).__init__()
        self.worker = Worker(name)

    def run(self):
        self.exec_()  # Start event loop for this thread


# Sender that posts events to a worker
class Sender(QObject):
    def __init__(self, target_worker):
        super(Sender, self).__init__()
        self.target_worker = target_worker

    def send_event(self, message):
        print "Sending event:", message
        event = StringEvent(message)
        QCoreApplication.postEvent(self.target_worker, event)


# Slot to handle the signal emitted by Worker
def handle_message(response):
    print "Worker emitted signal:", response


# Main application
if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    # Create and start worker threads
    thread1 = WorkerThread("Thread1")
    thread2 = WorkerThread("Thread2")
    thread1.start()
    thread2.start()

    # Move workers to their respective threads
    worker1 = thread1.worker
    worker2 = thread2.worker
    worker1.moveToThread(thread1)
    worker2.moveToThread(thread2)

    # Connect worker signal to a handler
    worker1.messageProcessed.connect(handle_message)
    worker2.messageProcessed.connect(handle_message)

    # Create a sender and send events
    sender = Sender(worker1)
    sender2 = Sender(worker2)

    sender.send_event("Hello to Worker1!")
    sender2.send_event("Hello to Worker2!")

    sys.exit(app.exec_())
