#include <iostream>
#include <opencv2/opencv.hpp>
#include <zmq.h>

int main() {
    // Initialize ZeroMQ context and create a PUSH socket
    void* context = zmq_ctx_new();
    void* socket = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(socket, "tcp://*:5555");

    // Open the video file
    cv::VideoCapture video("D:/Test/Test.mp4"); // Specify the path to your video file
    if (!video.isOpened()) {
        std::cerr << "Failed to open video file." << std::endl;
        zmq_close(socket);
        zmq_ctx_destroy(context);
        return 1;
    }

    // Main loop to read frames and send them as images
    cv::Mat frame;
    while (true) {
        // Read a frame from the video
        video >> frame;
        if (frame.empty()) // Check if end of video
            break;

        // Encode the frame as a PNG image
        std::vector<uchar> buffer;
        cv::imencode(".png", frame, buffer);

        // Create a ZeroMQ message and copy the image data into it
        zmq_msg_t message;
        zmq_msg_init_size(&message, buffer.size());
        memcpy(zmq_msg_data(&message), buffer.data(), buffer.size());

        // Send the message
        int sent = zmq_msg_send(&message, socket, 0);
        if (sent == -1) {
            std::cerr << "Failed to send message: " << zmq_strerror(errno) << std::endl;
            zmq_msg_close(&message);
            zmq_close(socket);
            zmq_ctx_destroy(context);
            return 1;
        }

        // Close the message
        zmq_msg_close(&message);

        // Optional: Add a delay to control the frame rate
        // You can adjust the delay according to your desired frame rate
        // e.g., for 30 FPS, use a delay of approximately 33 milliseconds
        // Adjust this delay according to the actual frame rate of your video
        // Adjust the delay if needed to match the desired frame rate
        // Note: This delay is optional and can be removed if not needed
        // cv::waitKey(33); // 33 milliseconds delay for approximately 30 FPS
    }

    // Close the video file, socket, and ZeroMQ context
    video.release();
    zmq_close(socket);
    zmq_ctx_destroy(context);

    std::cout << "Video frames sent." << std::endl;

    return 0;
}
