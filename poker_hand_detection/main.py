from ultralytics import YOLO
import cv2
import cvzone
import math
from hand_detector_functions import compare_player_hands

# Webcam
cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# Video
# cap = cv2.VideoCapture("../videos/bikes.mp4")

model = YOLO('../Yolo-Weights/playingCards.pt')

classNames = ['10C', '10D', '10H', '10S',
              '2C', '2D', '2H', '2S',
              '3C', '3D', '3H', '3S',
              '4C', '4D', '4H', '4S',
              '5C', '5D', '5H', '5S',
              '6C', '6D', '6H', '6S',
              '7C', '7D', '7H', '7S',
              '8C', '8D', '8H', '8S',
              '9C', '9D', '9H', '9S',
              'AC', 'AD', 'AH', 'AS',
              'JC', 'JD', 'JH', 'JS',
              'KC', 'KD', 'KH', 'KS',
              'QC', 'QD', 'QH', 'QS']

hole_cards = []
community_cards = ["None", "None", "None"]
display_state = 0
index = 0
hole_cards_string = ''
cards_str = ''
best_hands_string = ''
hands = []
while True:
    key = cv2.waitKey(1) & 0xFF
    success, img = cap.read()
    results = model(img, stream=True)
    detected_cards = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 3)
            w, h = x2 - x1, y2 - y1
            cvzone.cornerRect(img, (x1, y1, w, h))
            # Confidence
            conf = math.ceil((box.conf[0] * 100)) / 100
            # Class Name
            cls = int(box.cls[0])
            if conf > 0.3:
                detected_cards.append(classNames[cls])
            cvzone.putTextRect(img, f' {classNames[cls]} {conf}', (max(0, x1), max(30, y1)), scale=0.8,
                               thickness=1)
    # Get rid of repeated detections of the same card
    detected_cards = list(set(detected_cards))
    if display_state == 0:
        if len(detected_cards) == 2:
            hole_cards_string = ''
            for i, pair in enumerate(hole_cards):
                hole_cards_string += f" P{i+1} - "
                hole_cards_string += " ".join(pair)
            cvzone.putTextRect(img, f'Hole Cards : {hole_cards_string} P{len(hole_cards)+1} - {detected_cards[0]} '
                                    f'{detected_cards[1]}',
                               (50, 100), 1.5, 2,(255, 255, 255), (200, 0, 200))
            cvzone.putTextRect(img, f'Press c to Continue, a to Add More Hole Cards',
                               (50, 160), 1.5, 2,(255, 255, 255), (200, 0, 200))
            if key == ord('c'):
                hole_cards.append([detected_cards[0], detected_cards[1]])
                hole_cards_string = ''
                for i, pair in enumerate(hole_cards):
                    hole_cards_string += f" P{i + 1} - "
                    hole_cards_string += " ".join(pair)
                display_state = 1
            if key == ord('a'):
                hole_cards.append([detected_cards[0], detected_cards[1]])
                index += 1
        else:
            cvzone.putTextRect(img, f'Hole Cards : {hole_cards_string} P{len(hole_cards)+1} - ',
                               (50, 100), 1.5, 2,(255, 255, 255), (200, 0, 200))
            # if key == ord('c'):
            #     display_state = 1
    elif display_state == 1:
        if 5 >= len(detected_cards) >= 3:
            cvzone.putTextRect(img, f'Hole Cards : {hole_cards_string}',
                               (50, 100), 1.5, 2, (255, 255, 255), (200, 0, 200))
            community_cards = detected_cards
            cards_str = " ".join(community_cards)
            cvzone.putTextRect(img, f'Community Cards : {cards_str} - Press c to Continue',
                               (50, 160), 1.5, 2,(255, 255, 255), (200, 0, 200))
            if key == ord('c'):
                display_state = 2
                hands = [hole+community_cards for hole in hole_cards]
                winning_players, best_hands_info = compare_player_hands(hands)
                best_hands_string = ''
                for i, player in enumerate(winning_players):
                    best_hands_string += f"P{player + 1} - {best_hands_info[i][0]} "
        else:
            cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards_string}',
                               (50, 100), 1.5, 2, (255, 255, 255), (200, 0, 200))
            cards_str = " ".join(community_cards)
            cvzone.putTextRect(img, f'Community Cards Last Detected : {cards_str}',
                               (50, 160), 1.5, 2,(255, 255, 255), (200, 0, 200))

    elif display_state == 2:
        cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards_string}',
                           (50, 100), 1.5, 2, (255, 255, 255), (200, 0, 200))
        cvzone.putTextRect(img, f'Community Cards : {cards_str}',
                           (50, 160), 1.5, 2, (255, 255, 255), (200, 0, 200))

        cvzone.putTextRect(img, f'Best 5 Card Hand(s) : {best_hands_string}',
                           (50, 220), 1.5, 2, (255, 255, 255), (200, 0, 200))
        cvzone.putTextRect(img, 'Press r to Reset, b to Redo Community Cards', (50, 280),
                           1.5, 2, (255, 255, 255), (200, 0, 200))

        if key == ord('r'):
            display_state = 0
            index = 0
            hole_cards = []
            community_cards = ["None", "None", "None"]
            hole_cards_string = ''
            cards_str = ''
            best_hands_string = ''
            hands = []

        if key == ord('b'):
            display_state = 1
    cv2.imshow("Image", img)
    # cv2.waitKey(1)
    if key == ord('q'):
        break
