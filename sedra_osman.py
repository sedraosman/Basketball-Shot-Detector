import math
import cv2
import cvzone
from cvzone.ColorModule import ColorFinder
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


score = 0  

def load_video():
 
    file_path = filedialog.askopenfilename(title="Select Video", filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*")))
    if file_path:
        process_video(file_path)

def process_video(video_path):
    global score  
    cap = cv2.VideoCapture(video_path)

   
    myColorFinder = ColorFinder(False)
    hsvVals = {'hmin': 8, 'smin': 96, 'vmin': 115, 'hmax': 14, 'smax': 255, 'vmax': 255}

    
    posListX, posListY = [], []
    xList = [item for item in range(0, 1300)]
    prediction = False
    basket_found = False  


    canvas_width = 640
    canvas_height = 480
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="black")  

    while True:
        
        success, img = cap.read()
        if not success:
            break 

        img = img[0:900, :]

       
        imgColor, mask = myColorFinder.update(img, hsvVals)
        
        imgContours, contours = cvzone.findContours(img, mask, minArea=500)

        if contours:
            posListX.append(contours[0]['center'][0])
            posListY.append(contours[0]['center'][1])

        if posListX:
            #  y = Ax^2 + Bx + C
            
            A, B, C = np.polyfit(posListX, posListY, 2)

            for i, (posX, posY) in enumerate(zip(posListX, posListY)):
                pos = (posX, posY)
                cv2.circle(imgContours, pos, 10, (0, 255, 0), cv2.FILLED)
                if i == 0:
                    cv2.line(imgContours, pos, pos, (0, 255, 0), 5)
                else:
                    cv2.line(imgContours, pos, (posListX[i - 1], posListY[i - 1]), (0, 255, 0), 5)

            for x in xList:
                y = int(A * x ** 2 + B * x + C)
                cv2.circle(imgContours, (x, y), 2, (255, 0, 255), cv2.FILLED)

            if len(posListX) < 10:
              
                # X values 330 to 430  Y 590
                a = A
                b = B
                c = C - 590

                x = int((-b - math.sqrt(b ** 2 - (4 * a * c))) / (2 * a))
                prediction = 330 < x < 430

               
                if prediction and not basket_found:
                    score += 1  
                    basket_found = True 
           
            if prediction:
                result_text.set(f"Basket! Score: {score}")
            else:
                result_text.set(f"No Basket. Score: {score}")

        
        imgContours = cv2.resize(imgContours, (canvas_width, canvas_height))

       
        img_rgb = cv2.cvtColor(imgContours, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

       
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk  

        
        root.update_idletasks()
        root.update()

        
        cv2.waitKey(1)

        
        if not prediction:
            basket_found = False

    
    cap.release()


root = tk.Tk()
root.title("Load Video")
root.geometry("800x600") 


canvas = tk.Canvas(root, width=640, height=480)
canvas.pack(padx=20, pady=20)


load_button = tk.Button(root, text="Load Video", font=("Arial", 20), command=load_video)
load_button.pack(pady=10)


result_label_title = tk.Label(root, text="Result:", font=("Arial", 16))
result_label_title.pack()


result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, font=("Arial", 20))
result_label.pack(pady=20)


root.mainloop()
