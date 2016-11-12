from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np 
import argparse
import imutils
import cv2
from skimage.filter import threshold_adaptive
from itertools import product

# construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "path to the input image")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
image = imutils.resize(image, height = 900)

# convert image to gray
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# threshold
threshold_matrix = threshold_adaptive(gray, 251, offset = 10)
thresh = threshold_matrix.astype("uint8") * 255

# find black contours
(_, contours, _) = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

distances = []

for contour in contours: 
	minimum_contour_size = 10
	max_values = np.amax(contour, axis = 0).flatten().tolist()
	x_max, y_max = max_values
	min_values = np.amin(contour, axis = 0).flatten().tolist()
	x_min, y_min = min_values 

	dx = x_max - x_min
	dy = y_max - y_min
	if dx > minimum_contour_size and dy > minimum_contour_size:
		distances.append([dx, dy])

# import code; code.interact(local=dict(globals(), **locals()))

# get the most frequent distances from all contours
x_mode, y_mode = max(distances, key=distances.count)
deviation = 0.4
kernel_radius = 1

common_contours = []

for contour in contours: 
	max_values = np.amax(contour, axis = 0).flatten().tolist()
	x_max, y_max = max_values
	min_values = np.amin(contour, axis = 0).flatten().tolist()
	x_min, y_min = min_values 

	dx = x_max - x_min
	dy = y_max - y_min

	# check if black or white
	if int((1-deviation)*x_mode) < dx < int((1+deviation)*x_mode):
		# common_contours.append(contour)
		# check if the inside of the contour is white or black
		x_center = int(x_min + 0.5*dx)
		y_center = int(y_min + 0.5*dy)

		kernel_x_min = x_center - kernel_radius
		kernel_x_max = x_center + kernel_radius
		kernel_y_min = y_center - kernel_radius
		kernel_y_max = y_center + kernel_radius

		# get the cartesian product of the kernel boundaries
		kernel_coordinates = list(product([kernel_y_min, kernel_y_max], [kernel_x_min, kernel_x_max]))

		# get the color dimensions 
		average_color = 0 

		for coordinate in kernel_coordinates:
			average_color += gray[coordinate]

		average_color /= len(kernel_coordinates)

		common_contours.append([y_max, x_max, average_color])


		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(image, str(average_color), (x_center, y_center), font, 0.6, (0, 0, 255), 2)

# common_contours = np.array(common_contours)
# common_contours = common_contours[common_contours[:,0].argsort()]
common_contours.sort()

# import code; code.interact(local=dict(globals(), **locals()))


rows = []
row_buffer = []

# split by y value
for i in range(len(common_contours)):
	if abs(common_contours[i][0] - common_contours[i-1][0]) < 10:
		row_buffer.append(common_contours[i])
	else:
		# add the first element in the row to the buffer
		# save the buffer to the big array and reset the buffer 
		row_buffer.append(common_contours[i-len(row_buffer)-1])
		rows.append(row_buffer)
		row_buffer = []

# and add the last row	
row_buffer.append(common_contours[i-len(row_buffer)])
rows.append(row_buffer)

# delete the first empty row
# and duplicate first element
del rows[0]

questions = []

for row in rows:
	row.sort(key = lambda coords: coords[1])

	box_distance = row[1][1] - row[0][1]
	deviation = 1.4

	# splits when the distance between two boxes surpasses
	# the box distance times deviation
	# assumes there is always one and only one split
	for i in range(len(row)-1):
		if row[i+1][1] - row[i][1] > box_distance * deviation:
			questions.append(row[:i])
			questions.append(row[-i:])

for question in questions:
	darkest_color = min(question, key = lambda q: q[2])
	lightest_color = max(question, key = lambda q: q[2])
	blank_threshold = 50
	if lightest_color[2] - darkest_color[2] < blank_threshold:
		index = "question blank"
	else: 
		index = question.index(darkest_color)
	print("----------")
	print(question)
	print(index)
	print("----------")
# handle end of list, empty sets
# import code; code.interact(local=dict(globals(), **locals()))


cv2.drawContours(image, common_contours,-2,(0,255,0),3)
cv2.imshow("th", image)
cv2.waitKey(0)