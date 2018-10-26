from gsfilelock import gsfilelock
import time

print( "getting lock" )
#with gsfilelock.GsFileLock( "test.txt", 3, 1000, lock_expire_hr=20.0/60/60 ):
with gsfilelock.GsFileLock( "test.txt", 3, 1000, lock_expire_hr=None ):
    print( "in lock" )
    for i in range( 5 ):
        print( str(i) )
        time.sleep( 1 )
print( "out of lock" )
