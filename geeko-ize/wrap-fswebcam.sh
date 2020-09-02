# version 2 of this short script
# A simple way to test functionality from a webcam before trying to use it with
#  an app, such as an OpenCV python script
# original was for hackweek 15
# joadavis

filename=`date -Ins`
filename="video0-$filename".jpg

# built in is device 0
# fswebcam -d /dev/video0 --list-controls
#fswebcam -d /dev/video0 -r "640x480" $filename
fswebcam -d /dev/video0 -r "1920x1080" $filename
# on an HP z15 that created an image of 1280x720, likely the highest resolution it supported

# logitech external camera was video1
#fswebcam -d /dev/video1 -r "640x480" test-video1.jpg

# test video frames - creates a composited blurred image
#fswebcam -d /dev/video0 -r "640x480" -F100 --fps 15 vid0out

