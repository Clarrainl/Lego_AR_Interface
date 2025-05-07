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

This project is an interactive augmented tabletop for building LEGO models. Users place real LEGO bricks on a scanning zone, and the system uses computer vision to detect the pieces and guide the user through the construction of one of several predefined models using a visual interface projected on the table.

### System Architecture

**Backend (Python)**

* *MediaPipe*: Detects finger landmarks, especially the tips.
* *YOLOv8*: Detects LEGO bricks during the SCAN state.
* *Finite State Machine (FSM)*: Manages transitions and interaction logic.
* *UDP Communication*: Sends state, pointer, and piece position updates to Grasshopper in real time.

**Frontend (Grasshopper + Rhino)**

* Receives and decodes messages from Python.
* Displays UI components including buttons and step guidance.
* Projects the interface using a top-down projector.

### Key Scripts

* `lego_main.py`: Handles camera input, hand detection, FSM updates, and YOLOv8 execution during scanning.
* `lego_fsm_controller.py`: Defines FSM logic, including all transitions and input handling.

### FSM States

**🟢 START**

* UI displays “Put your legos here”.
* SCAN button is highlighted.
* Interaction is dwell-based: holding finger over button for >0.4s triggers transition.

**🔍 SCAN**

* Captures camera input and applies YOLOv8.
* Calculates center of each bounding box and maps it to projected coordinates.
* Sends PIECES\:x,y data to Grasshopper via UDP.
* Transitions to CHOOSE after detection.

**🧩 CHOOSE**

* Projects four model options (SET 1–4).
* User selects set by hovering over buttons.
* Transitions to ASSEMBLY with chosen set.

**🛠 ASSEMBLY**

* Displays build step image.
* Highlights required bricks.
* Sends STEP\:n and STATE\:ASSEMBLY over UDP.
* NEXT and BACK navigate steps.
* Final NEXT → FINISH.

**✅ FINISH**

* Displays success message.
* RETRY button resets process.

### Grasshopper Communication

Python backend sends real-time messages to Grasshopper UI:

* FSM state: `STATE:START`, `STATE:SCAN`, etc.
* Finger pointer: `POINTER:x,y`
* Build step: `STEP:n`
* Piece coordinates: `PIECES:x1,y1|x2,y2|...`

Grasshopper updates the projection dynamically based on received data.

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
2. Project the Rhino window onto a table surface using a projector, making sure it is in full-screen mode to display the interface clearly.
3. Make sure the interface (Grasshopper UI) is properly aligned on the surface.
4. Run the script `lego_main.py` on your computer. A simplified UI window will open showing real-time finger tracking.
5. Press **START** using your finger over the projected interface. A 5-second countdown will begin so you can remove your hand from the table.
6. The system scans the LEGO pieces on the surface using YOLO and proposes possible models to build.
7. Select a model. The script sends the center point of each required piece via UDP to Grasshopper, which highlights them with colored circles.
8. Use **NEXT** and **BACK** to navigate through assembly steps.
9. Once the model is complete, press **RETRY** to start again.

![lego\_15](https://github.com/user-attachments/assets/20df341b-7ea8-410d-a554-f27cabe14bd0)

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
