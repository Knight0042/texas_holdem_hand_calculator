#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <vector>
#include <string>
#include <cctype>
#include <algorithm>


namespace py = pybind11;

// Enums for suits and hands to make things clearer
enum Suit {HEARTS = 0, CLUBS, DIAMONDS, SPADES};
enum HandRank {UNKNOWN = 0, HIGH_CARD, PAIR, TWO_PAIR, THREE_OF_A_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_OF_A_KIND,
    STRAIGHT_FLUSH, ROYAL_FLUSH};

// This is a simple structure to hold the suit and rank of a card in integer form
struct card{
    int suit; // 0 = hearts, 1 = clubs, 2 = diamonds, 3 = spades
    int rank; // 2-14 (14 = Ace)
};

// This struct contains both the hand from the enums above and any needed extra info for certain hands
// For example, for a full house a struct could be {hand_rank=FULL_HOUSE (7), hand_info = {2, 3, 4, 2}}
// This represents a hand like {2H, 2C, 2D, 4S, 4D}
struct hand{
    int hand_rank; // (ex HIGH_CARD, PAIR, TWO_PAIR, THREE_OF_A_KIND, ...)
    std::vector<int> hand_info; // (ex above for a full house)
};

/*
This function simply converts a character into the corresponding suit
Input - char ('H')
Output - int (0)
*/
int suit_from_char(char s) {
    s = std::toupper(s); // convert to upper to handle lower case letters
    switch (s) {
        case 'H':
            return HEARTS;
        case 'C':
            return CLUBS;
        case 'D':
            return DIAMONDS;
        case 'S':
            return SPADES;
        default: // If the character does not match one of the suits return -1 to indicate an error
            return -1;
    }
}

/*
This function converts a string into a card struct
Input - string (ex "QH")
Output - Card Struct (ex {suit=HEARTS, rank=12})
*/
card string_to_card(const std::string &card_str){
    card new_card;
    if (card_str.length()==3){ // This handles the case where the card is a 10 ("10H", "10S", ...)
        std::string rank = card_str.substr(0, 2);
        new_card.rank = std::stoi(rank); // Convert the first 2 characters to an integer (10)
        char suit = card_str[2];
        new_card.suit = suit_from_char(suit); // Get the suit from the last character

    } else if (card_str.length()==2){
        char rank = card_str[0];
        switch(rank){ // If the rank is a letter assign the correct value, otherwise convert to an integer
            case 'a':
            case 'A':
                new_card.rank = 14;
                break;
            case 'k':
            case 'K':
                new_card.rank = 13;
                break;
            case 'q':
            case 'Q':
                new_card.rank = 12;
                break;
            case 'j':
            case 'J':
                new_card.rank = 11;
                break;
            default:
                if (std::isdigit(rank)){
                    new_card.rank = rank-'0'; // This handles converting from a character integer to an actual integer
                } else{
                    new_card.rank = -1; // If the rank is not valid return -1 to indicate error
                }
                break;
        }

        char suit = card_str[1];
        new_card.suit = suit_from_char(suit); // Get the suit from the last character
    } else{
        // error
        new_card.suit = -1;
        new_card.rank = -1;
    }
    return new_card;
}

/*
This function is an extension of string_to_card to handle multiple cards at once
Input - List of strings (ex ["QH", "JH", "2C"])
Output - List of card structs
*/
std::vector<card> strings_to_cards(const std::vector<std::string> &card_strings){
    std::vector<card> cards;
    for (int i=0; i<card_strings.size(); i++){
        std::string card_str = card_strings[i]; // iterate through each card and add it to the cards list
        card new_card = string_to_card(card_str);
        cards.push_back(new_card);
    }
    return cards;
}


/*
This function converts card structs to 2 integer lists, one for the suits and one for the ranks. Additionally,
the function can either sort the lists in ascending order, or leave them in the same order as the inputs (default).
Input - A list/vector of card structs and an integer value indicating whether order should be preserved.
Output - One vector containing two integer lists in sorted or unsorted order

*/
std::vector<std::vector<int>> cards_to_suits_ranks(std::vector<card> input_cards, const int &preserve_order = 1){
    std::vector<int> suits;
    std::vector<int> ranks;
    for (int i=0; i<input_cards.size(); i++){
        card new_card = input_cards[i]; // iterate through each card split it
        suits.push_back(new_card.suit);
        ranks.push_back(new_card.rank);
    }
    if (preserve_order==0){ // Unless specified that the caller wants to maintain the input order, sort the lists
      std::sort(suits.begin(), suits.end());
      std::sort(ranks.begin(), ranks.end());
    }
    std::vector<std::vector<int>> return_vector = {suits, ranks};
    return return_vector;
}


/*
This function determines the hand rank of a given 5 card input hand and also provides additional info for certain hands.
Input -
Output - A hand Struct. For example, for a full house the return struct could be
{hand_rank=FULL_HOUSE (7), hand_info = {2, 3, 4, 2}}

*/

hand overall_hand_checker(const std::vector<card> &input_hand){
    hand final_hand;
    final_hand.hand_rank = UNKNOWN;
    if (input_hand.size() != 5){ // Must have a 5 card hand
        return final_hand;
    }
    std::vector<std::vector<int>> suits_ranks = cards_to_suits_ranks(input_hand, 0);
    std::vector<int> suits = suits_ranks[0]; // This will give the suits and ranks in sorted order
    std::vector<int> ranks = suits_ranks[1];

    // Check for a flush
    if (std::count(suits.begin(), suits.end(), suits[0])==5){
        final_hand.hand_rank = FLUSH;
    }

    int straight_count = 1;
    int past_rank = ranks[0];
    int repeated_card_count = 1;
    for (int i=1; i<5; i++){ // We can start from i = 1 because the i = 0 case does not matter
        int cur_rank = ranks[i];
        if (past_rank == cur_rank){
            repeated_card_count++; // Checking for pairs, trips, etc.
        } else if ((past_rank+1 == cur_rank) || (cur_rank == 14 && ranks[0]==2)){
            // Check for straight. Also check for ace low straight
            straight_count++;
        } else{
            if (repeated_card_count>=2){ // This indicates a pair or better
                final_hand.hand_info.push_back(past_rank); // Add the card rank and # of repetitions for later use
                final_hand.hand_info.push_back(repeated_card_count);
            }
            repeated_card_count = 1; // reset the # of repeated cards
        }
        past_rank = cur_rank; // Update the past rank
    }
    if (repeated_card_count>=2){ // This indicates a pair or better
        final_hand.hand_info.push_back(past_rank); // Add the card rank and # of repetitions for later use
        final_hand.hand_info.push_back(repeated_card_count);
    }

    if (straight_count == 5){ // Check for straight
        if (final_hand.hand_rank == FLUSH){
            if (ranks[3]==13){ // If there is a straight+flush and the second to last card is a king, it's a royal flush
                final_hand.hand_rank = ROYAL_FLUSH;
            } else{ // If not a Royal Flush it is a Straight Flush
                final_hand.hand_rank = STRAIGHT_FLUSH;
            }
        } else{ // If not a flush, just a normal straight
            final_hand.hand_rank = STRAIGHT;
        }
    }

    if (final_hand.hand_rank != ROYAL_FLUSH && final_hand.hand_rank != STRAIGHT_FLUSH){
        if (final_hand.hand_info.size() == 2){ // Check for four/three of a kind, or a pair
            if (final_hand.hand_info[1] == 4){
                final_hand.hand_rank = FOUR_OF_A_KIND;
            } else if (final_hand.hand_rank != STRAIGHT && final_hand.hand_rank != FLUSH){
                if (final_hand.hand_info[1] == 3){
                    final_hand.hand_rank = THREE_OF_A_KIND;
                } else if (final_hand.hand_info[1] == 2){
                    final_hand.hand_rank = PAIR;
                }
            }
        } else if (final_hand.hand_info.size() == 4){ // Check for a full house or a two pair
            if (final_hand.hand_info[1] == 3 || final_hand.hand_info[3] == 3){
                final_hand.hand_rank = FULL_HOUSE;
            } else if (final_hand.hand_rank != STRAIGHT && final_hand.hand_rank != FLUSH){
                final_hand.hand_rank = TWO_PAIR;
            }
        } else if (final_hand.hand_rank != STRAIGHT && final_hand.hand_rank != FLUSH){
            final_hand.hand_rank = HIGH_CARD; // If no other hand is detected, Assign High Card
        }
    }
    return final_hand; // Return the calculated hand
}



// A function to calculate the equity of each player given certain hole cards and a community board
// Input - A double vector that contains each players hand (Passed into the function in python as
// [["AH", "KH"], ["9C", "QS"]]), Then another vector containing community cards (Passed as ["QH", "JH", "2C"])
// Output - A vector that contains the equities of each player as a list of doubles (0-1)
std::vector<double> calculate_equity(const std::vector<std::vector<std::string>> &hands,
                        const std::vector<std::string> &board) {
    std::vector<double> equities(hands.size());


    return equities;
}


PYBIND11_MAKE_OPAQUE(std::vector<card>);

PYBIND11_MODULE(equity_calc, m) {
    m.doc() = "Poker equity calculator in C++";

    py::bind_vector<std::vector<card>>(m, "CardVector");

    py::class_<card>(m, "Card")
        .def(py::init())
        .def_readwrite("suit", &card::suit)
        .def_readwrite("rank", &card::rank);

    py::class_<hand>(m, "Hand")
        .def(py::init())
        .def_readwrite("hand_rank", &hand::hand_rank)
        .def_readwrite("hand_info", &hand::hand_info);

    py::enum_<Suit>(m, "Suit")
    .value("CLUBS", Suit::CLUBS)
    .value("DIAMONDS", Suit::DIAMONDS)
    .value("HEARTS", Suit::HEARTS)
    .value("SPADES", Suit::SPADES)
    .export_values();

    py::enum_<HandRank>(m, "HandRank")
    .value("UNKNOWN", HandRank::UNKNOWN)
    .value("HIGH_CARD", HandRank::HIGH_CARD)
    .value("PAIR", HandRank::PAIR)
    .value("TWO_PAIR", HandRank::TWO_PAIR)
    .value("THREE_OF_A_KIND", HandRank::THREE_OF_A_KIND)
    .value("STRAIGHT", HandRank::STRAIGHT)
    .value("FLUSH", HandRank::FLUSH)
    .value("FULL_HOUSE", HandRank::FULL_HOUSE)
    .value("FOUR_OF_A_KIND", HandRank::FOUR_OF_A_KIND)
    .value("STRAIGHT_FLUSH", HandRank::STRAIGHT_FLUSH)
    .value("ROYAL_FLUSH", HandRank::ROYAL_FLUSH)
    .export_values();

    m.def("calculate_equity", &calculate_equity, "Calculate equity given a hand and board");
    m.def("overall_hand_checker", &overall_hand_checker, "Calculate a players overall hand");
    m.def("cards_to_suits_ranks", &cards_to_suits_ranks, "Convert a list of cards to their suits and ranks");
    m.def("strings_to_cards", &strings_to_cards, "Convert a list of strings to a list of cards");
    m.def("string_to_card", &string_to_card, "Convert a string to a card");
    m.def("suit_from_char", &suit_from_char, "Convert a character into a integer value representing a suit");
}