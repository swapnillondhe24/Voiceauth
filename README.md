# Voice-Authentication-CNN
A simple Voice Authentication system using pre-trained Convolutional Neural Network.

## Enrollment:
Enroll a new user using an audio file of his/her voice

``python voice_auth.py -t enroll -n "name of person" -f ./Test/audio.wav``

## Enrollment using csv:
Enroll mutiple users using a .csv file containing list of names and file paths respectively

``python voice_auth.py -t enroll -f ./Test/audio.wav``

 
## Recognition:
Authenticate a user if it matches voice prints saved on the disk

``python voice_auth.py -t recognize -f ./Test/audio.wav``


