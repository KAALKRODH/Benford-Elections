"""Check conformance of numerical data to Benford's Law."""
import sys
import math
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend to display the plot
import matplotlib.pyplot as plt

# Benford's Law percentages for leading digits 1-9
BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

def load_data(filename):
    """Open a text file & return a list of strings."""
    with open(filename) as f:
        return f.read().strip().split('\n')
    
def count_first_digits(data_list):
    """Count 1st digits in list of numbers; return counts & frequency."""
    first_digits = defaultdict(int)  # default value of int is 0
    for sample in data_list:
        if sample == '':
            continue
        try:
            int(sample)
        except ValueError as e:
            print(e, file=sys.stderr)
            print("Samples must be integers. Exiting.", file=sys.stderr)
            sys.exit(1)
        first_digits[sample[0]] += 1  
        
    # check for missing digits
    keys = [str(digit) for digit in range(1, 10)]
    for key in keys:
        if key not in first_digits:
            first_digits[key] = 0
            
    data_count = [v for (k, v) in sorted(first_digits.items())]
    total_count = sum(data_count)
    data_pct = [(i / total_count) * 100 for i in data_count]
    return data_count, data_pct, total_count

def get_expected_counts(total_count):
    """Return list of expected Benford's Law counts for total sample count."""
    return [round(p * total_count / 100) for p in BENFORD]

def chi_square_test(data_count, expected_counts):
    """Return boolean on chi-square test (8 degrees of freedom & P-val=0.05)."""
    chi_square_stat = 0  # chi square test statistic
    for data, expected in zip(data_count, expected_counts):
        chi_square = math.pow(data - expected, 2)
        chi_square_stat += chi_square / expected
    print("\nChi-squared Test Statistic = {:.3f}".format(chi_square_stat))
    print("Critical value at a P-value of 0.05 is 15.51.")    
    return chi_square_stat < 15.51

def bar_chart(data_pct):
    """Make bar chart of observed vs expected 1st digit frequency in percent."""
    fig = plt.figure()  # Create a Figure object
    ax = fig.add_subplot(1, 1, 1)

    index = [i + 1 for i in range(len(data_pct))]  # 1st digits for x-axis

    # Set the window title directly on the Tk object
    plt.get_current_fig_manager().window.wm_title('Percentage First Digits')

    ax.set_title('Data vs. Benford Values', fontsize=15)
    ax.set_ylabel('Frequency (%)', fontsize=16)
    ax.set_xticks(index)
    ax.set_xticklabels(index, fontsize=14)

    # build bars    
    rects = ax.bar(index, data_pct, width=0.95, color='black', label='Data')

    # attach a text label above each bar displaying its height
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height,
                '{:0.1f}'.format(height), ha='center', va='bottom', 
                fontsize=13)

    # plot Benford values as red dots
    ax.scatter(index, BENFORD, s=150, c='red', zorder=2, label='Benford')

    # Hide the right and top spines & add legend
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.legend(prop={'size':15}, frameon=False)
    
    plt.show()

def main():
    """Call functions and print stats."""
    # load data
    while True:
        filename = input("\nName of file with COUNT data: ")
        try:
            data_list = load_data(filename)
        except IOError as e:
            print("{}. Try again.".format(e), file=sys.stderr)
        else:
            break
    data_count, data_pct, total_count = count_first_digits(data_list)
    expected_counts = get_expected_counts(total_count)
    print("\nobserved counts = {}".format(data_count))
    print("expected counts = {}".format(expected_counts), "\n")
    
    print("First Digit Probabilities:")
    for i in range(1, 10):
        print("{}: observed: {:.3f}  expected: {:.3f}".
              format(i, data_pct[i - 1] / 100, BENFORD[i - 1] / 100))

    if chi_square_test(data_count, expected_counts):
        print("Observed distribution matches expected distribution.")
    else:
        print("Observed distribution does not match expected.", file=sys.stderr)       

    bar_chart(data_pct)    
        
if __name__ == '__main__':
    main()
    
    """Manipulate vote counts so that final results conform to Benford's Law."""

# example below is for Trump vs Clinton, Illinois, 2016 Presidental Election

def load_data(filename):
    """Open a text file of numbers & turn contents into a list of integers."""
    with open(filename) as f:
        lines = f.read().strip().split('\n')
        return [int(i) for i in lines]  # turn strings to integers

def steal_votes(opponent_votes, candidate_votes, scalar):
    """Use scalar to reduce one vote count & increase another, return as lists.

    Arguments:
    opponent_votes – votes to steal from
    candidate_votes - votes to increase by stolen amount
    scalar - fractional percentage, < 1, used to reduce votes

    Returns:
    list of changed opponent votes
    list of changed candidate votes
    
    """   
    new_opponent_votes = []
    new_candidate_votes = []
    for opp_vote, can_vote in zip(opponent_votes, candidate_votes):
        new_opp_vote = round(opp_vote * scalar)
        new_opponent_votes.append(new_opp_vote)
        stolen_votes = opp_vote - new_opp_vote
        new_can_vote = can_vote + stolen_votes
        new_candidate_votes.append(new_can_vote)
    return new_opponent_votes, new_candidate_votes
    

def main():
    """Run the program.

    Load data, set target winning vote count, call functions, display
    results as table, write new combined vote total as text file to
    use as input for Benford's Law analysis.

    """
    # load vote data
    c_votes = load_data('Clinton_votes_Illinois.txt')
    j_votes = load_data('Johnson_votes_Illinois.txt')
    s_votes = load_data('Stein_votes_Illinois.txt')
    t_votes = load_data('Trump_votes_Illinois.txt')

    total_votes = sum(c_votes + j_votes + s_votes + t_votes)


    # assume Trump amasses a plurality of the vote with 49%
    t_target = round(total_votes * 0.49)
    print("\nTrump winning target = {:,} votes".format(t_target))

    # calculate extra votes needed for Trump victory
    extra_votes_needed = abs(t_target - sum(t_votes))
    print("extra votes needed = {:,}".format(extra_votes_needed))

    # calculate scalar needed to generate extra votes
    scalar = 1 - (extra_votes_needed / sum(c_votes + j_votes + s_votes))
    print("scalar = {:.3}".format(scalar))
    print()

    # flip vote counts based on scalar & build new combined list of votes
    fake_counts = []
    new_c_votes, new_t_votes = steal_votes(c_votes, t_votes, scalar)
    fake_counts.extend(new_c_votes)
    new_j_votes, new_t_votes = steal_votes(j_votes, new_t_votes, scalar)
    fake_counts.extend(new_j_votes)
    new_s_votes, new_t_votes = steal_votes(s_votes, new_t_votes, scalar)
    fake_counts.extend(new_s_votes)
    fake_counts.extend(new_t_votes)  # add last as has been changing up til now   

    # compare old and new vote counts & totals in tabular form
    # switch-out "Trump" and "Clinton" as necessary
    for i in range(0, len(t_votes)):
        print("old Trump: {} \t new Trump: {} \t old Clinton: {} \t " \
              "new Clinton: {}".
              format(t_votes[i], new_t_votes[i], c_votes[i], new_c_votes[i]))              
        print("-" * 95)
    print("TOTALS:")
    print("old Trump: {:,} \t new Trump: {:,} \t old Clinton: {:,}  " \
          "new Clinton: {:,}".format(sum(t_votes), sum(new_t_votes),
                                     sum(c_votes), sum(new_c_votes)))
                                   
    # write-out a text file to use as input to benford.py program
    # this program will check conformance of faked votes to Benford's Law
    with open('fake_Illinois_counts.txt', 'w') as f:
        for count in fake_counts:
            f.write("{}\n".format(count))
    

if __name__ == '__main__':
    main()