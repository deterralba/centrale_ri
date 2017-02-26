from statistics import mean

def show_recall_precision(rec_pre, rank):
    from matplotlib import pyplot as plt
    import numpy as np
    rec_pre.sort(key=lambda x: x[0])  # sort (recall, precision) couples by recall
    recall = [x[0] for x in rec_pre]
    precision = [x[1] for x in rec_pre]
    decreasing_max_precision = np.maximum.accumulate(precision[::-1])[::-1]
    fig, ax = plt.subplots(1, 1)
    ax.set_title('Precision / Recall for the rank {}'.format(rank))
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_xlim([0,1.1])
    ax.set_ylim([0,1.1])
    ax.plot(recall, precision, '--g')
    ax.step(recall, decreasing_max_precision, '-b')
    fig.show()

def get_precision(truth, results):
    return 0 if len(results) == 0 else sum([1 for res in results if res in truth])/len(results)

def get_recall(truth, results):
    return 1 if len(truth) == 0 else sum([1 for res in results if res in truth])/len(truth)

def F1_measure(recall, precision, beta=1):
    precision = max(precision, 0.00000001)
    recall = max(recall, 0.00000001)
    return 2/((1/precision) + (1/recall))

def average_precision(truth, prediction):
    if not truth:
        return 0
    sum_ = 0
    num_truth = 0
    for i, p in enumerate(prediction):
        if p in truth and p not in prediction[:i]:
            num_truth += 1
            sum_ += num_truth / (i + 1)
    score = sum_ / len(truth)
    return score

def MAP(queries, relevant_docs, results_for_query):
    return mean(
        [average_precision(relevant_docs[q], results_for_query[q]) for q in queries.keys()]
    )



