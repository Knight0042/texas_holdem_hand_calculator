from ultralytics import YOLO
import cv2
import cvzone
import math
from hand_detector import best_five_card_hand

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

hole_cards = ["None", "None"]
community_cards = ["None", "None", "None"]
display_state = 0
while True:
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
            hole_cards = [detected_cards[0], detected_cards[1]]
            cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards[0]}, {hole_cards[1]} - Press c to Confirm',
                               (50, 100), 2.5, 2,(255, 255, 255), (200, 0, 200))
            if cv2.waitKey(1) & 0xFF == ord('c'):
                display_state = 1
        else:
            cvzone.putTextRect(img, f'Hole Cards Last Detected : {hole_cards[0]}, {hole_cards[1]}',
                               (50, 100), 2.5, 2,(255, 255, 255), (200, 0, 200))
            if cv2.waitKey(1) & 0xFF == ord('c'):
                display_state = 1
    elif display_state == 1:
        if 5 >= len(detected_cards) >= 3:
            cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards[0]}, {hole_cards[1]}',
                               (50, 100), 2.5, 2, (255, 255, 255), (200, 0, 200))
            community_cards = detected_cards
            cards_str = " ".join(community_cards)
            cvzone.putTextRect(img, f'Community Cards : {cards_str} - Press c to Confirm',
                               (50, 160), 2.5, 2,(255, 255, 255), (200, 0, 200))
            if cv2.waitKey(1) & 0xFF == ord('c'):
                display_state = 2
        else:
            cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards[0]}, {hole_cards[1]}',
                               (50, 100), 2.5, 2, (255, 255, 255), (200, 0, 200))
            cards_str = " ".join(community_cards)
            cvzone.putTextRect(img, f'Community Cards Last Detected : {cards_str}',
                               (50, 160), 2.5, 2,(255, 255, 255), (200, 0, 200))

    elif display_state == 2:
        cvzone.putTextRect(img, f'2 Hole Cards : {hole_cards[0]}, {hole_cards[1]}',
                           (50, 100), 2.5, 2, (255, 255, 255), (200, 0, 200))
        cards_str = " ".join(community_cards)
        cvzone.putTextRect(img, f'Community Cards : {cards_str}',
                           (50, 160), 2.5, 2, (255, 255, 255), (200, 0, 200))
        hand = hole_cards + community_cards
        cvzone.putTextRect(img, f'Best 5 Card Hand : {best_five_card_hand(hand)}',
                           (50, 220), 3, 2, (255, 255, 255), (200, 0, 200))
        cvzone.putTextRect(img, 'Press r to Reset, b to Redo Community Cards', (50, 280),
                           3, 2, (255, 255, 255), (200, 0, 200))

        if cv2.waitKey(1) & 0xFF == ord('r'):
            display_state = 0
        if cv2.waitKey(1) & 0xFF == ord('b'):
            display_state = 1
    cv2.imshow("Image", img)
    # cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
