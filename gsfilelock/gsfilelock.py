# Copyright (c) 2009, Evan Fosmark
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.

import os
import time
import errno
import random
import sys
import tensorflow as tf

class GsFileLockException(Exception):
    pass

class GsFileLock(object):
    """ A file locking mechanism that has context-manager support so
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
        Compatible with Google Buckets.  Includes a delay each time a lock is acquired
        to allow for consistency to propigate.
    """

    __slots__ = ('is_locked', 'consistency_time', 'lockfile', 'file_name', 'timeout', 'delay', 'id')

    def __init__(self, file_name, consistency_time, timeout=10, delay=.05, id=None):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.is_locked = False
        self.consistency_time = consistency_time
        self.lockfile = os.path.join(os.getcwd(), "%s.lock" % file_name)
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay
        if id:
            self.id = id
        else:
            self.id = random.uniform(0,sys.maxsize)


    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        start_time = time.time()
        pid = os.getpid()
        checkString = "<" + str(pid) + "." + str( self.id ) + ">"
        while not self.is_locked:
            
            if not tf.gfile.Exists( self.lockfile ):
                print( "writing to lock file at " + str( self.lockfile) )
                #write our number to it.
                with tf.gfile.Open( self.lockfile, "w" ) as writer:
                    writer.write( checkString )

                print( "Maybe..." + checkString )

                #give time for someone else to accidentally overwrite our file.
                time.sleep( self.consistency_time )

                #now read the file again and see if it has our number.
                with tf.gfile.Open( self.lockfile, "r" ) as reader:
                    readString = reader.readline()

                #if it does then say we won.
                if readString.startswith( checkString ):
                    self.is_locked = True
            #else:
            #    print( "file currently exists" + self.lockfile )
            
            if not self.is_locked:
                if (time.time() - start_time) >= self.timeout:
                    raise GsFileLockException("Timeout occured.")
                time.sleep(self.delay)
        


    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        if self.is_locked:
            tf.gfile.Remove( self.lockfile )
            self.is_locked = False


    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self


    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()
