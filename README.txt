
========
GsFileLock
========

    A file locking mechanism that has context-manager support so 
    you can use it in a with statement. This should be relatively cross
    compatible as it doesn't rely on msvcrt or fcntl for the locking.
    Compatible with Google Buckets.  Includes a delay each time a lock is acquired
    to allow for consistency to propigate.
    

    Originally posted at http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/
