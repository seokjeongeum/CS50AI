import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_prob = 1
    people_name = list(people.keys())
    arg_info = {}
    default_value = {"genes": 0, "trait": False}
    arg_info = {person: default_value.copy() for person in people_name}

    for one in one_gene:
        arg_info[one]["genes"] = 1
    for two in two_genes:
        arg_info[two]["genes"] = 2
    for have in have_trait:
        arg_info[have]["trait"] = True

    
    for person in people:
        person_prob = 0
        if people[person]["mother"]==None and people[person]["father"]==None:
            person_prob = PROBS["gene"][arg_info[person]["genes"]]
        else:
            mother = people[person]["mother"]
            father = people[person]["father"]
            prob_from_mother = from_parent_prob(arg_info[mother]["genes"])
            prob_from_father = from_parent_prob(arg_info[father]["genes"])

            if arg_info[person]["genes"] == 0:
                person_prob = (1-prob_from_mother)*(1-prob_from_father)
            elif arg_info[person]["genes"] == 1:
                person_prob = (1-prob_from_mother)*(prob_from_father)+(prob_from_mother)*(1-prob_from_father)
            elif arg_info[person]["genes"] == 2:
                person_prob = prob_from_mother*prob_from_father
        
        if arg_info[person]["trait"] == True:
            person_prob = person_prob * PROBS["trait"][arg_info[person]["genes"]][True]
        elif arg_info[person]["trait"] == False:
            person_prob = person_prob * PROBS["trait"][arg_info[person]["genes"]][False]
        
        joint_prob *= person_prob
    return joint_prob


def from_parent_prob(count_genes):
    if count_genes == 0:
        return PROBS["mutation"]
    elif count_genes == 1:
        return 0.5
    elif count_genes ==2:
        return 1- PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            check = 1
        elif person in two_genes:
            check =2
        else:
            check = 0
        
        TF_trait = person in have_trait # True or False
        probabilities[person]["gene"][check] += p
        probabilities[person]["trait"][TF_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        total_gene_values = sum(probabilities[person]["gene"].values())
        total_trait_values = sum(probabilities[person]["trait"].values())

        for gg in probabilities[person]["gene"]:
            probabilities[person]["gene"][gg] /= total_gene_values
        
        for tt in probabilities[person]["trait"]:
            probabilities[person]["trait"][tt] /= total_trait_values

if __name__ == "__main__":
    main()
