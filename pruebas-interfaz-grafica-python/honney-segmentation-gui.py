#https://stackoverflow.com/questions/31684375/automatically-create-file-requirements-txt
import tkinter as tk # GUI library imported
import tkinter.filedialog # to create open files windows and folders
import tkinter.ttk
import os # to manage actions of the operating system
import os.path
import keras
import tensorflow as tf
from keras.models import Model, load_model
#os.environ["SM_FRAMEWORK"] = "tf.keras"
import segmentation_models as sm # Segmentation Models: using `keras` framework.
from keras import backend as K
import random
import sys
import cv2 # opencv library to process images
import PIL.Image, PIL.ImageTk
import numpy as np
import math
from pathlib import Path
import shutil # to delete no empty folders
import time # library to get current date



app_version = 1
last_app_released_date = time.strftime("%Y-%m-%d") # last app version is today



#------------------------------------------------------------
# funcion auxiliar para hacer el split de las imagenes
#------------------------------------------------------------
def start_points(size, split_size, overlap=0):
  points = [0]
  stride = int(split_size * (1-overlap))
  counter = 1

  while True:
    pt = stride * counter

    if pt + split_size >= size:
      if split_size == size:
        break
      points.append(size - split_size)
      break

    else:
      points.append(pt)
    counter += 1
  return points
#------------------------------------------------------------

#------------------------------------------------------------
def get_file_names_with_strings(imagesPath, str_value):
  full_list = sorted((f for f in os.listdir(imagesPath) if not f.startswith(".")), key=str.lower)
  final_list = [nm for nm in full_list if str_value in nm]

  return final_list
#------------------------------------------------------------


def read_image(img_path, IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS):
  image = tf.io.read_file(img_path)
  image = tf.image.decode_image(image, channels=IMG_CHANNELS, expand_animations = False)
  image = tf.image.convert_image_dtype(image, tf.float32)
  image.set_shape((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))
  return image



def create_mask(pred_mask):
  pred_mask = tf.argmax(pred_mask, axis=-1)
  pred_mask = pred_mask[..., tf.newaxis]
  return pred_mask[0]












class openCVmouseEventStore:
  def __init__(self):
    self.drawing = False # true if mouse is pressed
    self.s_x = None
    self.s_y = None
    self.e_x = None
    self.e_y = None      

  # mouse callback function
  def line_drawing(self,event,x,y,flags,param):
    if event==cv2.EVENT_LBUTTONDOWN:
      self.drawing=True
      self.s_x, self.s_y = x, y
      self.e_x, self.e_y = x, y
    elif event==cv2.EVENT_MOUSEMOVE:
      if self.drawing==True:
#        cv2.line(param[5], (self.s_x, self.s_y),(x,y),color=(0,0,255),thickness=3)
        self.e_x, self.e_y = x, y
    elif event==cv2.EVENT_LBUTTONUP:
      self.drawing=False
      self.e_x, self.e_y = x, y
#      cv2.line(param[5], (self.s_x, self.s_y),(x,y),color=(0,0,255),thickness=3) 





class HoneySegmentationToolGUI(tk.Tk):
  def __init__(self, image_path=None):
    super().__init__()

    # variables to store paths, image data and so on...
    #--------------------------------------------------
    self.opencvImg = None
    self.opencvMask = None
    self.opencvMaskApply = None
    self.appIcon = Path("defaults/icons/icon.png")  
    self.imgDefaultLoad = Path("defaults/previewImages/defaultImageLoad.png")
    self.imgDefaultProcess = Path("defaults/previewImages/defaultImageProcess.png")  
    
    self.imgPath = None
    self.splittedPath = None
    self.saveFolderPath = None
    self.honeySegmentationModelPath = Path("defaults/honeyModels/efficientnetb2-FPN.keras")
    self.frameSegmentationModelPath = None
    self.referenceValue = 0
    self.lavelImgagePreview = None
    self.lavelSegmentedImgage = None    
    self.varLabelInformationText = tk.StringVar()
    self.progressBar = None
    self.cmToPixelRelation = 0
    self.cmEntry = 0
    self.areaOfHoney = 0
    
    self.processButtom = None
    self.referenceButtom = None
    self.saveButtom = None
    #--------------------------------------------------

    self.title('HoneyBee Segmetation Tool GUI') # main window title

    self.geometry("1366x768") # init window size
    self.minsize(1366, 768) # minimum window size
    self.maxsize(1366, 768) # maximum window size
    #self.iconbitmap("icon.png")
    self.call('wm', 'iconphoto', self._w, PIL.ImageTk.PhotoImage(file=str(self.appIcon)))
     
    
    self.image = None   # Image used for image processing
    self.resized_image=None
    self.tkimage = None # Image used to display in tkinter label
    self.tkimagePreview = None # Image used to display in tkinter label
    self.tkimageSegmented = None # Image used to display in tkinter label
         
    self.display = tk.Label(self)
    self.display.pack(expand=True, fill=tk.BOTH)
 
 
    menuTabs = tk.Menu(self)
    self.config(menu=menuTabs)

    fileMenu = tk.Menu(menuTabs)
    menuTabs.add_cascade(label='File', menu=fileMenu)
    fileMenu.add_command(label='Select file', command=self.load_image)
    fileMenu.add_command(label='Start Batch mode', command= self.batchModeWindows)
    fileMenu.add_separator()
    fileMenu.add_command(label='Exit', command=self.quit)

    preferencesMenu = tk.Menu(menuTabs)
    menuTabs.add_cascade(label='Preferences', menu=preferencesMenu)
    preferencesMenu.add_command(label='Load custom frame segmentation model', command=lambda: self.load_file_path(1))
    preferencesMenu.add_command(label='Load custom honey segmentation model', command=lambda: self.load_file_path(2))

    helpMenu = tk.Menu(menuTabs)
    menuTabs.add_cascade(label='Help', menu=helpMenu)
    helpMenu.add_command(label='About', command= self.aboutWindow) 
 
 
    left_frame = tk.Frame(self, width=450, height=700, bg='grey')
    left_frame.pack(side='left',  fill='both',  padx=10,  pady=20,  expand=True)

    right_frame = tk.Frame(self, width=850, height=700, bg='grey')
    right_frame.pack(side='right',  fill='both',  padx=10,  pady=20,  expand=True)

 
 
 
 
 
 
    # Make a frame to pack the buttons horizontally
    openExitButtons = tk.Frame(left_frame)
    openExitButtons.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
 
 
    # Make buttons to load image, save image and quit
    button = tk.Button(openExitButtons, text="LOAD IMAGE", command=self.load_image)
    button.pack(side=tk.LEFT, expand=True, fill=tk.X)
#    button = tk.Button(openExitButtons, text="SAVE FILE", command=self.save_image)
#    button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
    button = tk.Button(openExitButtons, text="EXIT", command=self.destroy)
    button.pack(side=tk.LEFT, expand=True, fill=tk.X) 
 
 
    im = PIL.Image.open(str(self.imgDefaultLoad))
    resized_img = im.resize((256, 256))
    self.tkimagePreview = PIL.ImageTk.PhotoImage(resized_img)
#    original_image = self.tkimage.subsample(3,3)
    self.lavelImgagePreview = tk.Label(left_frame, image=self.tkimagePreview)
    self.lavelImgagePreview.pack(fill=tk.X, padx=5, pady=5) 
 

    im = PIL.Image.open(str(self.imgDefaultProcess))
    resized_img = im.resize((830, 680))
    self.tkimageSegmented = PIL.ImageTk.PhotoImage(resized_img)    
    self.lavelSegmentedImgage = tk.Label(right_frame, image=self.tkimageSegmented)
    self.lavelSegmentedImgage.pack(fill=tk.X, padx=5, pady=5) 
 


 
    referenceFrame = tk.Frame(left_frame)
    referenceFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
  
    self.referenceButtom = tk.Button(referenceFrame, text='Find reference', command=self.find_reference)
    self.referenceButtom.pack(side=tk.TOP, expand=True, fill=tk.X, pady=5) # add a button to go back to main window and       
    self.referenceButtom["state"] = "disabled"

    tk.Label(referenceFrame, text="Specify cm per pixel").pack(side=tk.LEFT, expand=True, fill=tk.X)
    self.cmToPixelRelation = tk.Entry(referenceFrame)
    self.cmToPixelRelation.delete(0,tk.END)
    self.cmToPixelRelation.insert(0,"0")
    self.cmToPixelRelation.pack(expand=True, fill=tk.X)
    referenceButtom = tk.Button(referenceFrame, text='Click to apply', command=lambda: self.get_entry(self.cmToPixelRelation, self.referenceValue))
    referenceButtom.pack(side=tk.LEFT, expand=True, fill=tk.X) # add a button to go back to main window and close about window 

    processFrame = tk.Frame(left_frame)
    processFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    self.processButtom = tk.Button(processFrame, text='Process Image     >>>', command=lambda: self.segmentationProcess(640, 640, 3))
    self.processButtom.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5,  pady=5) # add a button to go back to main window and close about window     
    self.processButtom["state"] = "disabled"

  


    informationImageFrame = tk.Frame(left_frame)
    informationImageFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    label=tk.Label(informationImageFrame, text="IMAGE INFORMATION")
    label.config(font=("bold"))
    label.pack(side=tk.TOP, expand=True, fill=tk.X)

    
    self.varLabelInformationText.set("Image Name: -\nImage Size: -x-\nPercentage of honey: - %    Area of honey: - cm")
    tk.Label(informationImageFrame, textvariable=self.varLabelInformationText,wraplength=450 - 20).pack(side=tk.BOTTOM, expand=True, fill=tk.X)

    saveFrame = tk.Frame(left_frame)
    saveFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    self.saveButtom = tk.Button(saveFrame, text='Save result', command=self.saveResults)
    self.saveButtom.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5,  pady=5) # add a button to go back to main window and close about window   
    self.saveButtom["state"] = "disabled"
    
    progressBarFrame = tk.Frame(left_frame)
    progressBarFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    # Create a progressbar widget
    self.progressBar = tk.ttk.Progressbar(progressBarFrame, orient="horizontal", length=300, mode="determinate")
    self.progressBar.pack(fill=tk.X, padx=5,  pady=5)
    
    
    
#    print (self.referenceValue)
    


#    print(self.imgPath)


  def mergeImages(self, path, split_width, split_height):
    pathParser = Path(path)

    pathFolder = pathParser.parents[0]
    imageName = pathParser.name
    
    valid_images_format = [".jpg",".jpeg",".png"] # formatos de imagenes admitidos

    img = cv2.imread(pathFolder/imageName)
    img_h, img_w, _ = img.shape
    final_image = np.zeros_like(img) # creamos imagen llena de ceros

    X_points = start_points(img_w, split_width, 0.5)
    Y_points = start_points(img_h, split_height, 0.5)

    image_name = os.path.splitext(imageName)[0] #obtenemos el nombre de la imagen sin extension
    image_ext = (os.path.splitext(imageName)[1])[1:] #obtenemos la extension de la imagen sin el punto
    splitted_images_list = get_file_names_with_strings(str(pathFolder/"splittedImages"/"predictions"), image_name) #obtenemos la lista de imagenes que coincide con la variable 'image'
  
    splitted_images_loaded_in_memory = [] #lista de imagenes para guardarlas en memoria
  
    # rellenamos la variable splitted_images_loaded_in_memory con imagenes que tienen la cadena que contiene la variable 'image' dentro de su nombre
    for splitted_image in splitted_images_list:
      splitted_images_loaded_in_memory.append(cv2.imread(str(pathFolder/"splittedImages"/"predictions"/splitted_image)))

    # generamos la imagen completa y la guardamos en un nuevo directorio
    index = 0
    for i in Y_points:
      for j in X_points:
        final_image[i:i+split_height, j:j+split_width] = cv2.bitwise_or(final_image[i:i+split_height, j:j+split_width],splitted_images_loaded_in_memory[index])
        index += 1        

    self.opencvMask = final_image.copy()
#    print(self.opencvMask.shape)
#    cv2.imwrite('{}_{}.{}'.format(str(pathFolder / image_name), "predictionMak", image_ext), final_image)



  def calculateAreaofHoney(self, mask):
  
#    print(mask.shape)
    #https://docs.opencv.org/4.x/d1/d32/tutorial_py_contour_properties.html
    numberofWhitePixels = cv2.countNonZero(cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
    
    self.areaOfHoney = round(float(self.cmToPixelRelation.get()) * numberofWhitePixels, 4)
    self.varLabelInformationText.set("Image Name:" + self.imgPath + "\nImage Size: " + str(self.opencvImg.shape[0]) + "x" + str(self.opencvImg.shape[1]) + "\nPercentage of honey: - %    Area of honey: " + str(self.areaOfHoney) + " cm")
    self.update()

  def applySegmentation(self, img, mask):

    color = np.array([255,0,0], dtype='uint8')
    # equal color where mask, else image
    # this would paint your object silhouette entirely with `color`
    

    masked_img = np.where(mask, color, img)

    # use `addWeighted` to blend the two images
    # the object will be tinted toward `color`
    self.opencvMaskApply  = cv2.addWeighted(img, 0.6, masked_img, 0.4,0)




    
#    self.imgDefaultProcess = cv2.cvtColor(self.opencvMaskApply, cv2.COLOR_BGR2RGB)
    self.imgDefaultProcess = cv2.resize(self.opencvMaskApply, (830, 680))
 
    # Convert image to tkinter image format and display
    self.tkimageSegmented = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.imgDefaultProcess))
    self.lavelSegmentedImgage.config(image=self.tkimageSegmented)
    self.update()

  def saveResults(self):
  
    saveFolder = Path(tk.filedialog.askdirectory())
       
    pathParser = Path(self.imgPath)
    imageName = pathParser.name
    
    image_name = os.path.splitext(imageName)[0] #obtenemos el nombre de la imagen sin extension
    image_ext = (os.path.splitext(imageName)[1])[1:] #obtenemos la extension de la imagen sin el punto

    cv2.imwrite('{}_{}.{}'.format(str(saveFolder / image_name), "honey-Mask", image_ext), self.opencvMask)
    cv2.imwrite('{}_{}.{}'.format(str(saveFolder / image_name), "honey-Highlighted", image_ext), cv2.cvtColor(self.opencvMaskApply, cv2.COLOR_BGR2RGB))


  def splitImages(self, path, split_width, split_height):
    pathParser = Path(path)

    pathFolder = pathParser.parents[0]
    imageName = pathParser.name

    valid_images_format = [".jpg",".jpeg",".png"] # formatos de imagenes admitidos
    self.splittedPath = pathFolder / "splittedImages" #directorio para guardar el resultado de la division
    
    nameadd = 'splitted' #nombre de las imagenes divididas
    frmt = 'JPG' #formato para guardar las imagenes divididas

    # codigo para crear un directorio. Si el directorio existe lanza una excepción, por eso se mete en un try-except
    try:
      os.makedirs(self.splittedPath)
    except FileExistsError:
      # directory already exists
      pass

    name = os.path.splitext(imageName)[0]
    img = cv2.imread(pathFolder/imageName)
    img_h, img_w, _ = img.shape

    X_points = start_points(img_w, split_width, 0.5)
    Y_points = start_points(img_h, split_height, 0.5)

    count = 0

    for i in Y_points:
      for j in X_points:
        split = img[i:i+split_height, j:j+split_width]
        saveTileName = str(self.splittedPath / name) + '_{}_{:0=5}.{}'.format(nameadd, count, frmt)
        cv2.imwrite(saveTileName, split) # le he metido un padding de 5 ceros a la izquierda a los numeros del contador
        count += 1





  def segmentationProcess(self, IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS):

    self.progressBar.start()

    self.splitImages(self.imgPath, IMG_HEIGHT, IMG_WIDTH)
    
    self.progressBar['value'] = 10
    self.update_idletasks()  
    
    resultPath = self.splittedPath / "predictions"
    
    reconstructed_model = keras.models.load_model(self.honeySegmentationModelPath)
    valid_images_format = [".jpg",".jpeg",".png"] # formatos de imagenes admitidos
    

    frmt = 'png' #formato para guardar las imagenes divididas

    # codigo para crear un directorio. Si el directorio existe lanza una excepción, por eso se mete en un try-except
    try:
      os.makedirs(resultPath)
    except FileExistsError:
      # directory already exists
      pass

    image_list = [] # variable para guardar el listado de imagenes 

    #leemos la lista de ficheros dentro de un directorio
    for filename in os.listdir(self.splittedPath):
      ext = os.path.splitext(filename)[1] #nos quedamos con la extension de cada uno de los ficheros
  
      if ext.lower() not in valid_images_format: #pasamos la extension a minusculas y comprobamos si la extension esta en la lista
        continue # si no esta en la lista continuamos
      image_list.append(filename) # si esta en la lista de formatos admitidos, guardamos el nombre de la imagen en la lista


    cont = 1
    for imageName in image_list:
#      print("Imagen {0:2d}/{1:2d}: {other}".format(cont, len(image_list), other=imageName))
      test_image = read_image(str(self.splittedPath / imageName), IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS) 

      test_image = np.expand_dims(test_image, axis = 0)

      #predict the result
      prediction = reconstructed_model.predict(test_image)
      prediction = (prediction > 0.5).astype(np.uint8) # sin esto se muestran valores que no son 0-255 pero puede que sea interesante para umbralizar mas fino.


      i3 = prediction[0, :, :, 0] # Shape is (224, 224) here
      i3 = (i3*255).astype(np.uint8) # scale to 0-255  range and convert to int
      nameImageToSave = os.path.splitext(imageName)[0]
      cv2.imwrite('{}.{}'.format(str(resultPath / nameImageToSave), frmt), i3) # le he metido un padding de 5 ceros a la izquierda a los numeros del contador

      self.progressBar['value'] = round(70.0 * cont / float(len(image_list)), 1) + 10
      self.update_idletasks()  

      cont = cont + 1


    self.mergeImages(self.imgPath, IMG_HEIGHT, IMG_WIDTH)
    
    self.progressBar['value'] = 80
    self.update_idletasks()  
    self.applySegmentation(self.opencvImg, self.opencvMask)
    
    self.progressBar['value'] = 90
    self.update_idletasks()  
    self.calculateAreaofHoney(self.opencvMask)
    
    # removing directory 
    shutil.rmtree(str(self.splittedPath), ignore_errors = True) 
    
    self.progressBar['value'] = 100
    self.update_idletasks()   


    # Simulate a task that takes time to complete
#    for i in range(101):
      # Simulate some work
#        time.sleep(0.05)  
#        self.progressBar['value'] = i
        # Update the GUI
#        self.update_idletasks()  
    self.progressBar.stop()

    self.saveButtom["state"] = "normal"


  def get_entry(self, entry, saveEntryVar): 
    saveEntryVar = entry.get() 
#    print (self.referenceValue)


  def load_file_path(self, typeOfFile):
    modelTypes = (
                 ('model files', '*.keras'),
                 ('All files', '*.*')
                 )
    imageTypes = (
                 ('JPG', '*.jpg .JPG'),      
                 ('JPEG', '*.jpeg *.JPEG'),
                 ('PNG', '*.png *.PNG'),                              
                 ('All files', '*.*')
                 )    
                 
    if typeOfFile == 1:
      self.frameSegmentationModelPath = tk.filedialog.askopenfilename(title='Select a model', filetypes=modelTypes)
    elif typeOfFile == 2:
      self.honeySegmentationModelPath = tk.filedialog.askopenfilename(title='Select a model', filetypes=modelTypes)    
    elif typeOfFile == 3:
      self.imgPath = tk.filedialog.askopenfilename(title='Select an image', filetypes=imageTypes)


  def batchModeWindows(self): 
    batchWindow = tk.Toplevel() # generate a new child window
    batchWindow.grab_set() # keep focus in this new window and prevent to interact with the main window

    batchWindow.title('HoneyBee Segmetation Tool GUI [BATCH MODE]') # main window title
    batchWindow.geometry("1366x768") # init window size
    batchWindow.minsize(1366, 768) # minimum window size
    batchWindow.maxsize(1366, 768) # maximum window size

    tk.Button(batchWindow, text='Exit', command=batchWindow.destroy).pack() # add a button to go back to main window and close about window 



 
  def aboutWindow(self): 
    aboutMessageWindow = tk.Toplevel() # generate a new child window
    aboutMessageWindow.grab_set() # keep focus in this new window and prevent to interact with the main window

    message = "App version: " + str(app_version) + "\n" + \
              "App date: " + last_app_released_date + "\n" + \
              "This application was developed by r: xxxxxx"

    tk.Label(aboutMessageWindow, text=message).pack() # add message information as text label to about window

    tk.Button(aboutMessageWindow, text='Exit', command=aboutMessageWindow.destroy).pack() # add a button to go back to main window and close about window 
 
 
  def load_image(self):
    """Select an image to display"""
    self.load_file_path(3)
    if self.imgPath:
      # Read image and convert to RGB
      self.opencvImg = cv2.imread(self.imgPath)
      self.opencvImg = cv2.cvtColor(self.opencvImg, cv2.COLOR_BGR2RGB)
      self.resized_image = cv2.resize(self.opencvImg, (640, 480))
 
      # Convert image to tkinter image format and display
      self.tkimage = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.resized_image))
      

      resized_imgPreview = cv2.resize(self.opencvImg, (256, 256))
      self.tkimagePreview = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(resized_imgPreview))
      
#      self.display["image"] = self.tkimage
#      self.lavelImgageInformation["text"] = "Image Name:"# + self.imgPath + "\nImage Size:\nPercentage of honey:\nArea of honey:"
      self.lavelImgagePreview.config(image=self.tkimagePreview)
      rows, cols, _ = self.opencvImg.shape
      self.varLabelInformationText.set("Image Name:" + self.imgPath + "\nImage Size: " + str(cols) + "x" + str(rows) + "\nPercentage of honey: - %    Area of honey: - cm")
      self.referenceButtom["state"] = "normal"
      self.processButtom["state"] = "normal"
      self.update()
 
  def save_image(self):
    """Save image to a file"""
    filename = filedialog.asksaveasfilename(defaultextension='.jpg')
    if filename:
      # Convert image to BGR and write to file.
      cv2.imwrite(filename, cv2.cvtColor(self.opencvImg, cv2.COLOR_RGB2BGR))


  def calculateDistanceResized(self, sX, sY, eX, eY, originalWidth, originalHeight, paintedWidth, paintedHeight):
    Original_sX = (sX/paintedWidth)*originalWidth
    Original_sY = (sY/paintedHeight)*originalHeight
    
    Original_eX = (eX/paintedWidth)*originalWidth
    Original_eY = (eY/paintedHeight)*originalHeight
       
    difX = Original_eX-Original_sX
    difY = Original_eY-Original_sY
    
    euclideanDistance = math.sqrt(pow(difX,2) + pow(difY,2))

    return euclideanDistance
    

  def calculeReferenceValue(self, entry, distance):
    self.referenceValue = float(entry.get()) / distance
    self.cmToPixelRelation.delete(0,tk.END)
    self.cmToPixelRelation.insert(0,str(self.referenceValue))

    
 
  def find_reference(self):
#    self.opencvImg = cv2.cvtColor(self.opencvImg, cv2.COLOR_RGB2BGR)
    cv2.namedWindow("Select a line defining the reference in the image", cv2.WINDOW_NORMAL) 
    
#    clearImage = self.opencvImg
    mouseLineCoordinates = openCVmouseEventStore()

    cv2.setMouseCallback('Select a line defining the reference in the image', mouseLineCoordinates.line_drawing)  

    while True:
      clearImage = cv2.cvtColor(self.opencvImg, cv2.COLOR_RGB2BGR)
      
#      cv2.imshow("self.opencvImg", self.opencvImg)
      
      cv2.line(clearImage, (mouseLineCoordinates.s_x, mouseLineCoordinates.s_y), (mouseLineCoordinates.e_x, mouseLineCoordinates.e_y), color=(0,0,255), thickness=12)

      cv2.imshow("Select a line defining the reference in the image", clearImage)
      cv2.waitKey(10)
      
#      print("start: ("+str(mouseLineCoordinates.s_x)+","+str(mouseLineCoordinates.s_y)+")  end: ("+str(mouseLineCoordinates.e_x)+","+str(mouseLineCoordinates.e_y)+")")
      
      if cv2.getWindowProperty("Select a line defining the reference in the image", cv2.WND_PROP_VISIBLE) <1:
        break
      (x, y, windowWidth, windowHeight) = cv2.getWindowImageRect("Select a line defining the reference in the image") 
      #print("Origin Coordinates(x,y): ", x, y) 
      #print("Width: ", windowWidth) 
      #print("Height: ", windowHeight) 
      
    distance = self.calculateDistanceResized(mouseLineCoordinates.s_x, mouseLineCoordinates.s_y, mouseLineCoordinates.e_x, mouseLineCoordinates.e_y, self.opencvImg.shape[1], self.opencvImg.shape[0], windowWidth, windowHeight)
    
    cv2.destroyWindow("Select a line defining the reference in the image") 
    insertCentimetersInRealLifeWindow = tk.Toplevel() # generate a new child window
    insertCentimetersInRealLifeWindow.grab_set() # keep focus in this new window and prevent to interact with the main window

    referenceFrame = tk.Frame(insertCentimetersInRealLifeWindow)
    referenceFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    
    tk.Label(referenceFrame, text="Measure in cm").pack(side=tk.LEFT, expand=True, fill=tk.X)
    self.cmEntry = tk.Entry(insertCentimetersInRealLifeWindow)
    self.cmEntry.pack(expand=True, fill=tk.X)
    cmButtom = tk.Button(insertCentimetersInRealLifeWindow, text='Click to apply', command=lambda: self.calculeReferenceValue(self.cmEntry, distance))
    cmButtom.pack()
    
    
    
    tk.Button(insertCentimetersInRealLifeWindow, text='Exit', command=insertCentimetersInRealLifeWindow.destroy).pack() # add a button to go back to main window and close about window 




HoneySegmentationToolGUI().mainloop()




'''








































#------------------------------------------------------------------------------------------------------------------------------------------------------------------
def aboutWindow(): 
  aboutMessageWindow = tk.Toplevel() # generate a new child window
  aboutMessageWindow.grab_set() # keep focus in this new window and prevent to interact with the main window

  message = "App version: " + str(app_version) + "\n" + \
            "App date: " + last_app_released_date + "\n" + \
            "This application was developed by r: xxxxxx"

  tk.Label(aboutMessageWindow, text=message).pack() # add message information as text label to about window

  tk.Button(aboutMessageWindow, text='Exit', command=aboutMessageWindow.destroy).pack() # add a button to go back to main window and close about window
#------------------------------------------------------------------------------------------------------------------------------------------------------------------









#------------------------------------------------------------------------------------------------------------------------------------------------------------------
def select_directory():
#    filetypes = (
#        ('text files', '*.txt'),
#        ('All files', '*.*')
#    )

  folder_selected = tk.filedialog.askdirectory()

#  print(folder_selected)
 
  global folderImagePath 
  
  folderImagePath = folder_selected
  
  return folder_selected
#    filename = tk.filedialog.askopenfilename(
#        title='Select a folder')#,
#        initialdir='/')#,
#        filetypes=filetypes)

#    showinfo(
#        title='Selected folder',
#        message=filename
#    )
#------------------------------------------------------------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
def RefreshList(MyListBox):
  folderDir = select_directory()
  myList = os.listdir(folderDir)
#  print(myList)
  
  MyListBox.delete(0, tk.END)
#  myList.delete(0, END)
  for file in myList:
   MyListBox.insert(tk.END, file)
    
#  return MyListBox
#------------------------------------------------------------------------------------------------------------------------------------------------------------------




# Function for printing the
# selected listbox value(s)
def selected_item(listbox):
  global imgPath
  # Traverse the tuple returned by
  # curselection method and print
  # corresponding value(s) in the listbox
#  for i in listbox.curselection():
#    print(listbox.get(i))
  
  imgPath = listbox.get(listbox.curselection())
    




def readImageAsTkinterPhoto(imagePath):
  print(imagePath)
  global imgtk
  image = cv2.imread(folderImagePath + '/' + imagePath)
  
  image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 

  # Convert the Image object into a TkPhoto object
  imageArray = PIL.Image.fromarray(image_rgb)
  imgtk = PIL.ImageTk.PhotoImage(image=imageArray) 
  print (imgtk)
  

mainWindow = tk.Tk()
mainWindow.title('HoneyBee Segmetation Tool GUI') # main window title

# Adjust window size
mainWindow.geometry("640x480")
mainWindow.minsize(640, 480) # minimum window size
mainWindow.maxsize(640, 480) # maximum window size


frame = tk.Frame()
mylist = tk.Listbox()


# Create a scrollbar with vertical orientation.
scrollbarY = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbarX = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

# Link it to the listbox.
mylist = tk.Listbox(frame, yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set)
scrollbarY.config(command=mylist.yview)
scrollbarY.pack(side=tk.RIGHT, fill=tk.Y)
scrollbarX.config(command=mylist.xview)
scrollbarX.pack(side=tk.BOTTOM, fill=tk.X)

mylist.pack()
frame.pack()



# open button
open_button = tk.Button(mainWindow, text='Open a File', command=lambda: RefreshList(mylist))
open_button.pack(expand=True)


#scrollbarY = tk.Scrollbar(mylist)
#scrollbarY.pack(side=tk.LEFT, fill=tk.Y)

#scrollbarX = tk.Scrollbar(mylist)
#scrollbarX.pack(side=tk.LEFT, fill=tk.X)

#mylist = tk.Listbox(mainWindow, yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set, width = 50)


#mainWindow.update()
#print(mylist.size())

#if mylist.size() != 0:
#  for i in mylist.curselection():
#    print(listbox.get(i))

    
#mylist.pack(side=tk.LEFT, fill=tk.BOTH)
#scrollbarY.config(command=mylist.yview)
#scrollbarX.config(command=mylist.xview)













menu = tk.Menu(mainWindow)
mainWindow.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New')
filemenu.add_command(label='Open...')
filemenu.add_separator()
filemenu.add_command(label='Exit', command=mainWindow.quit)
helpmenu = tk.Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About', command= aboutWindow)

button = tk.Button(mainWindow, text='Select image', width=25, command=lambda: [selected_item(mylist), readImageAsTkinterPhoto(imgPath)])
button.pack()




# Put it in the display window
tk.Label(mainWindow, image=imgtK).pack()




button = tk.Button(mainWindow, text='Stop', width=25, command=mainWindow.destroy)
button.pack()










mainWindow.mainloop()

'''
