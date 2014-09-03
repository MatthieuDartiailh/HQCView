# -*- coding: utf-8 -*-
# =============================================================================
# module : hqc_view/utils/log/tools.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
This module defines some tools to make easier the use of the logging module
in the program, first by seamlessly converting stream information into log
record so that any `print` can get recorded. And also by defining tools to
process log emitted in the measure process.

:Contains:
    StreamToLogRedirector
        Simple class to redirect a stream to a logger.
    QueueHandler
        Logger handler putting records into a queue.
    GuiConsoleHandler
        Logger handler adding the message of a record to a GUI panel.
    QueueLoggerThread
        Thread getting log record from a queue and asking logging to handle
        them.
"""
import logging, Queue, time, os, datetime, sys
from logging.handlers import TimedRotatingFileHandler
from inspect import cleandoc
from textwrap import fill
from threading import Thread
from enaml.application import deferred_call
from atom.api import Atom, Unicode
try:
    import codecs
except ImportError:
    codecs = None


class StreamToLogRedirector(object):
    """Simple class to redirect a stream to a logger.

    Stream like object which can be used to replace `sys.stdout`, or
    `sys.stderr`.

    Parameters
    ----------
    logger : instance(`Logger`)
        Instance of a loger object returned by a call to logging.getLogger
    stream_type : {'stdout', 'stderr'}, optionnal
        Type of stream being redirected. Stderr stream are logged as CRITICAL

    Attributes
    ----------
    logger : instance(`Logger`)
        Instance of a loger used to log the received message
    level : {logging.INFO, logging.CRITICAL}
        Default level to which logs the received messages

    Methods
    -------
    write(message)
        Log the received message to the correct level
    flush()
        Useless method implemented for compatibilty

    """
    def __init__(self, logger, stream_type='stdout'):
        self.logger = logger
        if stream_type == 'stderr':
            self.level = logging.CRITICAL
        else:
            self.level = logging.INFO
        self.encoding = sys.getdefaultencoding()

    def write(self, message):
        """Record the received message using the logger stored in `logger`

        The received message is first strip of starting and trailing
        whitespaces and line return. If `level` is `logging.CRITICAL` the
        message is directly logged, otherwise the message is parsed to look
        for the following markers, corresponding to logging levels :
        '<DEBUG>', '<WARNING>', '<ERROR>', '<CRITICAL>'. This allows to use
        different logging levels using print.

        """
        message = message.strip()
        message = message.decode(self.encoding)
        if message != '':
            if self.level != logging.CRITICAL:
                if '<DEBUG>' in message:
                    message = message.replace('<DEBUG>', '').strip()
                    self.logger.debug(message)
                elif '<WARNING>' in message:
                    message = message.replace('<WARNING>', '').strip()
                    self.logger.warn(message)
                elif '<ERROR>' in message:
                    message = message.replace('<ERROR>', '').strip()
                    self.logger.error(message)
                elif '<CRITICAL>' in message:
                    message = message.replace('<CRITICAL>', '').strip()
                    self.logger.critical(message)
                else:
                    self.logger.log(self.level, message)
            else:
                self.logger.critical(message)

    def flush(self):
        """Useless function implemented for compatibility
        """
        return None


# Copied and pasted from the logging module of Python 3.3
class QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    with a multiprocessing Queue to centralise logging to file in one process
    (in a multi-process application), so as to avoid file write contention
    between processes.

    """

    def __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method if you want to use blocking, timeouts or custom queue
        implementations.

        """
        self.queue.put_nowait(record)

    def prepare(self, record):
        """
        Prepares a record for queueing. The object returned by this
        method is enqueued.
        The base implementation formats the record to merge the message
        and arguments, and removes unpickleable items from the record
        in-place.
        You might want to override this method if you want to convert
        the record to a dict or JSON string, or send a modified copy
        of the record while leaving the original intact.

        """
        # The format operation gets traceback text into record.exc_text
        # (if there's exception data), and also puts the message into
        # record.message. We can then use this to replace the original
        # msg + args, as these might be unpickleable. We also zap the
        # exc_info attribute, as it's no longer needed and, if not None,
        # will typically not be pickleable.
        self.format(record)
        record.msg = record.message
        record.args = None
        record.exc_info = None
        return record

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it first.
        """
        try:
            self.enqueue(self.prepare(record))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class PanelModel(Atom):
    """ Simple model which can be used for a GuiHandler.

    """

    text = Unicode()


class GuiHandler(logging.Handler):
    """Logger record sending the log message to a GUI panel

    Parameters
    ----------
    model : Atom
        Model object with a text member.

    Methods
    -------
    emit(record)
        Handle a log record by appending the log message to the model

    """
    def __init__(self, model):
        logging.Handler.__init__(self)
        self.model = model

    def emit(self, record):
        """
        Write the log record message to the model. Use Html encoding to add
        colors, etc.

        """
        # TODO add coloring. Better to create a custom formatter
        msg = self.format(record)
        try:
            if record.levelname == 'INFO':
                deferred_call(self._write_in_panel, self.model,
                              msg + '\n')
            elif record.levelname == 'CRITICAL':
                deferred_call(self._write_in_panel, self.model,
                              fill(cleandoc('''An error occured please check
                                  the log file for more details.''')) + '\n')
            else:
                deferred_call(self._write_in_panel, self.model,
                              record.levelname + ': ' + msg + '\n')
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def _write_in_panel(self, model, string):
        """
        """
        if sys.platform == 'win32':
            string = string.decode('cp1252')
        model.text += string


class QueueLoggerThread(Thread):
    """Worker thread emptying a queue containing log record and asking the
    appropriate logger to handle them.

    """

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        """
        Pull any output from the queue while the listened process does not put
        `None` into the queue
        """
        while True:
            # Collect all display output from process
            try:
                record = self.queue.get()
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except Queue.Empty:
                continue


class DayRotatingTimeHandler(TimedRotatingFileHandler):
    """ Custom implementation of the TimeRotatingHandler to avoid issues on
    win32.

    """
    def __init__(self, filename, when='midnight', **kwargs):
        self.when = when.upper()
        super(DayRotatingTimeHandler, self).__init__(filename, when=when,
                                                     **kwargs)

    def _open(self):
        """
        Open the a file named accordingly to the base name and the time of
        creation of the file with the (original) mode and encoding.
        Return the resulting stream.
        """
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')):
            today = str(datetime.datetime.today()).split(' ')[0]
        else:
            aux = str(datetime.datetime.today()).split('.')[0]
            aux = aux.replace(' ', '_')
            today = aux.replace(':', '-')

        base_dir, base_filename = os.path.split(self.baseFilename)
        aux = base_filename.split('.')
        filename = aux[0] + today + '.' + aux[1]
        path = os.path.join(base_dir, filename)

        if self.encoding is None:
            stream = open(path, self.mode)
        else:
            stream = codecs.open(path, self.mode, self.encoding)
        return stream

    def doRollover(self):
        """Do a rollover. Close old file and open a new one, no renaming is
        performed to avoid issues on window.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]

        for s in self.getFilesToDelete():
            os.remove(s)

        self.stream = self._open()

        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if ((self.when == 'MIDNIGHT' or self.when.startswith('W'))
                and not self.utc):
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                # DST kicks in before next rollover, so we need to deduct an
                # hour
                if not dstNow:
                    addend = -3600

                # DST bows out before next rollover, so we need to add an hour
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
