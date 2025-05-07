# Lego\_AR\_Interface

## Index

* [Overview](#overview)
* [Getting Started](#getting-started)
* [Demo](#demo)
* [Authors](#authors)
* [References](#references)
* [Credits](#credits)

## MRAC24-25: Hardware III - Lego\_AR\_Interface

This project explores an augmented reality interface to guide the assembly of LEGO sets through hand gesture interaction. The user interacts via a UI projected in Rhino using Grasshopper, and their hand movements are detected by a webcam. A finite state machine (FSM) controls the process flow and communicates with Grasshopper using UDP.

## Overview

Lego\_AR\_Interface combines computer vision, a custom FSM, and an object detection model (YOLO) to visually guide LEGO assembly. Inspired by AR-assisted workflows, the system runs in Rhino + Grasshopper and uses a webcam to track the user's hand. Actions such as "scan", "next step", or "retry" are triggered in real time based on hand gestures.

### System States:

* **START**: User places LEGO pieces.
* **SCAN**: Pieces are detected using YOLO.
* **CHOOSE**: User selects a proposed model to build.
* **ASSEMBLY**: Step-by-step assembly guidance.
* **FINISH**: Completion of the model.

## Getting Started

### Prerequisites

* Windows with Rhino 8
* Python 3.9 (specifically)
* OpenCV-compatible webcam

### Create virtual environment

We recommend using a Python 3.9 virtual environment. For example:

```cmd
py -3.9 -m venv .lego_ar_interface
.\.lego_ar_interface\Scripts\activate
```

### Dependencies

Install all dependencies from `requirements.txt`:

```cmd
pip install -r requirements.txt
```

Main libraries used:

* `mediapipe` – hand detection
* `opencv-python` – video capture and UI
* `ultralytics` – YOLOv8 model
* `torch`, `torchvision` – model inference
* `numpy`, `pandas`, `matplotlib`, `seaborn` – data processing

### Structure

* `lego_main.py`: Main script for video input, hand detection, and FSM control.
* `lego_fsm_controller.py`: FSM logic that manages all UI states and transitions.
* `FSM_Lego final.gh`: Grasshopper definition that receives UDP data and renders the UI.

### UDP Communication

Communication happens via sockets:

* IP: `127.0.0.1`
* Port: `5005`
* Messages include: `state`, `step`, `selected_set`, `pos_x`, `pos_y`

## Demo

1. Open **Rhino 8** and **Grasshopper**.
2. Project the Rhino window onto a table surface using a projector.
3. Make sure the interface (Grasshopper UI) is properly aligned on the surface.
4. Run the script `lego_main.py` on your computer. A simplified UI window will open showing real-time finger tracking.
5. Press **START** using your finger over the projected interface. A 5-second countdown will begin so you can remove your hand from the table.
6. The system scans the LEGO pieces on the surface using YOLO and proposes possible models to build.
7. Select a model. The script sends the center point of each required piece via UDP to Grasshopper, which highlights them with colored circles.
8. Use **NEXT** and **BACK** to navigate through assembly steps.
9. Once the model is complete, press **RETRY** to start again.

![lego_15](https://github.com/user-attachments/assets/20df341b-7ea8-410d-a554-f27cabe14bd0)

## Authors

* [Mau Weber](https://github.com/Mauweberla)
* [Javi Albo](https://github.com/j-albo)
* [Eli Frias](https://github.com/elicolds)
* [Charlie Larraín](https://github.com/Clarrainl)

## References

* [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
* [Ultralytics YOLO](https://docs.ultralytics.com/)
* [OpenCV](https://opencv.org/)

## Credits

* Rhino + Grasshopper interface design – \[Your Name / Collaborator]
* FSM structure inspired by UX in AR-assisted assembly workflows
* ChatGPT (OpenAI)

## Faculty

* [Huanyu Li](https://www.linkedin.com/in/huanyu-li-457590268/)
* [Sameer Kishore](https://linkedin.com/in/sameer-kishore-635624bb/)
* [Pit Siebenaler](https://github.com/pitsieben)

#### Acknowledgements

* GitHub template: [Marita Georganta](https://www.linkedin.com/in/marita-georganta/)
* MRAC-IAAC GitHub Structure: [Huanyu Li](https://www.linkedin.com/in/huanyu-li-457590268/)
