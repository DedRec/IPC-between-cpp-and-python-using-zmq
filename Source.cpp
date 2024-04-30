#include <iostream>
#include <opencv2/opencv.hpp>
#include <zmq.h>
#include <vector>

int main() {
    // Initialize ZeroMQ context and connect to the socket
    void* context = zmq_ctx_new();
    void* socket = zmq_socket(context, ZMQ_PULL);
    zmq_connect(socket, "tcp://localhost:5555");

    while (true) {
        // Receive the message containing the image data
        zmq_msg_t message;
        zmq_msg_init(&message);
        zmq_msg_recv(&message, socket, 0);

        // Get the size of the received message
        size_t size = zmq_msg_size(&message);

        // Check if the message is not empty
        if (size > 0) {
            // Create a buffer to hold the received image data
            std::vector<uchar> buffer(size);

            // Copy the message data into the buffer
            memcpy(buffer.data(), zmq_msg_data(&message), size);

            // Decode the image
            cv::Mat image = cv::imdecode(buffer, cv::IMREAD_COLOR);

            // Check if the image is not empty
            if (!image.empty()) {
                // Display the received image
                std::cout << "Image Recieved";
                cv::imshow("Received Image", image);
                cv::waitKey(0);
            }
            else {
                std::cerr << "Failed to decode image." << std::endl;
            }
        }
        else {
            std::cerr << "Empty message received." << std::endl;
        }

        // Close the message
        zmq_msg_close(&message);
    }

    // Close the socket and destroy the ZeroMQ context
    zmq_close(socket);
    zmq_ctx_destroy(context);

    return 0;
}
