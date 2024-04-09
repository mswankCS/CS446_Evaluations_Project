# import package ...
import sys
import math


def eval(trecrunFile, qrelsFile, outputFile):
    # get list of all unique queries in trecrun
    queries = []
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    for line in trec_lines:
        split = line.split()
        if split[0] not in queries:
            queries.append(split[0])
    # get measures for each query
    query_evals = {}
    evals_sums = {
        'NDCG@20': 0,
        'numRel': 0,
        'relFound' :0,
        'RR': 0,
        'P@10': 0,
        'R@10': 0,
        'F1@10': 0,
        'AP': 0
        }
    for q in queries:
        query_evals[q] = run_all_evals(q, trecrunFile, qrelsFile)
    out = open(outputFile, 'w+')
    for eval in query_evals:
        for method in query_evals[eval]:
            out.write(f"{method[0]:<8}")
            out.write('   ')
            out.write(f"{eval:<8}")
            out.write('   ')
            out.write(f"{str(method[1]):<8}")
            out.write('\n')
            evals_sums[method[0]] += float(method[1])
    # for all
    for sum in evals_sums:
        if sum == 'RR':
            out.write(f"{str('MRR'):<8}")
        elif sum == 'AP':
            out.write(f"{str('MAP'):<8}")
        else:
            out.write(f"{str(sum):<8}")
        out.write('   ')
        out.write(f"{str('all'):<8}")
        out.write('   ')
        if sum == 'numRel' or sum == 'relFound':
            out.write(f"{str(str(int(evals_sums[sum]))):<8}")
        else:
            data = "{:6.4f}".format(evals_sums[sum] / len(queries))
            out.write(f"{str(data):<8}")
        out.write('\n')

    print("Success")
    out.close()
    trec.close()
    
    
# find number of relevant documents given a query and qrelsFile (returns (int, []))
def find_num_rel(query, qrelsFile):
    total = 0
    rel_docs = []
    qrels = open(qrelsFile, 'r')
    qrels_lines = qrels.readlines()
    for line in qrels_lines:
        columns = line.split()
        if columns[0] == query:
            if int(columns[3]) > 0:
                total += 1
                rel_docs.append(columns[2])
    qrels.close()
    return (total, rel_docs)


# gives count of how many docs from docids are found in trecrunFile
def find_num_rel_found(query, trecrunFile, docids):
    count = 0
    rel_docs = []
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    for line in trec_lines:
        split = line.split()
        if (split[0] == query and split[2] in docids):
            count += 1
            rel_docs.append(split[2])
    trec.close()
    return (count, rel_docs)


# get NDCG at rank p
def get_NDCG(query, trecrunFile, qrelsFile, p):
    if (find_num_rel(query, qrelsFile)[0] == 0):
        return 0
    qrels = open(qrelsFile, 'r')
    qrels_lines = qrels.readlines()
    query_lines = []
    for line in qrels_lines:
        if line.split()[0] == query:
            query_lines.append(line.replace('\n', '').split())
    # find DCG
    p_long_arr = []
    # get top p-ranked docids for query (from trecrun)
    order = get_ranking_order(query, trecrunFile, p)
    found_count = 0
    for doc in order:
        found = found_count
        for line in query_lines:
            if line[2] == doc:
                p_long_arr.append(line)
                found += 1
        found_count += 1
        if found != found_count:
            p_long_arr.append([0, 0, 0, 0])
    dcg = get_DCG(p_long_arr, p)
    # find NDCG
    def sort_key(array):
        return float(array[3])
    ideal_query_lines = sorted(query_lines, key=sort_key, reverse=True)[:p]
    idcg = get_DCG(ideal_query_lines, p)
    qrels.close()
    return dcg / idcg


# calculate DCG given qrels_arr, an array of arrays of the lines from qrels, and p, the rank at which to find DCG at
def get_DCG(qrels_arr, p):
    new = ['skip'] + qrels_arr
    value = float(new[1][3])
    i = 2
    while (i < p + 1):
        gain = float(new[i][3])
        value += gain / math.log2(i)
        i += 1
    return value


# retreives an array of the top p docids for a specific query, from trecrun
def get_ranking_order(query, trecrunFile, p):
    i = 0
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    split_lines = []
    for line in trec_lines:
        split_lines.append(line.split())
    def has_query(arr):
        if arr[0] == query:
            return True
        else:
            return False
    query_lines = filter(has_query, split_lines)
    query_lines = list(query_lines)[:p]
    ret = []
    for line in query_lines:
        ret.append(line[2])
    trec.close()
    return ret
    

# calculate reciprocal rank given a query
def get_reciprocal_rank(query, trecrunFile, qrelsFile):
    docids = find_num_rel(query, qrelsFile)[1]
    if (find_num_rel_found(query, trecrunFile, docids)[0] == 0):
        return 0
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    for line in trec_lines:
        split = line.split()
        if (split[0] == query and split[2] in docids):
            trec.close()
            return 1 / int(split[3])
        

# returns precision at rank p
def precision_at_p(query, trecrunFile, qrelsFile, p):
    # list of all relevant docs
    docids = find_num_rel(query, qrelsFile)[1]
    # list of first p docs retrieved under query
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    i = 0
    first_p_docs = []
    for line in trec_lines:
        split = line.split()
        if split[0] == query and i < p:
            first_p_docs.append(split[2])
            i += 1
    count = 0
    for doc in first_p_docs:
        if doc in docids:
            count += 1
    trec.close()
    return count / p


# returns recall at rank p
def recall_at_p(query, trecrunFile, qrelsFile, p):
    num_rel = find_num_rel(query, qrelsFile)
    # if numRel is 0, report 0
    if num_rel[0] == 0:
        return 0
    # list of first p docs retrieved under query
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    i = 0
    first_p_docs = []
    for line in trec_lines:
        split = line.split()
        if split[0] == query and i < p:
            first_p_docs.append(split[2])
            i += 1
    count = 0
    for doc in first_p_docs:
        if doc in num_rel[1]:
            count += 1
    trec.close()
    return count / num_rel[0]


# returns f measure at rank p
def f_measure(query, trecrunFile, qrelsFile, p):
    precision = precision_at_p(query, trecrunFile, qrelsFile, p)
    recall = recall_at_p(query, trecrunFile, qrelsFile, p)
    # if precision or recall 0, report 0
    if (precision == 0 or recall == 0):
        return 0
    return (2 * precision * recall)/(precision + recall)


# returns average precision measure
def average_precision(query, trecrunFile, qrelsFile):
    num_rel = find_num_rel(query, qrelsFile)[0]
    if num_rel == 0:
        return 0
    # get list of relevant docs
    relevant = find_num_rel(query, qrelsFile)[1]
    # get list of retrieved docs under query
    trec = open(trecrunFile, 'r')
    trec_lines = trec.readlines()
    positions = []
    for line in trec_lines:
        split = line.split()
        if split[0] == query and split[2] in relevant:
            positions.append(int(split[3]))
    # find average precision across all positions in positions[]
    sum = 0
    for p in positions:
        precision = precision_at_p(query, trecrunFile, qrelsFile, p)
        sum += precision
    trec.close()
    return sum / num_rel


# returns an array: [NDCG@20, numRel, relFound, RR, P@10, R@10, F1@10, AP]
def run_all_evals(query, trecrunFile, qrelsFile):
    ret = []
    ret.append(('NDCG@20', "{:6.4f}".format(get_NDCG(query, trecrunFile, qrelsFile, 20))))
    ret.append(('numRel', find_num_rel(query, qrelsFile)[0]))
    ret.append(('relFound', find_num_rel_found(query, trecrunFile, find_num_rel(query, qrelsFile)[1])[0]))
    ret.append(('RR', "{:6.4f}".format(get_reciprocal_rank(query, trecrunFile, qrelsFile))))
    ret.append(('P@10', "{:6.4f}".format(precision_at_p(query, trecrunFile, qrelsFile, 10))))
    ret.append(('R@10', "{:6.4f}".format(recall_at_p(query, trecrunFile, qrelsFile, 10))))
    ret.append(('F1@10', "{:6.4f}".format(f_measure(query, trecrunFile, qrelsFile, 10))))
    ret.append(('AP', "{:6.4f}".format(average_precision(query, trecrunFile, qrelsFile))))
    return ret
            

if __name__ == '__main__':
    argv_len = len(sys.argv)
    runFile = sys.argv[1] if argv_len >= 2 else "msmarcosmall-bm25.trecrun"
    qrelsFile = sys.argv[2] if argv_len >= 3 else "msmarco.qrels"
    outputFile = sys.argv[3] if argv_len >= 4 else "my-msmarcosmall-bm25.eval"

    eval(runFile, qrelsFile, outputFile)
