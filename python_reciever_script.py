import cv2
import numpy as np
import zmq
import argparse
import os
import sys

from vision.ssd.config.fd_config import define_img_size

parser = argparse.ArgumentParser(
    description='detect_imgs')

parser.add_argument('--net_type', default="slim", type=str,
                    help='The network architecture ,optional: RFB (higher precision) or slim (faster)')
parser.add_argument('--input_size', default=320, type=int,
                    help='define network input size,default optional value 128/160/320/480/640/1280')
parser.add_argument('--threshold', default=0.8, type=float,
                    help='score threshold')
parser.add_argument('--candidate_size', default=1500, type=int,
                    help='nms candidate size')
parser.add_argument('--path', default="imgs", type=str,
                    help='imgs dir')
parser.add_argument('--test_device', default="cpu", type=str,
                    help='cuda:0 or cpu')
args = parser.parse_args()
define_img_size(args.input_size)  # must put define_img_size() before 'import create_mb_tiny_fd, create_mb_tiny_fd_predictor'

from vision.ssd.mb_tiny_fd import create_mb_tiny_fd, create_mb_tiny_fd_predictor
from vision.ssd.mb_tiny_RFB_fd import create_Mb_Tiny_RFB_fd, create_Mb_Tiny_RFB_fd_predictor

result_path = "./detect_imgs_results"
label_path = "./models/voc-model-labels.txt"
test_device = args.test_device

class_names = [name.strip() for name in open(label_path).readlines()]
if args.net_type == 'slim':
    model_path = "models/pretrained/version-slim-320.pth"
    # model_path = "models/pretrained/version-slim-640.pth"
    net = create_mb_tiny_fd(len(class_names), is_test=True, device=test_device)
    predictor = create_mb_tiny_fd_predictor(net, candidate_size=args.candidate_size, device=test_device)
elif args.net_type == 'RFB':
    model_path = "models/pretrained/version-RFB-320.pth"
    # model_path = "models/pretrained/version-RFB-640.pth"
    net = create_Mb_Tiny_RFB_fd(len(class_names), is_test=True, device=test_device)
    predictor = create_Mb_Tiny_RFB_fd_predictor(net, candidate_size=args.candidate_size, device=test_device)
else:
    print("The net type is wrong!")
    sys.exit(1)
net.load(model_path)


# Initialize ZeroMQ context and connect to the socket
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5555")

name = 0
# Function to process the received image
def process_image(orig_image, result_path):
    global name 
    if orig_image is not None:
        print("----------Image received--------------")
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        sum = 0
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        boxes, labels, probs = predictor.predict(image, args.candidate_size / 2, args.threshold)
        sum += boxes.size(0)
        for i in range(boxes.size(0)):
            box = boxes[i, :]
            cv2.rectangle(orig_image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
            label = f"{probs[i]:.2f}"
            cv2.putText(orig_image, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(orig_image, str(boxes.size(0)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Save image with incremented filename
        output_filename = f"{str(name)}.png"  # Naming starting from 0, incrementing by 1
        cv2.imwrite(os.path.join(result_path, output_filename), orig_image)
        name += 1
        print(f"Found {len(probs)} faces. The output image is {os.path.join(result_path, output_filename)}")

while True:
    # Receive the message containing the image data
    message = socket.recv()

    # Check if the message is not empty
    if message:
        # Decode the message into a NumPy array
        buffer = np.frombuffer(message, dtype=np.uint8)

        # Check if the buffer is not empty
        if buffer.size > 0:
            # Decode the image
            image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

            # Check if the image is not empty
            if image is not None:
                # Decode the image
                image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

                if image is not None:
                    sum = 0
                    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    boxes, labels, probs = predictor.predict(image, args.candidate_size / 2, args.threshold)
                    sum += boxes.size(0)
                    for i in range(boxes.size(0)):
                        box = boxes[i, :]
                        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
                        label = f"{probs[i]:.2f}"
                        cv2.putText(image, label, (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(image, str(boxes.size(0)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Process the received image
                # process_image(image, result_path)

                # Display the received image
                cv2.imshow("py_Received Image", image)
                cv2.waitKey(1)
                #cv2.destroyAllWindows()
            else:
                print("Failed to decode image.")
        else:
            print("Empty buffer received.")
    else:
        print("Empty message received.")
