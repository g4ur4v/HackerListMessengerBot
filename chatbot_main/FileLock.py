import os
import logging

logger = logging.getLogger('django')

class FileLock:
    def __init__(self, filename):
        self.filename = filename
        self.fd = None

    def acquire(self):
        try:
            self.fd = os.open(self.filename, os.O_CREAT|os.O_EXCL|os.O_RDWR)
            logger.debug('Lock acquired')
            return True
        except OSError:
            logger.error('Unable to acquire Lock')
            self.fd = None
            return False

    def release(self):
        if not self.fd:
            return False
        try:
            os.close(self.fd)
            os.remove(self.filename)
            self.fd = None
            logger.debug('Lock released')
            return True
        except OSError:
            return False

    def poll(self):
        while os.path.isfile(self.filename):
            pass

    def __del__(self):
        self.release()