# traffic_counter.py

import numpy as np
import socket
import cv2
import os

# setup the script
YOLO_PATH = "COCO"
TCP_PORT = 10000
EXT_CAM = False

# function to count the number of vehicles in a given image
def count_vehicles(camera, net, ln, list_of_vehicles=["bicycle","car","motorbike","bus","truck"]):
	# load our image frame and grab its spatial dimensions
	success, image = camera.read()
	if not success:
		print("Couldn't capture image, ensure a camera is setup")
		return -1
	(H, W) = image.shape[:2]

	# construct a blob from the input image and then perform a forward pass of the YOLO object detector, giving us our bounding boxes and associated probabilities
	blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
	net.setInput(blob)
	layerOutputs = net.forward(ln)

	# loop over each of the layer outputs
	total_vehicle_count = 0
	for output in layerOutputs:
		# loop over each of the detections
		for detection in output:
			# extract the confidence (i.e., probability) of the current object detection
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			# filter out weak predictions by ensuring the detected probability is greater than the minimum probability
			if confidence > 0.5 and LABELS[classID] in list_of_vehicles:
				# update our counted vehicles count
				total_vehicle_count += 1

	return total_vehicle_count

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Created connection socket")

# Bind the socket to the port
server_address = ("localhost", TCP_PORT)
print("Starting up on {} port {}".format(*server_address))

# Listen for incoming connections
sock.bind(server_address)
sock.listen(1)

# load the COCO class labels our YOLO model was trained on
labelsPath = os.path.join(YOLO_PATH, "coco.names")
LABELS = open(labelsPath).read().strip().split("\n")
print("Loaded YOLO Labels")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.join(YOLO_PATH, "yolov3-tiny.weights")
configPath = os.path.join(YOLO_PATH, "yolov3.cfg")
print("Dervied YOLO config paths")

try:
	# load our YOLO object detector trained on COCO dataset (80 classes)
	net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

	# determine only the *output* layer names that we need from YOLO
	ln = net.getLayerNames()
	ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
except:
	net, ln = None, None

# setup camera capturing
camera = cv2.VideoCapture(int(EXT_CAM))
print("Finished Camera Integration")

while True:
	# Wait for a connection
	print("Waiting for a connection to the server")
	connection, client_address = sock.accept()
	try:
		print("Received Connection from", client_address)
		# Receive the data in small chunks and retransmit it
		while True:
			data = connection.recv(4096).decode()
			if data:
				if data == "close server":
					print("Closing the server connection")
					connection.close()
					exit()
				data = str(count_vehicles(camera, net, ln))
				print("Detected {} vehicles".format(data))
				connection.sendall(data.encode("utf-8"))
			else:
				print("No data received from", client_address)
				break
	except Exception as e:
		print(e)
		pass

print("Exited the server")
