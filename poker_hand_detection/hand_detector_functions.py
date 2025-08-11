import itertools


# This function takes in a list of cards and determines the best possible 5 card hand when those cards are combined
# Inputs - cards (ex ["JC", "10H", "9C", "8C", "7D", "8D", "AD"])
# Outputs - Final hand name (ex Straight), Best 5 Card Hand Combination (ex ["JC", "10H", "9C", "8C", "7D"]), and
# Any additional info (only for certain hands)
def best_five_card_hand(cards):
    final_hand = 'Unknown'
    final_hand_combo = []
    final_hand_info = []
    hand_list = []
    hand_combos = itertools.combinations(cards, 5)
    for hand_combo in hand_combos:
        hand, hand_info = hand_detector(hand_combo)
        if hand_dictionary[hand] > hand_dictionary[final_hand]:
            final_hand = hand
            final_hand_combo = hand_combo
            final_hand_info = hand_info
        elif hand_dictionary[hand] == hand_dictionary[final_hand]:
            # need to handle the case where 2 of the same type of hand are returned but one is better
            better = better_between_two_hands([hand, hand_combo, hand_info],
                                              [final_hand, final_hand_combo, final_hand_info])
            if better == 1:
                final_hand = hand
                final_hand_combo = hand_combo
                final_hand_info = hand_info
    return final_hand, final_hand_combo, final_hand_info


def compare_player_hands(hands):
    # best_hands is of the form [[first hand name, cards in first hand, hand info], ...]
    best_hands = [best_five_card_hand(hand) for hand in hands]
    best_hand = 'Unknown'
    matching_hands = set()
    for hand_index, hand in enumerate(best_hands):
        if hand_dictionary[hand[0]] > hand_dictionary[best_hand]:
            best_hand = hand[0]
            matching_hands = {hand_index}
        elif hand_dictionary[hand[0]] == hand_dictionary[best_hand]:
            # matching_hands.add(best_hand_index)
            matching_hands.add(hand_index)

    # matching_hands = list(matching_hands)
    removed_hands = set()
    if len(matching_hands) > 1:
        hand_comparisons = itertools.combinations(matching_hands, 2)
        for hand_comparison in hand_comparisons:
            # These two hands are each a list of 5 cards.
            # All hands should have the same overall state (ex all are flushes)
            # The goal is to determine the best hand
            hand_one = best_hands[hand_comparison[0]]
            hand_two = best_hands[hand_comparison[1]]
            better_hand = better_between_two_hands(hand_one, hand_two)
            if better_hand == 1:
                removed_hands.add(hand_comparison[1])
            elif better_hand == 2:
                removed_hands.add(hand_comparison[0])
            # Otherwise the hands are exactly the same and the players should chop the pot
    final_hand_indexes = sorted(matching_hands - removed_hands)
    best_hand_info = [best_hands[idx] for idx in final_hand_indexes]
    return final_hand_indexes, best_hand_info


# This function determines the better hand between two hands of the same type (ex both are straights)
# by comparing individual cards in each hand
# Input - 2 hands of the form [type (ex straight), cards in hand (ex ["JC", "10H", "9C", "8C", "7D"]), extra hand info]
# Output - 0 indicates the hands are the same value, 1 indicates hand one is better, 2 indicates hand two is better
def better_between_two_hands(hand_one, hand_two):
    better_hand = 0
    hand_type = hand_one[0]
    hand_one_suits, hand_one_ranks, hand_one_rank_values = split_card_strings(hand_one[1])
    hand_two_suits, hand_two_ranks, hand_two_rank_values = split_card_strings(hand_two[1])
    hand_one_info = hand_one[2]
    hand_two_info = hand_two[2]
    if hand_type == 'Four of a Kind' or hand_type == 'Three of a Kind' or hand_type == 'Pair':
        if hand_one_info[0] > hand_two_info[0]:
            better_hand = 1
        elif hand_one_info[0] == hand_two_info[0]:
            # Need to check the remaining cards same as a high card so we can just change the type to
            # 'High Card' and it will be handled in the next section
            hand_type = 'High Card'
        else:
            better_hand = 2
    elif hand_type == 'Two Pair':
        higher_pair_value_one = max(hand_one_info)
        higher_pair_value_two = max(hand_two_info)
        if higher_pair_value_one > higher_pair_value_two:
            better_hand = 1
        elif higher_pair_value_one == higher_pair_value_two:

            higher_pair_value_one = min(hand_one_info)
            higher_pair_value_two = min(hand_two_info)
            if higher_pair_value_one > higher_pair_value_two:
                better_hand = 1
            elif higher_pair_value_one == higher_pair_value_two:
                # There Should only be one remaining value in the ranks after the two pairs are removed
                high_one = [v for v in hand_one_rank_values if v not in hand_one_info][0]
                high_two = [v for v in hand_two_rank_values if v not in hand_two_info][0]
                if high_one > high_two:
                    better_hand = 1
                elif high_one < high_two:
                    better_hand = 2
                # If they are equal we don't need to do anything because the default output is 0
            else:
                better_hand = 2
        else:
            better_hand = 2
    elif hand_type == 'Full House':
        # The hand info for a full house is of the form [[rank 1, 2 or 3], [rank 2, 3 or 2]]
        if hand_one_info[0][1] == 3:
            three_rank_one = hand_one_info[0][0]
            two_rank_one = hand_one_info[1][0]
        else:
            three_rank_one = hand_one_info[1][0]
            two_rank_one = hand_one_info[0][0]

        if hand_two_info[0][1] == 3:
            three_rank_two = hand_two_info[0][0]
            two_rank_two = hand_two_info[1][0]
        else:
            three_rank_two = hand_two_info[1][0]
            two_rank_two = hand_two_info[0][0]

        if three_rank_one > three_rank_two:
            better_hand = 1
        elif three_rank_one == three_rank_two:
            if two_rank_one > two_rank_two:
                better_hand = 1
            elif two_rank_one < two_rank_two:
                better_hand = 2
        else:
            better_hand = 2

    if hand_type == 'Flush' or hand_type == 'High Card' or hand_type == 'Straight Flush' or hand_type == 'Straight':
        while True:
            if len(hand_one_rank_values) == 0:
                # This handles the case where the hands are the same
                break
            max_one = max(hand_one_rank_values)
            max_two = max(hand_two_rank_values)
            if max_one == max_two:
                hand_one_rank_values.remove(max_one)  # Remove the largest values to compare the next highest value
                hand_two_rank_values.remove(max_two)
                if hand_type == 'Straight Flush' or hand_type == 'Straight':
                    # If this is a straight and the high card matches the other cards will match (unless it's an ace)
                    if max_one == 14:  # check for an ace
                        max_one = max(hand_one_rank_values)
                        max_two = max(hand_two_rank_values)
                        if max_one == max_two:
                            break
                        elif max_one > max_two:
                            better_hand = 1
                            break
                        else:
                            better_hand = 2
                            break
                    else:  # All cards will match so the hands are equal
                        break
            else:
                if hand_type == 'Straight Flush' or hand_type == 'Straight':
                    # We already know the high cards are not both aces from an earlier check so check both separately
                    if max_one == 14:  # Check for an ace, need to check high vs low ace straight
                        if min(hand_one_rank_values) == 2:
                            better_hand = 2  # This indicates a low ace straight so the other straight is better
                            break
                    elif max_two == 14:
                        if min(hand_two_rank_values) == 2:
                            better_hand = 1  # This indicates a low ace straight so the other straight is better
                            break
                # Assuming there is not an ace the higher card indicates the better straight, and in a flush the ace
                # is always better so there is no need to perform an additional check
                if max_one > max_two:
                    better_hand = 1
                    break
                else:
                    better_hand = 2
                    break
    return better_hand


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


# This function splits card strings into the corresponding suits and ranks
# Input - list of cards
# Output - suits, ranks, rank_values
def split_card_strings(cards):
    suits = []
    ranks = []
    for card in cards:
        if len(card) == 3:
            ranks.append(card[0:2])
            suits.append(card[2])
        else:
            ranks.append(card[0])
            suits.append(card[1])

    # Convert string ranks to integer values
    rank_values = []
    for rank in ranks:
        rank_value = rank_dictionary[rank]
        rank_values.append(rank_value)
    rank_values.sort()

    return suits, ranks, rank_values


# This function determines a poker hand given 5 cards
# Inputs - A list of 5 cards as strings (ex ["2D", "2S", "9C", "KD", "10C"])
# Outputs - Name of the hand (ex 'Flush' or 'Straight') and hand specific info (ex for a full house return a list with
# info about the full house. Such as [[10, 3], [4, 2]] )
def hand_detector(hand):
    if len(hand) != 5:
        return 'Wrong Number of Cards', []
    determined_hand = 'Unknown'
    hand_specific_info = []
    suits, ranks, rank_values = split_card_strings(hand)

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
                hand_specific_info = [rank]
            elif occurrences == 3:
                full_house_check[full_house_index] = [rank, 3]
                full_house_index += 1
                if determined_hand != 'Straight' and determined_hand != 'Flush' and determined_hand != 'Four of a Kind':
                    determined_hand = 'Three of a Kind'
                    hand_specific_info = [rank]
            elif occurrences == 2:
                full_house_check[full_house_index] = [rank, 2]
                full_house_index += 1
                if determined_hand != 'Straight' and determined_hand != 'Flush' and determined_hand != 'Four of a Kind':
                    if determined_hand == 'Pair':
                        determined_hand = 'Two Pair'
                        hand_specific_info.append(rank)
                    else:
                        determined_hand = 'Pair'
                        hand_specific_info = [rank]
        if determined_hand != 'Four of a Kind':
            if (full_house_check[0][1] == 2 or full_house_check[0][1] == 3) and (full_house_check[1][1] == 2 or
                    full_house_check[1][1] == 3) and (full_house_check[1][1] != full_house_check[0][1]):
                determined_hand = 'Full House'
                hand_specific_info = full_house_check
        if determined_hand == 'Unknown':
            determined_hand = 'High Card'
    return determined_hand, hand_specific_info


if __name__ == "__main__":
    print(hand_detector(["KH", "AH", "QH", "JH", "10H"]))  # Royal Flush
    print(hand_detector(["QC", "JC", "10C", "9C", "8C"]))  # Straight Flush
    print(hand_detector(["5C", "5S", "5H", "5D", "QH"]))  # Four of a Kind
    print(hand_detector(["2H", "2D", "2S", "10H", "10C"]))  # Full House
    print(hand_detector(["2D", "KD", "7D", "6D", "5D"]))  # Flush
    print(hand_detector(["JC", "10H", "9C", "8C", "7D"]))  # Straight
    print(hand_detector(["10H", "10C", "10D", "2D", "5S"]))  # Three of a Kind
    print(hand_detector(["KD", "KH", "5C", "5S", "6D"]))  # Two Pair
    print(hand_detector(["2D", "2S", "9C", "KD", "10C"]))  # Pair
    print(hand_detector(["KD", "5H", "2D", "10C", "JH"]))  # High Card
    print(hand_detector(["4D", "5H", "3C", "2C", "AH"]))  # Straight (with low Ace)
