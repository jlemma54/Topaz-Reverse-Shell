import cv2
import os


def webcam_capture():
    key = cv2.waitKey(1)
    webcam = cv2.VideoCapture(0)

    try:
        check, frame = webcam.read()

        cv2.imshow("Capturing", frame)
        key = cv2.waitKey(1)

        webcam_path = 'C:\\Users\\Public\\Pictures\\saved_img.jpg'
        awebcam_path = 'C:\\Users\\Public\\Pictures\\saved_img-final.jpg'

        cv2.imwrite(filename=webcam_path, img=frame)
        webcam.release()
        img_new = cv2.imread(webcam_path, cv2.IMREAD_GRAYSCALE)
        img_new = cv2.imshow("Captured Image", img_new)
        cv2.waitKey(1650)
        cv2.destroyAllWindows()
        img_ = cv2.imread(webcam_path, cv2.IMREAD_ANYCOLOR)
        gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
        img_ = cv2.resize(gray, (28, 28))
        img_resized = cv2.imwrite(filename=awebcam_path, img=img_)
        print("Image saved!")
        os.remove(awebcam_path)
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()


    except(KeyboardInterrupt):
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()