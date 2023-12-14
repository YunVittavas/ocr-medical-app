from tkinter import * 
import tkinter as tk
from tkinter import ttk, messagebox
#from tkinter.messagebox import askyesno 

import cv2
from PIL import Image, ImageTk
import os
import pytesseract
from pathlib import Path
import sys
import threading
from ocr_med.json_functions.file_functions import FileFunctions
from ocr_med.filters.image_filters import ImageFilter
import re

pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe' 
class ImageCropper:
    def __init__(self, parent, image):
        self.tkInter = parent
        self.image = image
        self.new_image = image

        self.tkInter.title("Label interface")
        self.tkInter.geometry("575x200") 
        self.style = ttk.Style()
        
        self.input_text = StringVar() 
        self.ocr_text = StringVar()

        self.plot_roi_coordinates: StringVar = []
        self.roi_coordinates: StringVar = []
        self.ocr_value: StringVar = []
        self.image_roi: StringVar = []

        self.get_value_text = False
        self.get_value_ocr = False
        self.exitFlag = False
        self.previous_value_exist = True
        self.title_exist = False
        self.buttonState = None
        
        # Text box and enter button
        self.style.configure('TEntry', foreground='black') 
        self.user_input = ttk.Entry(self.tkInter, textvariable=self.input_text, justify=CENTER, font=("Helvetica", 10, 'bold'))    
        self.user_input.focus_force() 
        self.user_input.grid(row=0, column=0, columnspan=3, pady=10) 

        self.enter = ttk.Button(self.tkInter, text='Enter', command=lambda: self.callback_enter()) 
        self.enter.grid(row=0, column=3, pady=10)

        # Buttons for selecting the type of input
        self.button_template = ttk.Button(self.tkInter, text="Template Name", command=lambda: self.change_state(1))
        self.button_title = ttk.Button(self.tkInter, text="Title", command=lambda: self.change_state(2))
        self.button_key = ttk.Button(self.tkInter, text="Key", command=lambda: self.change_state(3))
        self.button_value = ttk.Button(self.tkInter, text="Value", command=lambda: self.change_state(4))
        self.button_save = ttk.Button(self.tkInter, text="Save", command=lambda: self.save_template_json())
        self.button_template.grid(row=1, column=0)
        self.button_title.grid(row=1, column=1, padx=5, pady=10)
        self.button_key.grid(row=1, column=2, padx=5, pady=10)
        self.button_value.grid(row=1, column=3, padx=5, pady=10)
        self.button_save.grid(row=2, column=3, padx=5, pady=10)

        # Label for status text at the bottom
        self.status_label = tk.Label(self.tkInter, text="", font=("Helvetica", 10), anchor=CENTER, padx=5, pady=10)
        self.status_label.grid(row=2, column=0, columnspan=3, pady=10)

        #zoom and scroll
        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 5
        self.x_offset = 0
        self.y_offset = 0
        
        self.file_functions = FileFunctions()
        self.filter_functions = ImageFilter()
    
    def resize_window(self):
        self.tkInter.update_idletasks()
        width = self.tkInter.winfo_reqwidth()
        height = self.tkInter.winfo_reqheight()
        self.tkInter.geometry(f"{width}x{height}")

    def show_success(self, message):
        self.status_label.config(text=message, fg="green")

    def show_error(self, message):
        self.status_label.config(text=message, fg="red")

    def show_error_message():
        messagebox.showerror("Error", "The title already exists. Please enter a new title.")

    def change_state(self, new_state):
        self.buttonState = new_state
        if new_state == 1:
            self.show_success("Template Name Mode")
        elif new_state == 2:
            self.show_success("Title Mode")
        elif new_state == 3:
            self.show_success("Key Mode")
        elif new_state == 4:
            self.show_success("Value Mode")
        else:
            self.show_success("Press Botton for Label")

    def save_template_json(self):
        print(self.file_functions.base_dict)
        self.file_functions.save_template_json()
        self.show_success(f"Successfully save template at {self.file_functions.create_file_path(self.file_functions.base_dict.get('template_name'), file_type='json')}")

    def callback_enter(self):
        self.get_value_text = True

    def callback_ocr(self):
        self.get_value_ocr = True

    @property
    def get_button_state(self):
        return self.buttonState

    @property
    def get_exit_flag(self):
        return self.exitFlag
    
    @property
    def get_value_text_flag(self):
        return self.get_value_text
    
    @property
    def get_value_ocr_flag(self):
        return self.get_value_ocr
    
    @property
    def get_input_text(self):
        return self.input_text
    
    @property
    def get_ocr_text(self):
        return self.ocr_text
    
    @property
    def get_roi_coordinate(self):
        return self.roi_coordinates
    
    def reset_get_value_text_flag(self):
        self.get_value_text = False

    def reset_get_value_ocr_flag(self):
        self.get_value_ocr = False

    def shape_selection(self, event, x, y, flags, param): 
        # Storing the (x1,y1) coordinates when left mouse button is pressed  
        if event == cv2.EVENT_LBUTTONDOWN: 
            self.roi_coordinates = [(x, y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.roi_coordinates.append((x, y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            cv2.rectangle(image, self.roi_coordinates[0], self.roi_coordinates[1], (0,255,255), 2) 
            cv2.imshow("Imported Image", image) 

    def scroll_zoom(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom *= 1.1
                self.zoom = min(self.zoom, self.max_zoom)
            else:
                self.zoom /= 1.1
                self.zoom = max(self.zoom, self.min_zoom)
            img = self.image.copy()

            new_width = round(img.shape[1] / self.zoom)
            new_height = round(img.shape[0] / self.zoom)
            self.x_offset = round(x - (x / self.zoom))
            self.y_offset = round(y - (y / self.zoom))
            img = img[
                self.y_offset : self.y_offset + new_height,
                self.x_offset : self.x_offset + new_width,]
            self.new_image = cv2.resize(img, (self.image.shape[1], self.image.shape[0]))

        if event == cv2.EVENT_LBUTTONDOWN: 
            self.plot_roi_coordinates = [(x, y)]
            if self.zoom > 1:
                origin_x = round((x / self.zoom) + self.x_offset)
                origin_y = round((y / self.zoom) + self.y_offset)
                self.origin_roi_coordinates = [(origin_x, origin_y)]
            else:
                origin_x = x
                origin_y = y
            self.roi_coordinates = [(origin_x, origin_y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.plot_roi_coordinates.append((x, y))
            if self.zoom > 1:
                origin_x = round((x / self.zoom) + self.x_offset)
                origin_y = round((y / self.zoom) + self.y_offset)
            else:
                origin_x = x
                origin_y = y
            self.roi_coordinates.append((origin_x, origin_y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            # print(self.roi_coordinates)

            cv2.rectangle(self.new_image, self.plot_roi_coordinates[0], self.plot_roi_coordinates[1], (0,255,255), 2) 
            cv2.imshow("Imported Image", self.new_image) 
                
    def crop_image(self):
        # Function to capture ROI based on the current state
        image_copy = self.image.copy()
        cv2.namedWindow("Imported Image", cv2.WINDOW_GUI_EXPANDED) 
        cv2.setMouseCallback("Imported Image", self.scroll_zoom) 
        
        while True: 
        # Display the image and wait for a keypress 
            cv2.imshow("Imported Image", self.new_image) 
            key = cv2.waitKey(1) & 0xFF

            if key==13: # If 'enter' is pressed, apply OCR
                if len(self.roi_coordinates) == 2:
                    self.image_roi = image_copy[self.roi_coordinates[0][1]:self.roi_coordinates[1][1], 
                                        self.roi_coordinates[0][0]:self.roi_coordinates[1][0]]
                    self.image_roi = self.filter_functions.blurry_filter(self.image_roi)
                    self.image_roi = self.filter_functions.salt_and_pepper_filter(self.image_roi)
                    self.image_roi = self.filter_functions.convert_to_grayscale(self.image_roi)
                    # cv2.imshow("ROI", self.image_roi)
                    self.ocr_text = pytesseract.image_to_string(self.image_roi, lang='eng', config='--psm 6') # <---- OCR config needs to be 6 !!!!
                    self.ocr_text = re.sub(r'\n', '', self.ocr_text)
                    print(self.ocr_text)
                    self.callback_ocr()
            
            if key==27: # ESC
                print("Exiting")
                cv2.destroyAllWindows()
                self.exitFlag = True
                sys.exit(0)
            
            if key == ord("c"): # Clear the selection when 'c' is pressed 
                self.new_image = image_copy.copy() 
                
    def main(self):
        while True:
            try:
                if self.get_value_text_flag:
                    if self.get_button_state == 1:
                        self.file_functions.add_template_name(self.get_input_text.get())
                        self.show_success("Add template name by typing")
                        print(self.file_functions.base_dict)
                    elif self.get_button_state == 2:
                        if not self.previous_value_exist:
                            self.show_error("Please add a value in previous key first")
                            print(self.file_functions.base_dict)
                        else: 
                            self.title_exist = True         # First Time only
                            self.file_functions.add_region()
                            self.file_functions.add_title(self.get_input_text.get())
                            print(self.file_functions.base_dict)
                            self.show_success("Successfully add title by typing")
                           
                    elif self.get_button_state == 3:
                        if not self.title_exist:
                            self.show_error("Please add a title before adding a header")
                            print(self.file_functions.base_dict)
                        elif not self.previous_value_exist:
                            self.show_error("Please add a value in previous key first")
                            print(self.file_functions.base_dict)
                        else: 
                            self.previous_value_exist = False
                            self.file_functions.add_key(self.get_input_text.get())
                            self.show_success("Successfully add key by typing")
                            print(self.file_functions.base_dict)
                    elif self.get_button_state == 4:
                        self.show_error("Please crop from the image to get the value")
                    else:   
                        self.show_error("Please select a mode")
                    self.reset_get_value_text_flag()


                elif self.get_value_ocr_flag:
                    if self.get_button_state == 1:
                        self.show_error("Please identify template name by typing")
                        print(self.file_functions.base_dict)
                    elif self.get_button_state == 2:
                        self.show_error("Please identify title name by typing")
                        print(self.file_functions.base_dict)
                    elif self.get_button_state == 3:
                        if not self.title_exist:
                            self.show_error("Please add a title before adding a header")
                            print(self.file_functions.base_dict)
                        elif not self.previous_value_exist:
                            self.show_error("Please add a value in previous key first")
                            print(self.file_functions.base_dict)
                        else:
                            self.previous_value_exist = False
                            self.file_functions.add_key(self.get_ocr_text)
                            self.show_success("Successfully add key by OCR cropping")
                            print(self.file_functions.base_dict)
                    elif self.get_button_state == 4:
                        if self.previous_value_exist:
                            self.show_error("Please add a new key first")
                            print(self.file_functions.base_dict)
                        else:
                            self.previous_value_exist = True
                            self.file_functions.add_value(self.get_roi_coordinate)
                            self.show_success("Successfully add value by OCR cropping")
                            print(self.file_functions.base_dict)
                    else: 
                        self.show_error("Please select a mode")
                    self.reset_get_value_ocr_flag()
                    
            
                if self.get_exit_flag:
                    sys.exit(0)

            except Exception as e:
                self.show_error(f"An error occurred: {e}, Please try again.")
        

if __name__ == "__main__":
    ROOT_PATH :str = Path(__file__).parents[2]
    PDF_LOCATION :str =  os.path.join(ROOT_PATH, "data\pdf")
    JPG_LOCATION :str =  os.path.join(ROOT_PATH, "data\jpg")

    file_name = 'GCA RE'
    input_img = cv2.imread(os.path.join(JPG_LOCATION, file_name+'.jpg')) 
    # input_img = cv2.resize(input_img, (675, 826))
    image = input_img 

    label_functions = ImageCropper(image)
    #file_functions = FileFunctions()

    cv2_thread =threading.Thread(target=label_functions.crop_image)
    cv2_thread.start()
    main_thread = threading.Thread(target=label_functions.main)
    main_thread.start()

    label_functions.resize_window()
    label_functions.tkInter.mainloop()
    
    
    
    
