from gsfilelock import gsfilelock
import time

print( "getting lock" )
with gsfilelock.GsFileLock( "test.txt", 3, 1000 ):
    print( "in lock" )
    for i in range( 5 ):
        print( str(i) )
        time.sleep( 1 )
print( "out of lock" )
