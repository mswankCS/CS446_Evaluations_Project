def make_table(qlFile, bm25File, dprFile, outputFile):
    ql = open(qlFile, 'r')
    bm25 = open(bm25File, 'r')
    dpr = open(dprFile, 'r')

    ql_lines = ql.readlines()
    bm25_lines = bm25.readlines()
    dpr_lines = dpr.readlines()

    queries = []
    ql_vals = []
    bm25_vals = []
    dpr_vals = []

    for line in ql_lines:
        split = line.split()
        if split[0] == 'AP':
            queries.append(split[1])
            ql_vals.append(float(split[2]))
    
    for line in bm25_lines:
        split = line.split()
        if split[0] == 'AP':
            bm25_vals.append(float(split[2]))

    for line in dpr_lines:
        split = line.split()
        if split[0] == 'AP':
            dpr_vals.append(float(split[2]))

    ql.close()
    bm25.close()
    dpr.close()

    percent_inc_ql_to_bm25 = []
    percent_inc_ql_to_dpr = []

    for i in range(len(queries)):
        if (ql_vals[i] == 0):
            percent_inc_ql_to_bm25.append(0)
            percent_inc_ql_to_dpr.append(0)
        else:
            percent_inc_ql_to_bm25.append((bm25_vals[i] - ql_vals[i]) / ql_vals[i] * 100)
            percent_inc_ql_to_dpr.append((dpr_vals[i] - ql_vals[i]) / ql_vals[i] * 100)

    out = open(outputFile, 'w+')
    
    column_names = ['Query', '  QL  ', ' BM25 ', '  -  ', '  DPR ', '  -  ']
    for name in column_names:
        out.write(name)
        out.write('  ')
    out.write('\n')

    for i in range(len(queries)):
        out.write(f"{queries[i]:<s}")
        out.write('  ')
        out.write(f"{ql_vals[i]:<6.4f}")
        out.write('  ')
        out.write(f"{bm25_vals[i]:<6.4f}")
        out.write('  ')
        out.write(f"{percent_inc_ql_to_bm25[i]:<5.1f}")
        out.write('%')
        out.write('  ')
        out.write(f"{dpr_vals[i]:<6.4f}")
        out.write('  ')
        out.write(f"{percent_inc_ql_to_dpr[i]:<5.1f}")
        out.write('%')
        out.write('\n')

    out.close()


if __name__ == '__main__':
    make_table('../ql.eval', '../bm25.eval', '../dpr.eval', '../table.md')
    print("Success")