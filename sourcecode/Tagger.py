from collections import defaultdict


# A class to hold the information about the tuples
class TaggerTuple:
    def __init__(self, from_tag, to_tag, pre_tag, score):
        self.from_tag = from_tag
        self.to_tag = to_tag
        self.pre_tag = pre_tag
        self.score = score


# A function to store the given corpus into string
def read_file(filename):
    corpus_line = ""

    with open(filename) as file:
        for line in file:
            corpus_line = corpus_line + line
    file.close()

    return corpus_line


# Tokenize input file and create a unigram model
def tokenize(corpus_line):
    unigram = defaultdict(dict)
    unigram_tokens = {}

    unigram_file = open("output\\unigram\\unigram.txt", "w")
    unigram_tokens_file = open("output\\unigram\\unigram_tokens.txt", "w")

    for word in corpus_line.split():
        words = word.split("_")

        if words[0] in unigram:
            if words[1] in unigram[words[0]]:
                unigram[words[0]][words[1]] = unigram[words[0]][words[1]] + 1
            else:
                unigram[words[0]][words[1]] = 1
        else:
            unigram[words[0]][words[1]] = 1

        if words[0] in unigram_tokens:
            unigram_tokens[words[0]] = unigram_tokens[words[0]] + 1
        else:
            unigram_tokens[words[0]] = 1

    for key, value in unigram.items():
        unigram_file.write(key + " " + str(value) + "\n")
    unigram_file.close()

    for key, value in unigram_tokens.items():
        unigram_tokens_file.write(key + " " + str(value) + "\n")
    unigram_tokens_file.close()

    return unigram


# Initialize the dummy corpus with mostly like tags
def initialize_with_most_likely_tag():
    most_likely_unigram = {}

    with open("output\\unigram\most_probable_unigram.txt", "w") as most_likely_unigram_file:
        for key, value in unigram.items():
            sorted_list = sorted(value, key=value.get, reverse=True)
            most_likely_unigram[key] = sorted_list[0]
            most_likely_unigram_file.write(key + " " + str(sorted_list[0]) + "\n")
    most_likely_unigram_file.close()

    return most_likely_unigram


# Train the model to generate 10 transformational templates
def tbl(most_likely_unigram, corpus_tuple, current_tag):
    n = 1
    transforms_queue = []

    while n <= 10:
        best_transform = get_best_transform(most_likely_unigram, corpus_tuple, correct_tag, current_tag, n)

        if best_transform.from_tag == '' and best_transform.to_tag == '':
            break

        apply_transform(best_transform, corpus_tuple, current_tag, n)
        transforms_queue.append(best_transform)
        n = n + 1

    return transforms_queue


# A function to get the best transform
def get_best_transform(most_likely_unigram, corpus_tuple, correct_tag, current_tag, n):
    instance = get_best_instance(most_likely_unigram, corpus_tuple, correct_tag, current_tag, n)
    return instance


# A function to get the best instance
def get_best_instance(most_likely_unigram, corpus_tuple, correct_tag, current_tag, iteration):
    best_score = 0
    all_tags = ["NN", "VB"]

    transform = TaggerTuple("", "", "", "")

    print("Iteration :: " + str(iteration))

    for from_tag in all_tags:
        for to_tag in all_tags:
            max_difference = 0
            num_good_transform = {}
            num_bad_transform = {}

            if from_tag == to_tag:
                continue

            for pos in range(1, len(corpus_tuple)):

                if to_tag == correct_tag[pos] and from_tag == current_tag[pos]:
                    rule = (current_tag[pos - 1], from_tag, to_tag)

                    if rule in num_good_transform:
                        num_good_transform[rule] += 1
                    else:
                        num_good_transform[rule] = 1
                elif from_tag == correct_tag[pos] and from_tag == current_tag[pos]:
                    rule = (current_tag[pos - 1], from_tag, to_tag)

                    if rule in num_bad_transform:
                        num_bad_transform[rule] += 1
                    else:
                        num_bad_transform[rule] = 1

            for key, value in num_good_transform.items():
                if key in num_bad_transform:
                    difference = num_good_transform[key] - num_bad_transform[key]
                else:
                    difference = num_good_transform[key]

                if difference > max_difference:
                    arg_max = key[0]
                    max_difference = difference

            if max_difference > best_score:
                best_rule = "Change tag FROM :: '" + from_tag + "' TO :: '" + to_tag + "' PREV tag :: '" + arg_max + "'"
                best_score = max_difference

                print("Best Rule :: " + best_rule)
                transform = TaggerTuple(from_tag, to_tag, arg_max, best_score)

    return transform


# Apply transform after calculating best score of transformation template
def apply_transform(best_transform, corpus_tuple, current_tag, n):
    current_tag_File = open("output\logs\iteration_" + str(n) + ".txt", "w")

    for pos in range(1, len(corpus_tuple)):
        if (current_tag[pos] == best_transform.from_tag) and (current_tag[pos - 1] == best_transform.pre_tag):
            current_tag[pos] = best_transform.to_tag

    for pos in range(0, len(current_tag)):
        current_tag_File.write(current_tag[pos] + "\n")


# Divide the corpus into 3 forms
# corpus_tuple : all the corpus words
# correct_tag :  all the corpus tags
# current_tag_File : most likely tag applied to all the words in corpus
def create_corpus_tuple(corpus_line, most_likely_unigram):
    corpus_tuple = []
    correct_tag = []
    current_tag = []

    corpus_tuple_file = open("output\\tuple\corpus_tuple.txt", "w")
    correct_tag_file = open("output\\tags\correct_tag.txt", "w")
    current_tag_file = open("output\\tags\current_tag.txt", "w")

    for word in corpus_line.split():
        words = word.split("_")

        corpus_tuple.append(words[0])
        correct_tag.append(words[1])
        current_tag.append(most_likely_unigram[words[0]])

        corpus_tuple_file.write(words[0] + "\n")
        correct_tag_file.write(words[1] + "\n")
        current_tag_file.write(most_likely_unigram[words[0]] + "\n")

    return corpus_tuple, correct_tag, current_tag


# sort all the transformation generated in oprder of their score
def sort_transformation_in_order_of_score(transformation_transforms_queue):
    sorted_Templates = sorted(transformation_transforms_queue, key=lambda x: x.score, reverse=True)
    index = 1

    with open("output\\top10.txt", "w") as top10_file:
        for transformation in sorted_Templates:
            result = str(index) + ":: From '" + transformation.from_tag + "' To '" + transformation.to_tag\
                     + "' when Prev '" + transformation.pre_tag + "'"
            print(result)
            top10_file.write(result + "\n")
            index = index + 1
    top10_file.close()

    return sorted_Templates


filename = "resources\POSTaggedTrainingSet.txt"

corpus_line = read_file(filename)
unigram = tokenize(corpus_line)

most_likely_unigram = initialize_with_most_likely_tag()
corpus_tuple, correct_tag, current_tag = create_corpus_tuple(corpus_line, most_likely_unigram)
transformation_transforms_queue = tbl(most_likely_unigram, corpus_tuple, current_tag)

print("\n================== Top 10 Rules ==================")
sorted_Templates = sort_transformation_in_order_of_score(transformation_transforms_queue)
