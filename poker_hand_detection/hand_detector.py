import itertools


def best_five_card_hand(cards):
    final_hand = 'Unknown'
    hand_list = []
    hand_combos = itertools.combinations(cards, 5)
    for hand_combo in hand_combos:
        hand = hand_detector(hand_combo)
        if hand_dictionary[hand] > hand_dictionary[final_hand]:
            final_hand = hand
    return final_hand


hand_dictionary = {
    "Royal Flush": 10,
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "Pair": 2,
    "High Card": 1,
    "Unknown": 0
}


rank_dictionary = {
    'A': 14,
    'K': 13,
    'Q': 12,
    'J': 11,
    '10': 10,
    '9': 9,
    '8': 8,
    '7': 7,
    '6': 6,
    '5': 5,
    '4': 4,
    '3': 3,
    '2': 2
}
def hand_detector(hand):

    # This function determines the hand given 5 cards

    if len(hand) != 5:
        return 'Wrong Number of Cards'

    suits = []
    ranks = []
    determined_hand = 'Unknown'
    for card in hand:
        if len(card) == 3:
            ranks.append(card[0:2])
            suits.append(card[2])
        else:
            ranks.append(card[0])
            suits.append(card[1])

    # Check for a flush
    same_suit_counter = 0
    last_suit = ''
    for suit in suits:
        if same_suit_counter == 0:
            last_suit = suit
            same_suit_counter = 1
        else:
            if suit == last_suit:
                same_suit_counter += 1
            else:
                same_suit_counter = 1
                last_suit = suit
    if same_suit_counter >= 5:
        determined_hand = 'Flush'

    # Check for a Straight or straight flush or Royal Flush
    # Convert string ranks to integer values
    rank_values = []
    for rank in ranks:
        rank_value = rank_dictionary[rank]
        rank_values.append(rank_value)
    # Check for a straight
    rank_values.sort()
    prev_value = 0
    cards_in_a_row = 0
    most_cards_in_a_row = 0
    repeated_rank_count = 0
    repeated_rank = 0
    repeated_ranks = []

    for value in rank_values:
        if repeated_rank == value:
            repeated_rank_count += 1
        else:
            if repeated_rank_count >= 2:
                repeated_ranks.append([repeated_rank, repeated_rank_count])
            repeated_rank = value
            repeated_rank_count = 1

        if prev_value == 0:
            prev_value = value
            cards_in_a_row = 1
        else:
            if prev_value == value-1:
                cards_in_a_row += 1
                prev_value = value
            else:
                if value == 14 and rank_values[0] == 2:
                    cards_in_a_row += 1
                else:
                    most_cards_in_a_row = max(cards_in_a_row, most_cards_in_a_row)
                    cards_in_a_row = 1
    most_cards_in_a_row = max(cards_in_a_row, most_cards_in_a_row)
    if most_cards_in_a_row >= 5:
        if determined_hand == 'Flush':
            if rank_values[-1] == 14:
                determined_hand = 'Royal Flush'
            else:
                determined_hand = 'Straight Flush'
        else:
            determined_hand = 'Straight'

    full_house_check = [[0, 0], [0, 0]]
    full_house_index = 0
    if repeated_rank_count >= 2:
        repeated_ranks.append([repeated_rank, repeated_rank_count])
    if determined_hand != 'Royal Flush' and determined_hand != 'Straight Flush':
        for rank_occurrence in repeated_ranks:
            rank = rank_occurrence[0]
            occurrences = rank_occurrence[1]
            if occurrences == 4:
                determined_hand = 'Four of a Kind'
            elif occurrences == 3:
                full_house_check[full_house_index] = [rank, 3]
                full_house_index += 1
                if determined_hand != 'Straight' and determined_hand != 'Flush' and determined_hand != 'Four of a Kind':
                    determined_hand = 'Three of a Kind'
            elif occurrences == 2:
                full_house_check[full_house_index] = [rank, 2]
                full_house_index += 1
                if determined_hand != 'Straight' and determined_hand != 'Flush' and determined_hand != 'Four of a Kind':
                    if determined_hand == 'Pair':
                        determined_hand = 'Two Pair'
                    else:
                        determined_hand = 'Pair'
        if determined_hand != 'Four of a Kind':
            if (full_house_check[0][1] == 2 or full_house_check[0][1] == 3) and (full_house_check[1][1] == 2 or
                    full_house_check[1][1] == 3) and (full_house_check[1][1] != full_house_check[0][1]):
                determined_hand = 'Full House'
        if determined_hand == 'Unknown':
            determined_hand = 'High Card'
    return determined_hand


if __name__ == "__main__":
    hand_detector(["KH", "AH", "QH", "JH", "10H"])  # Royal Flush
    hand_detector(["QC", "JC", "10C", "9C", "8C"])  # Straight Flush
    hand_detector(["5C", "5S", "5H", "5D", "QH"])  # Four of a Kind
    hand_detector(["2H", "2D", "2S", "10H", "10C"])  # Full House
    hand_detector(["2D", "KD", "7D", "6D", "5D"])  # Flush
    hand_detector(["JC", "10H", "9C", "8C", "7D"])  # Straight
    hand_detector(["10H", "10C", "10D", "2D", "5S"])  # Three of a Kind
    hand_detector(["KD", "KH", "5C", "5S", "6D"])  # Two Pair
    hand_detector(["2D", "2S", "9C", "KD", "10C"])  # Pair
    hand_detector(["KD", "5H", "2D", "10C", "JH"])  # High Card
    hand_detector(["4D", "5H", "3C", "2C", "AH"])  # Straight (with low Ace)
