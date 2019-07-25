import sys
import cv2 as cv
import numpy as np 

# Captura el cuadro de entrada
def get_frame(cap, scaling_factor=0.5): 
    ret, frame = cap.read() 

    # Cambiar el tamaño del marco
    frame = cv.resize(frame, None, fx=scaling_factor, 
            fy=scaling_factor, interpolation=cv.INTER_AREA) 

    return frame 

if __name__=='__main__': 
    # Inicializar el objeto de captura de video
    cap = cv.VideoCapture(0) 

    # Crear el objeto restador de fondo
    bgSubtractor = cv.createBackgroundSubtractorMOG2()

    # This factor controls the learning rate of the algorithm. 
    # The learning rate refers to the rate at which your model 
    # will learn about the background. Higher value for 
    # 'history' indicates a slower learning rate. You 
    # can play with this parameter to see how it affects 
    # the output. 
    history = 100 

    # Iterate until the user presses the ESC key 
    while True: 
        frame = get_frame(cap, 0.5) 

        # Apply the background subtraction model to the input frame 
        mask = bgSubtractor.apply(frame, learningRate=1.0/history)

        # Convert from grayscale to 3-channel RGB 
        mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR) 

        cv.imshow('Input frame', frame)
        cv.imshow('Moving Objects MOG', mask & frame)

        # Check if the user pressed the ESC key 
        c = cv.waitKey(delay=30) 
        if c == 27: 
            break 

    cap.release() 
    cv.destroyAllWindows()