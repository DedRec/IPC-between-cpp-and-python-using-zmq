# ipc-between-cpp-and-python-using-zmq
## Packages
### Python
- pytorch using GPU >= 1.6 
- cv2 using cudas
- pyzmq
- numpy
- python 3.6 or higher
- zeromq
- cuda 10.2
- cudnn 7.0 or higher

Recommended install python package with conda to avoid conflicts

Recommended install Miniconda as it takes less memory https://docs.anaconda.com/free/miniconda/

Install conda from https://www.anaconda.com/download/success

```bash
conda create -c pytorch -c conda-forge -n ultralight 'pytorch=1.6' torchvision torchaudio cudatoolkit opencv pyzmq zeromq python=3.6.9
```

These packages above take 1.35 GB storage

### Cpp
- opencv with cuda or without
- zmq (zmq.h)

#### install with opencv
```bash
sudo apt-get update
sudo apt-get install libopencv-dev libzmq3-dev
```
#### without opencv
```bash
sudo apt-get update
sudo apt-get install libzmq3-dev
```
## Compile
```bash
g++ -o cpp_sender_script_ubuntu cpp_sender_script_ubuntu.cpp -std=c++11 -lzmq `pkg-config --cflags --libs opencv`
```

## Run
```bash
./cpp_sender_script_ubuntu
```
