# REDM GoldrushRP Minigame Automation

The minigame is similar to a popular arcade game called "pop the lock". This project aimed to automate it within the game with computer vision and some backseat bus math. 

This project started purely based on a "I can probably automate this" thought. Along with my hatred for these lab rat tasks for reward mechanics that are lazy solutions to underlying problems.

If you're a developer of the server and want to find how to make this script redundant, changing the element colours or number font will break it. However, this is a lazy temp fix and you should really just not care, it would be easy to detect those who are abusing any automation with basic math. 

After 10 hours of testing. The success rate was 99.7% 

![Hello](https://i.imgur.com/i4NPnbv.png)

## Basic explanation of how it works
It locates a window with the keyword "Redm". Captures and processes the frames with dynamic cropping and colour thresholding. 

Further on it uses contour segmentation to locate the most central contour which is always the number, which it then uses to template match from predefined image template arrays stored in `number_data.pkl`. This is essentially a very fast and lightweight OCR solution.

It then uses some rather basic logic to determine when it should send the number keystroke. It simply counts the total contours in the previous frame, if the current frame has less contours, it sends the keystroke. This logic worked much better than other solutions I tried like a K-NN model or pixel density analysis. 

A space bar keystroke is sent every 5 seconds. No fancy logic for this, its just a macro. 

Lastly there is some very fancy GUI scripting with tkinter that gives us a very nice stop/start button. 

## Considerations
This was tested on a screen size of 5120x1440, further tested at smaller window sizes like 2540x1440 and 1920x1080. I have not tested this in full screen or lesser resolutions. If you are playing on anything smaller, I recommend getting a job and upgrading to the modern era. 

For best results, aim your camera in game towards the floor. This is based of the white pixel thresholding, if you aim your camera into the sky, it with definitely not operate well. 


## Support
I will not be offering any support if you encounter any issues. If googling can not help you, then you are doomed. 

Updates may happen if I still play on the server and care enough. This was just a project to keep me entertained. 


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```python
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
