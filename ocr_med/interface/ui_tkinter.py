import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import threading
import numpy as np
import cv2
import os
import ctypes

from ocr_med.roi_label import crop_with_tkinter as cwt
from ocr_med.json_functions.file_functions import FileFunctions
from ocr_med.ocr import run_ocr

def initiate_ocr():
    image, folder_path, output_path, template_path, file_type_var, page_number = call_all_value_and_change_to_image()
    file_name = os.path.split(folder_path)[-1]
    
    # Check if the folder path and Excel name are provided
    if not folder_path or not output_path:
        show_error("Please enter both folder path and Excel file name.")
    else:
        try:
            # Add Yun OCR Code here
            result_ocr = run_ocr(image, template_path, file_name)
            FileFunctions.export_json_csv(result_ocr, output_path)
            #print(f"OCR initiated for Folder: {folder_path}, Excel File: {excel_name}")
            success_message = f"OCR is finished and saved at {output_path}" # Replace output_path with the actual path
            show_success(success_message)

        except Exception as e:
            show_error(f"Error during OCR process: {str(e)}")

def label_function():
    image, folder_path, output_path, template_path, file_type_var, page_number = call_all_value_and_change_to_image()
    second_window = tk.Toplevel(window)
    cropper = cwt.ImageCropper(second_window, image)

    # Add Jean label(or what ever u like to call) function here, and if want to change button name find this line
    cv2_thread =threading.Thread(target=cropper.crop_image)
    cv2_thread.start()
    main_thread = threading.Thread(target=cropper.main)
    main_thread.start()
    
    cropper.resize_window()
    cropper.tkInter.mainloop()

#This is the function for browse button in create template window 
def browse_template_path(template_entry):
    template_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    template_entry.delete(0, tk.END)
    template_entry.insert(0, template_path)
    update_template_label(template_path)

def browse_folder_path():
    folder_path = filedialog.askopenfilename(filetypes=[("Folder", "")])
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)
    update_folder_label(folder_path)

def browse_excel_path():
    output_path = filedialog.askdirectory()
    excel_name_entry.delete(0, tk.END)
    excel_name_entry.insert(0, output_path)
    update_excel_label(output_path)
    #return output_path

def select_file_type():
    return file_type_var.get()

def display_file(file_path, page_number):
    try:
        file_type = select_file_type()

        if file_type == "Image":
            # For image files
            image = Image.open(file_path)
        elif file_type == "PDF":
            # For PDF files
            pdf_images = convert_pdf_to_images(file_path)
            if pdf_images:
                page_index = int(page_number) - 1  # Convert to zero-based index
                if 0 <= page_index < len(pdf_images):
                    image = pdf_images[page_index]
                else:
                    raise Exception("Invalid page number.")
            else:
                raise Exception("Error converting PDF to images.")
        else:
            raise Exception("Unsupported file type.")

        # Check the current orientation (landscape or portrait)
        orientation = current_orientation

        width = 420
        height = int(display_canvas_width * 1.414)  # A4 ratio

        # Display the image with the current orientation
        if orientation == "landscape":
            image = image.resize((height, width), Image.BILINEAR)
        elif orientation == "portrait":
            image = image.resize((width, height), Image.BILINEAR)

        img = ImageTk.PhotoImage(image)
        display_canvas.config(width=image.width, height=image.height)
        display_canvas.create_image(0, 0, anchor=tk.NW, image=img)
        display_canvas.image = img
        error_label.config(text="")
        show_success("File displayed successfully.")
    except Exception as e:
        show_error(f"Error displaying file: {str(e)}")

def convert_pdf_to_images(pdf_path):
    if not pdf_path:
        show_error("Please choose a file first.")
        return  None
    else:
        try:
            pdf_images = convert_from_path(pdf_path)
            return pdf_images
        except Exception as e:
            show_error(f"Error converting PDF to images: {str(e)}, Forget to change File type?")
            return None

def show_success(message):
    error_label.config(text=message, fg="green", font=("Helvetica", 9))

def show_error(message):
    error_label.config(text=message, fg="red", font=("Helvetica", 9))

def update_folder_label(folder_path):
    last_two_dirs = "/".join(folder_path.split("/")[-2:])
    folder_label.config(text=f"Selected: {last_two_dirs}")
    
def update_excel_label(output_path):
    last_two_dirs = "/".join(output_path.split("/")[-2:])
    excel_label.config(text=f"Selected: {last_two_dirs}")

def update_template_label(template_path):
    last_two_dirs = "/".join(template_path.split("/")[-2:])
    template_location_label.config(text=f"Selected: {last_two_dirs}")

def display_selected_file():
    try:
        # Get the selected file path and page number
        selected_file_path, page_number = get_selected_file_info()

        # Check if a file path is provided
        if selected_file_path:
            # Display the selected file with the specified page number
            display_file(selected_file_path, page_number)
        else:
            show_error("No file path selected.")
    except Exception as e:
        show_error(f"Error displaying selected file: {str(e)}")

def get_selected_file_info():
    selected_file_path = folder_path_entry.get()
    page_number = page_number_entry.get()
    return selected_file_path, page_number

current_orientation = "portrait"

def toggle_orientation():
    global current_orientation
    # Toggle between portrait and landscape
    current_orientation = "landscape" if current_orientation == "portrait" else "portrait"
    # Update the display_file function to consider the current orientation when displaying the file
    display_file(folder_path_entry.get(), int(page_number_entry.get()))

def call_all_value_and_change_to_image():
    folder_path = folder_path_entry.get()   #return type of file_path is string
    output_path = excel_name_entry.get()    #return type of output_path is string
    file_type_var = select_file_type()      #return type of file_type_var is string ("Image" or "PDF")
    template_path = template_path_entry.get() #return type of template_path is string
    # For multiple pages pdf
    page_number = page_number_entry.get()

    if file_type_var == "Image":
        # For image files
        image = cv2.imread(folder_path)
    elif file_type_var == "PDF":
        # For PDF files
        pdf_images = convert_pdf_to_images(folder_path)
        page_index = int(page_number) - 1  # Convert to zero-based index
        if 0 <= page_index < len(pdf_images):
            image = np.array(pdf_images[page_index])
    return image, folder_path, output_path, template_path, file_type_var, page_number

def on_configure(event):
    # Adjust font and widget sizes when the window is resized
    new_width = event.width
    new_height = event.height

    # Calculate the center position based on the new window dimensions
    center_x = new_width // 2
    center_y = new_height // 2

    # Move the main frame to the center
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    main_frame.place(x=center_x, y=center_y, anchor="center")

def resize_window():
    window.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    window.geometry(f"{width}x{height}")
    
# Create the main window with higher DPI
window = tk.Tk()
window.title("OCR Application")
window.geometry("960x540")  # Set the initial window size

# Set DPI (dots per inch) to improve appearance
window.tk.call('tk', 'scaling', 2.2)

# Define modern color scheme
background_color = "#F5F5F5"
accent_color = "#006401"
text_color = "#2c3e50"

# Configure window background color
window.configure(bg=background_color)

# Create a style for the main frame
style = ttk.Style()
style.configure("main.TFrame", background=background_color)

# Create and pack a main frame
main_frame = ttk.Frame(window, padding="20", style="main.TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configure row and column weights for expansion
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create and pack a main frame
main_frame = ttk.Frame(window, padding="20")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create and pack left frame for input elements
left_frame = ttk.Frame(main_frame, padding="10", style="left.TFrame")
left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Apply a separator between frames
ttk.Separator(main_frame, orient=tk.VERTICAL).grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)

# Create and pack right frame for image display
right_frame = ttk.Frame(main_frame, padding="10", style="right.TFrame")
right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

# Apply a modern style to the left frame
style = ttk.Style()
style.configure("left.TFrame", background=background_color)

style = ttk.Style()
style.configure("right.TFrame", background=background_color)

# Create and pack widgets with modern styling for the left frame
title_font = ("Helvetica", 16, "bold")
button_font = ("Helvetica", 10)
label_font = ("Helvetica", 12)

# Right Frame Configuration
datapreview_label = tk.Label(right_frame, text="Data Preview", font=button_font, bg=background_color, fg=text_color, width=20, anchor=tk.CENTER)
datapreview_label.grid(row=0, column=0, pady=10)

display_canvas_width = 400
display_canvas_height = display_canvas_width * 1.414  # A4 ratio

display_canvas = tk.Canvas(right_frame, width=display_canvas_width, height=display_canvas_height, bg=background_color, highlightthickness=0, relief="ridge")
display_canvas.grid(row=1, column=0, pady=10)

orientation_button = tk.Button(right_frame, text="Toggle Orientation", command=toggle_orientation, bg=accent_color, fg="white", font=button_font, width=20)
orientation_button.grid(row=2, column=0, pady=5)

# Left Frame Configuration
title_label = tk.Label(left_frame, text="OCR Application", font=title_font, bg=background_color, fg=text_color)
title_label.grid(row=0, column=0, pady=10, sticky=tk.W)

# Row 1
folder_path_label = tk.Label(left_frame, text="1. Select Your File for OCR:", font=label_font, bg=background_color, fg=text_color)
folder_path_label.grid(row=1, column=0, pady=10, sticky=tk.W)

folder_path_entry = tk.Entry(left_frame, width=30, font=label_font)
folder_path_entry.grid(row=2, column=0, pady=5, sticky=tk.W)

browse_button = tk.Button(left_frame, text="Browse", command=browse_folder_path, bg=accent_color, fg="white", font=button_font)
browse_button.grid(row=3, column=0, pady=5, sticky=tk.W)

folder_label = tk.Label(left_frame, text="Selected File:", font=label_font, bg=background_color, fg=text_color)
folder_label.grid(row=2, column=1, pady=5, sticky=tk.W)

# Row 4
file_type_label = tk.Label(left_frame, text="2. Select File Type (Image or PDF):", font=label_font, bg=background_color, fg=text_color)
file_type_label.grid(row=4, column=0, pady=10, sticky=tk.W)

file_type_label = tk.Label(left_frame, text="for PDF select pages below (default is page 1):", font=label_font, bg=background_color, fg=text_color)
file_type_label.grid(row=4, column=1, pady=10, sticky=tk.W)

file_type_var = tk.StringVar()
file_type_var.set("PDF")

file_type_menu = tk.OptionMenu(left_frame, file_type_var, "Image", "PDF")
file_type_menu.config(bg=accent_color, fg="white", font=button_font)
file_type_menu.grid(row=5, column=0, pady=5, sticky=tk.W)


page_number_entry = tk.Entry(left_frame, width=5, font=label_font, justify=tk.CENTER)
page_number_entry.grid(row=5, column=1, pady=5, sticky=tk.W)
page_number_entry.insert(0, "1")  # Set default value to 1

# Row 6
excel_name_label = tk.Label(left_frame, text="3. Select Folder for Saving Result:", font=label_font, bg=background_color, fg=text_color)
excel_name_label.grid(row=6, column=0, pady=10, sticky=tk.W)

excel_name_entry = tk.Entry(left_frame, width=30, font=label_font)
excel_name_entry.insert(0, "choose_a_path")  # for sean default change here
excel_name_entry.grid(row=7, column=0, pady=5, sticky=tk.W)

browse_excel_button = tk.Button(left_frame, text="Browse", command=browse_excel_path, bg=accent_color, fg="white", font=button_font)
browse_excel_button.grid(row=8, column=0, pady=5, sticky=tk.W)

excel_label = tk.Label(left_frame, text="Selected Folder:", font=label_font, bg=background_color, fg=text_color)
excel_label.grid(row=7, column=1, pady=5, sticky=tk.W)

# Row 9
template_label = tk.Label(left_frame, text="4. Select Template or Create Template", font=label_font, bg=background_color, fg=text_color)
template_label.grid(row=9, column=0, pady=10, sticky=tk.W)

template_path_entry = tk.Entry(left_frame, width=30, font=label_font)
template_path_entry.insert(0, "choose_a_path")  # for sean default change here
template_path_entry.grid(row=10, column=0, pady=5, sticky=tk.W)

browse_template_button = tk.Button(left_frame, text="Browse Existed Template", command=lambda: browse_template_path(template_path_entry), bg=accent_color, fg="white", font=button_font)
browse_template_button.grid(row=11, column=0, pady=5, sticky=tk.W)

template_location_label = tk.Label(left_frame, text="Selected Template:", font=label_font, bg=background_color, fg=text_color)
template_location_label.grid(row=10, column=1, pady=5, sticky=tk.W)

create_template_button = tk.Button(left_frame, text="Click here to create New Template", command=label_function, bg=accent_color, fg="white", font=button_font)
create_template_button.grid(row=11, column=1, pady=5, sticky=tk.W)

# Row 11
# Menu Label
menu_label = tk.Label(left_frame, text="Menu", font=("Helvetica", 12, "bold"), bg=background_color, fg=text_color)
menu_label.grid(row=12, column=0, pady=10, sticky=tk.W)

# Row 12
preview_file_button = tk.Button(left_frame, text="Preview Selected File", command=display_selected_file, bg=accent_color, fg="white", font=button_font)
preview_file_button.grid(row=13, column=0, pady=5, sticky=tk.W)

initiate_ocr_button = tk.Button(left_frame, text="Initiate OCR", command=initiate_ocr, bg=accent_color, fg="white", font=button_font)
initiate_ocr_button.grid(row=13, column=1, pady=5, sticky=tk.W)

# Row 13
# Error label
error_label = tk.Label(left_frame, text="Create by Biomedical Engineering, Mahidol University", font=label_font, bg=background_color, fg=text_color)
error_label.grid(row=14, column=0, columnspan=2, pady=5, sticky=tk.W)

ctypes.windll.shcore.SetProcessDpiAwareness(True)

resize_window()
# Start the Tkinter event loop
window.mainloop()
