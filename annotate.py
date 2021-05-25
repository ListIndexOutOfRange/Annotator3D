import cv2
import pickle
import argparse
from copy import deepcopy




class Annotator:

    """ This class allows one to load, display an image and draw lines onto it. 
    
    Usage:
        - Left click on the beginning of the line
        - Hold the left click until the desired line's end is reached.
        - Release left click to finish line.
        - Press r to reset annotations.  
    """

    def __init__(self, image_path=None, window_name="image", window_size=(1280, 720)):
        """ When the left click is holded, we must plot the current line only, that is the line 
        corresponding to the last mouse position. In order to do that we must keep a copy of our
        image (a cache).
        Following the same idea, the original attribute allows one to reset the annotations.   
        """
        self.image    = cv2.imread(image_path)
        self.cache    = deepcopy(self.image)
        self.original = deepcopy(self.image)
        self.window   = window_name 
        cv2.namedWindow(self.window, cv2.WINDOW_NORMAL) 
        cv2.resizeWindow(self.window, *window_size)
        cv2.setMouseCallback(self.window, self.draw_line)
        self.drawing = False
        self.start_x, self.start_y = -1, -1
        self.lines = []
        

    def draw_line(self, event, x, y, flags, param):
        """ Callback function to be called by open-cv every time an event is detected.

        Args:
            event (int): An cv2 event descriptor, can be everything mouse related.
            x (float): Current x position of the mouse. 
            y (float): Current y position of the mouse.
            flags (optional): Handled by cv2. Flags related to the current event
            param (Any): Additional parameters needed by the callback functions can be passed
                         through this argument.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_x, self.start_y = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            self.image = deepcopy(self.cache)
            if self.drawing == True:
                cv2.line(self.image, (self.start_x, self.start_y),(x, y), (0, 0, 255), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.image, (self.start_x, self.start_y), (x, y), (0, 0, 255), 2)
            self.cache = deepcopy(self.image)
            self.lines.append((self.start_x, self.start_y, x, y))


    def run(self, save_annotated_image=False, save_annotations=False):
        """ Loop until Esc is pressed or window is closed by user. 
            Pressing r will reset the annotations.
            Eventually save the annotated image as a .jpg file and/or the annotations
            as a pickled file.  
        """
        print("Click and hold to draw lines.")
        print("Press r to reset annotations")
        while cv2.getWindowProperty(self.window, cv2.WND_PROP_VISIBLE) >= 1:
            cv2.imshow(self.window, self.image)
            keyCode = cv2.waitKey(1) & 0xFF
            if keyCode == ord("r"):
                self.image = deepcopy(self.original)
                self.cache = deepcopy(self.original)
            if keyCode == 27:
                break
        cv2.destroyAllWindows()
        if save_annotated_image:
            cv2.imwrite("annotated_image.jpg", self.image)
        if save_annotations:
            with open('annotations.pkl', 'wb') as fp:
                pickle.dump(self.lines, fp)




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="path to the distorted image")
    parser.add_argument("--save", help="save annotated image and annotations", action="store_true")
    return parser.parse_args()


def main():
    args      = parse_args()
    annotator = Annotator(image_path=args.image_path, window_name="distorted image")
    annotator.run(save_annotated_image=args.save, save_annotations=args.save)




if __name__ == '__main__': main()
