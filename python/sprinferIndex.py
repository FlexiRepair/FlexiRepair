from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]
SPINFER_PATH = os.environ["spinfer"]

SPINFER_INDEX_PATH = os.environ["dataset"]
COCCI_PATH = join(os.environ["coccinelle"],'spatch')
DATASET = os.environ["dataset"]
ROOT_DIR = os.environ["ROOT_DIR"]
REDIS_PORT = os.environ["REDIS_PORT"]


def indexCore():

    print(SPINFER_INDEX_PATH)
    # dbDir = join(DATA_PATH, 'redis')
    # startDB(dbDir, "6399", "ALLdumps-gumInput.rdb")
    # import redis
    # redis_db = redis.StrictRedis(host="localhost", port=6399, db=0)
    # keys = redis_db.hkeys("dump")#hkeys "dump"
    # # keys = redis_db.scan(0, match='*', count='1000000')
    #
    # matches = pd.DataFrame(keys, columns=['pairs_key'])
    #
    # # matches = load_zipped_pickle(join(DATA_PATH,'singleHunks'))
    # matches['pairs_key'] = matches['pairs_key'].apply(lambda x: x.decode())
    # matches['root'] = matches['pairs_key'].apply(lambda x: x.split('/')[0])
    # matches['size'] = matches['pairs_key'].apply(lambda x: x.split('/')[1])
    # matches['file'] = matches['pairs_key'].apply(lambda x: x.split('/')[2])
    # matches['hunk'] = matches['pairs_key'].apply(lambda x: x.split('/')[2].split('_')[-1])
    # matches['fileName'] = matches['pairs_key'].apply(lambda x: '_'.join(x.split('/')[2].split('_')[:-1]))
    # test = matches[['fileName', 'hunk']]
    # df = test.groupby(by=['fileName'], as_index=False).agg(lambda x: x.tolist())
    # # sDF = df[df.hunk.apply(lambda x: True if x == ['0'] else False)]
    # sDF = df[df.hunk.apply(lambda x: True if len(x)<10005 else False)]
    # singleHunkedFiles = sDF.fileName.unique().tolist()
    # singleHunkedFiles = [i.replace('.txt', '') for i in singleHunkedFiles]

    clusterPath = join(DATA_PATH, 'actions')
    roots = listdir(clusterPath)
    roots = [i for i in roots if not (i.startswith('.') or i.endswith('.pickle'))]


    for root in roots:
        root
        sizes = listdir(join(clusterPath,root))
        sizes = [f for f in sizes if not f.startswith('.')]
        for size in sizes:

            # actions = listdir(join(clusterPath,root,size))
            # for action in actions:
                clusters = listdir(join(clusterPath,root,size))
                clusters = [f for f in clusters if not f.startswith('.')]
                for cluster in clusters:
                    members = listdir(join(clusterPath,root,size,cluster))
                    members= [f for f in members if not f.startswith('.')]
                    # members = [re.sub('^linux_','',i) for i in members]

                    # csMembers = {}
                    # for j in [i.split('.txt_') for i in members]:
                    #     k,v = j
                    #     k = k +'.txt'
                    #     if k in csMembers:
                    #         tmp = csMembers[k]
                    #         tmp.append(v)
                    #         csMembers[k] = tmp
                    #     else:
                    #         csMembers[k] = [v]
                    #
                    # splitMembers = []
                    # for k,v in csMembers.items():
                    #     hunks = df[df.fileName == k].iloc[0].hunk
                    #     if set(hunks) == set(v):
                    #         splitMembers.append(k)


                    members = [re.sub('\.txt\_\d+','',i) for i in members]
                    members = list(set(members))
                    # members = [i for i in members if i in singleHunkedFiles or i in splitMembers]
                    if len(members) > 1:
                            lines = []
                            for member in members:
                                # project, _, fileName = re.split('_[0-9a-f]{6}', member)
                                # prev, rev = re.findall('[0-9a-f]{6}', member)

                                project, _, fileName = re.split('_[0-9a-f]{6,40}', member, maxsplit=2)
                                prev, rev = re.findall('_[0-9a-f]{6,40}', member)[:2]

                                prev = prev.replace('_', '')
                                rev = rev.replace('_', '')

                                # fileName, hunk = fileName.split('.txt_')
                                # split = dumpFile.split('_')
                                # project = split[0]
                                # filename = "_".join(split[1:-1])
                                filename = prev + '_' + rev + fileName

                                # split =member.split('_')
                                # pj = split[0]
                                # member ='_'.join(split[1:])
                                line = project+'/prevFiles/prev_' + filename + ' ' + project+'/revFiles/' + filename + '\n'
                                lines.append(line)

                            if len(lines)>0:
                                with open(join(SPINFER_INDEX_PATH, root+"_"+size +'_'+cluster+'.index'), 'w', encoding='utf-8') as writeFile:
                                    # if levelPatch == 0:
                                    writeFile.write(''.join(lines))



def test():
    indexes = listdir(SPINFER_INDEX_PATH)
    indexes = [i for i in indexes if i.endswith('.index')]
    coccis = listdir(join(SPINFER_INDEX_PATH,'cocci'))

    if not os.path.exists(join(SPINFER_INDEX_PATH,'indexNC')):
        os.mkdir(join(SPINFER_INDEX_PATH,'indexNC'))

    for i in indexes:
        if re.sub('\.index', '.cocci', i) not in coccis:
            shutil.move(join(SPINFER_INDEX_PATH,i),join(SPINFER_INDEX_PATH,'indexNC',i))


def runSpinfer():
    [os.remove(join(SPINFER_INDEX_PATH, i)) for i in listdir(SPINFER_INDEX_PATH) if i.endswith('.index')]
    indexCore()
    indexes = listdir(SPINFER_INDEX_PATH)
    indexes = [i for i in indexes if i.endswith('.index')]
    # indexes = ['if_9_44.index']
    if not os.path.exists(join(SPINFER_INDEX_PATH,'cocci')):
        os.mkdir(join(SPINFER_INDEX_PATH,'cocci'))
    os.chdir(SPINFER_INDEX_PATH)
    pairs = []
    for i in indexes:
        pairs.append((os.path.getsize(i),i))
    pairs.sort(key=lambda s:s[0])

    coccis = listdir(join(SPINFER_INDEX_PATH,'cocci'))

    cmdList = []
    bigCmdList = []
    for t in pairs:
        sizes, idx = t
        cocciName = re.sub('\.index', '.cocci', idx)
        if cocciName in coccis:
            continue
        # cmd = SPINFER_PATH + " --no-progress -f " + idx + " -o cocci/" + cocciName
        # bigCmdList.append(cmd)
        if sizes < 500:
        #     #cmd = SPINFER_PATH + " -j 16 -f " + idx + " -o cocci/" + re.sub('\.index', '.cocci', idx)
        #     # cmd = SPINFER_PATH + " --no-progress --genericity 1 -j 16 -f " + idx + " -o cocci/" + cocciName
            cmd = SPINFER_PATH + " --no-progress -f " + idx + " -o cocci/" + cocciName
            cmdList.append(cmd)
        else:
        #     # cmd = SPINFER_PATH + " --no-progress --genericity 1 -j 1 -f " + idx + " -o cocci/" + cocciName
            cmd = SPINFER_PATH + " --no-progress -f " + idx + " -o cocci/" + cocciName
            bigCmdList.append(cmd)

    # for cmd in cmdList:
    #     logging.info(cmd)
    #     output, e = shellGitCheckout(cmd)
    #     logging.info(output)
    parallelRun(callSpinfer,cmdList)
    # logging.info('big commands')
    # for cmd in bigCmdList:
    #     #     logging.info(cmd)
    #     #     output, e = shellGitCheckout(cmd)
    #     #     logging.info(output)
    parallelRun(callSpinfer,bigCmdList,max_workers=8)

    # if not os.path.exists(join(DATA_PATH,'cocci')):
    #     os.mkdir(join(DATA_PATH,'cocci'))


        # logging.info(cmd)
        # output,e = shellGitCheckout(cmd)
        # logging.info(output)

def mergeCoccis():
    DATA = DATA_PATH
    folders = os.listdir(DATA)
    coccis = [i for i in folders if 'cocci' in i]

    allCoccis = [get_filepaths(join(DATA, i), '') for i in coccis]

    for cocci in list(itertools.chain.from_iterable(allCoccis)):

        _,srcFolder,cocciName = cocci.split(DATA)[-1].split('/')

        with open(cocci, 'r') as iFile:
            idx = iFile.readlines()
            idx
        values = np.array(idx)
        points = np.where(values == '@@\n')

        points = list(itertools.chain.from_iterable(points))
        # if len(points) == 0:
        #     os.remove(join(SPINFER_INDEX_PATH, 'cocci', cocci))
        # patches = list(zip(*([iter(points)] * 2)))
        patches = list(pairwise(points[::2]))# every second element in list

        if len(patches) > 0:
            i = 0;
            for t in patches :
                t
                with open(join(DATA, 'merged', cocciName+str(i)+'-'+srcFolder), 'w') as iFile:
                    iFile.writelines(idx[t[0]:t[1]])
                i=i+1
            t
            with open(join(DATA, 'merged', cocciName + str(i)+'-'+srcFolder), 'w') as iFile:
                iFile.writelines(idx[t[1]:])
        else:
            shutil.copy2(cocci,join(DATA, 'merged', cocciName + '-'+srcFolder))


def divideCoccis():
    import datetime
    shutil.copytree(join(SPINFER_INDEX_PATH,'cocci'),join(DATA_PATH,'cocci'+ datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))

    coccis =os.listdir(join(SPINFER_INDEX_PATH,'cocci'))
    toDivide = [i for i in coccis if i.endswith('cocci')]
    for cocci in toDivide:
        with open(join(SPINFER_INDEX_PATH,'cocci',cocci), 'r') as iFile:
            idx = iFile.readlines()
            idx
        values = np.array(idx)
        points = np.where(values == '@@\n')

        points = list(itertools.chain.from_iterable(points))
        if len(points) == 0:
            os.remove(join(SPINFER_INDEX_PATH, 'cocci', cocci))
            continue
        # patches = list(zip(*([iter(points)] * 2)))
        patches = list(pairwise(points[::2]))# every second element in list
        existingGenericPatches = [i for i in coccis if i.startswith(cocci)]
        fileNumber = 0
        if len(existingGenericPatches) > 1:
            existingGenericPatches.remove(cocci)
            fileNumber = max([int(re.findall(r".cocci([0-9]+)", i)[0]) for i in existingGenericPatches]) + 1



        if len(patches) > 0:

            i = fileNumber;
            for t in patches :
                t
                with open(join(SPINFER_INDEX_PATH, 'cocci', cocci+str(i)), 'w') as iFile:
                    iFile.writelines(idx[t[0]:t[1]])
                i=i+1
            t
            with open(join(SPINFER_INDEX_PATH, 'cocci', cocci + str(i)), 'w') as iFile:
                iFile.writelines(idx[t[1]:])
            os.remove(join(SPINFER_INDEX_PATH, 'cocci', cocci))
        else:
            os.rename(join(SPINFER_INDEX_PATH, 'cocci', cocci),
                      join(SPINFER_INDEX_PATH, 'cocci', cocci + str(fileNumber)))
            coccis.remove(cocci)
            coccis.append(cocci + str(fileNumber))

def getFreqPatterns():
    patterns = load_zipped_pickle(join(DATA_PATH, 'allCocciPatterns.pickle'))
    freqs = patterns.pattern.value_counts().to_dict()

    allPatterns = patterns.cid.values.tolist()
    uniquePatterns = patterns.drop_duplicates(subset=['pattern']).cid.values.tolist()

    uniquePatterns = patterns[patterns.cid.isin(uniquePatterns)]

    uniquePatterns['newFreq'] = uniquePatterns.pattern.apply(lambda x: freqs[x])

    re.search(r"// Recall:(.*), Precision:(.*), Matching recall:(.*)")



def getPatternTypes():

    if isfile(join(DATA_PATH,'allCocciPatternsLast.pickle')):
        coccis = load_zipped_pickle(join(DATA_PATH,'allCocciPatternsLast.pickle'))
    else:
        commentPattern = r"(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)"
        DATA = join(DATA_PATH,'patches')
        coccis =os.listdir(join(DATA, 'cocci'))
        cocciPatterns = pd.DataFrame(columns=['cid', 'pattern','inferedFrom','recall','precision','matchingRecall'])
        ind = 0
        for cocci in coccis:
            try:
                if cocci == '.DS_Store':
                    continue
                with open(join(DATA, 'cocci', cocci), 'r') as iFile:
                    idx = iFile.read()
                    idx
                    inferedFrom = re.search(r"// Infered from:(.*)\n",idx).groups()
                    recall,precision, matchingRecall = re.search(r"// Recall:(.*), Precision:(.*), Matching recall:(.*)",idx).groups()
                    pattern = re.sub(commentPattern, '', idx, re.DOTALL)
                    cocciPatterns.loc[ind] = [cocci,pattern,inferedFrom,recall.strip(),precision.strip(),matchingRecall.strip()]
                    ind = ind +1
            except Exception as e:
                # shutil.move(join(DATA,'merged',cocci),join(DATA,'mergedBroken',cocci))
                continue
                # logging.error(e)
        cocciPatterns['iFiles'] = cocciPatterns.inferedFrom.apply(lambda x: getInferred(x[0]))

        cocciPatterns['freq'] = cocciPatterns.iFiles.apply(lambda x: len(x))
        cocciPatterns['project'] = cocciPatterns.iFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
        cocciPatterns.sort_values(by='freq', inplace=True, ascending=False)
        # save_zipped_pickle(cocciPatterns,join(DATA_PATH,'allCocciPatterns.pickle'))
        save_zipped_pickle(cocciPatterns,join(DATA_PATH,'allCocciPatternsLast.pickle'))

    coccis

    port = REDIS_PORT
    import redis
    redis_db = redis.StrictRedis(host="localhost", port=port, db=0)

    redis_db

    # def getPatternFromRedis(x):
    #     lines = redis_db.hget(dKey, 'actionTree')



def removeDuplicates2():
    commentPattern = r"(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)"
    DATA = DATA_PATH
    coccis =os.listdir(join(DATA, 'merged'))
    cocciPatterns = pd.DataFrame(columns=['cid', 'pattern','inferedFrom','recall','precision','matchingRecall'])
    ind = 0
    for cocci in coccis:
        try:
            if cocci == '.DS_Store':
                continue
            with open(join(DATA, 'merged', cocci), 'r') as iFile:
                idx = iFile.read()
                idx
                inferedFrom = re.search(r"// Infered from:(.*)\n",idx).groups()
                recall,precision, matchingRecall = re.search(r"// Recall:(.*), Precision:(.*), Matching recall:(.*)",idx).groups()
                pattern = re.sub(commentPattern, '', idx, re.DOTALL)
                cocciPatterns.loc[ind] = [cocci,pattern,inferedFrom,recall.strip(),precision.strip(),matchingRecall.strip()]
                ind = ind +1
        except Exception as e:
            shutil.move(join(DATA,'merged',cocci),join(DATA,'mergedBroken',cocci))
            continue
            # logging.error(e)
    cocciPatterns['iFiles'] = cocciPatterns.inferedFrom.apply(lambda x: getInferred(x[0]))

    cocciPatterns['freq'] = cocciPatterns.iFiles.apply(lambda x: len(x))
    cocciPatterns['project'] = cocciPatterns.iFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
    cocciPatterns.sort_values(by='freq', inplace=True, ascending=False)
    # save_zipped_pickle(cocciPatterns,join(DATA_PATH,'allCocciPatterns.pickle'))
    save_zipped_pickle(cocciPatterns,join(DATA,'allCocciPatternsMerge.pickle'))

    cocciPatterns['dup'] = cocciPatterns.duplicated(subset=['pattern'], keep=False)

    duplicates = cocciPatterns[cocciPatterns.dup == True]

    duplicateDF = duplicates.groupby(by=['pattern'], as_index=False).agg(lambda x: x.tolist())

    pattern2keep= duplicateDF.cid.apply(lambda x: min(x, key=len)).values.tolist()
    allDuplicates = list(itertools.chain.from_iterable(duplicateDF.cid.values.tolist()))

    toRemove = list(set(allDuplicates).difference(set(pattern2keep)))

    for tr in toRemove:
        shutil.move(join(DATA,'merged',tr),join(DATA,'mergedDuplicate',tr))

    # allPatterns = cocciPatterns.cid.values.tolist()
    # uniquePatterns = cocciPatterns.drop_duplicates(subset=['pattern']).cid.values.tolist()
    # toRemove = list(set(allPatterns).difference(uniquePatterns))
    # print(toRemove)
    # for p in toRemove:
    #     os.remove(join(SPINFER_INDEX_PATH, 'cocci', p))
    # print(len(uniquePatterns))

def removeDuplicates():

    commentPattern = r"(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)"
    coccis =os.listdir(join(SPINFER_INDEX_PATH, 'cocci'))
    cocciPatterns = pd.DataFrame(columns=['cid', 'pattern','inferedFrom','recall','precision','matchingRecall'])
    ind = 0
    for cocci in coccis:
        if cocci == '.DS_Store':
            continue
        with open(join(SPINFER_INDEX_PATH, 'cocci', cocci), 'r') as iFile:
            idx = iFile.read()
            idx
            inferedFrom = re.search(r"// Infered from:(.*)\n",idx).groups()
            recall,precision, matchingRecall = re.search(r"// Recall:(.*), Precision:(.*), Matching recall:(.*)",idx).groups()
            pattern = re.sub(commentPattern, '', idx, re.DOTALL)
            cocciPatterns.loc[ind] = [cocci,pattern,inferedFrom,recall.strip(),precision.strip(),matchingRecall.strip()]
            ind = ind +1
    cocciPatterns['iFiles'] = cocciPatterns.inferedFrom.apply(lambda x: getInferred(x[0]))

    cocciPatterns['freq'] = cocciPatterns.iFiles.apply(lambda x: len(x))
    cocciPatterns['project'] = cocciPatterns.iFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
    cocciPatterns.sort_values(by='freq', inplace=True, ascending=False)

    uPatterns = cocciPatterns.groupby(by=['pattern'], as_index=False).agg(lambda x: x.tolist())
    # uPatterns['uid'] = uPatterns.cid.apply(lambda x: min(x, key=len))
    uPatterns['uid'] = uPatterns.cid.apply(lambda x: [i for i in x if i.endswith( '.cocci'+str(min([int(re.findall(r".cocci([0-9]+)", i)[0]) for i in x])))][0])
    uPatterns['uFiles'] = uPatterns.iFiles.apply(lambda x: list(set(itertools.chain.from_iterable(x))))
    uPatterns['uFreq'] = uPatterns.uFiles.apply(lambda x: len(x))
    uPatterns['uProjects'] = uPatterns.uFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
    uPatterns['allProjects'] = uPatterns.uFiles.apply(lambda x: list([i.split('/{')[0].replace('(', '') for i in x]))

    uPatterns.sort_values(by='uFreq', inplace=True, ascending=False)


    uPatterns.uFiles.apply(lambda x: len(set([i.split(':')[-1] for i in x])))
    uPatterns['uFilenames'] = uPatterns.uFiles.apply(
        lambda x: len(set([re.split('_[0-9a-f]{6,40}', i.split(',')[0])[-1] for i in x])))
    uPatterns['uFunction'] = uPatterns.uFiles.apply(lambda x: len(set([i.split(':')[-1] for i in x])))
    uPatterns['uPatch'] = uPatterns.uFiles.apply(
        lambda x:
        len(set(
            [i.split('/{')[0].replace('(', '') + ''.join(re.findall('_[0-9a-f]{6,40}', i.split(',')[0])) for i
             in x])))
    uPatterns['uProject'] = uPatterns.uFiles.apply(
        lambda x:
        len(set(
            [i.split('/{')[0].replace('(', '') for i
             in x])))


    # save_zipped_pickle(cocciPatterns,join(DATA_PATH,'allCocciPatterns.pickle'))
    save_zipped_pickle(cocciPatterns,join(DATA_PATH,'allCocciPatterns.pickle'))
    save_zipped_pickle(uPatterns,join(DATA_PATH,'uPatterns.pickle'))

    duplicatedPatterns = list(itertools.chain.from_iterable(uPatterns[uPatterns.cid.apply(lambda x: len(x) > 1)].cid.values.tolist()))
    removeDups = [i for i in duplicatedPatterns if i not in uPatterns.uid.values.tolist()]
    print("{} duplicated generic pathes to remove ".format(str(len(removeDups))))
    for i in removeDups:
        os.remove(join(SPINFER_INDEX_PATH, 'cocci', i))



def filterPatterns():
    cocciPatterns = load_zipped_pickle(join(DATA_PATH,'allCocciPatterns.pickle'))
    cocciPatterns['filtered'] = cocciPatterns.iFiles.apply(lambda x: [i for i in x if  (
                i.startswith('(libtiff') or i.startswith('(php-src') or i.startswith('(cpython'))])
    return cocciPatterns[cocciPatterns.filtered.str.len() > 0].cid.values.tolist()

def getInferred(x):
    regex = r"\(.*?\)"
    matches = re.finditer(regex, x)

    results = []
    for matchNum, match in enumerate(matches, start=1):
        results.append(match.group())
    return results


def getNegLines(x):
    negLines = r"^-(.*)"
    matches = re.finditer(negLines, x, re.MULTILINE)
    res = []
    for matchNum, match in enumerate(matches, start=1):

        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            res.append(match.group(groupNum))
    from common.preprocessing import getTokensForPatterns
    tokens = getTokensForPatterns(res)

    return tokens
def patternOperations():
    cocciPatterns = load_zipped_pickle(join(DATA_PATH, 'allCocciPatterns.pickle'))
    # cocciPatterns.pattern.apply(lambda x:re.search(r"@@(.*)@@",x,re.DOTALL|re.M).groups())
    cocciPatterns['patternTokens'] = cocciPatterns.pattern.apply(lambda x:getNegLines(x))
    #set(getTokensForPatterns(lines)).intersection(set(tokens))
    save_zipped_pickle(cocciPatterns,join(DATA_PATH, 'allCocciPatterns.pickle'))


def filterCore(t):
    # cocciPatterns = load_zipped_pickle(join(DATA_PATH, 'allCocciPatterns.pickle'))
    src,spfile = t
    srcPath = src
    patchName = src.split('/')[-1]
    manybug = src.split('/')[-2]
    # with open(srcPath, mode='r') as srcFile:
    #     lines = srcFile.read()
    # scTokens = getTokensForPatterns(lines)

    # tokens = cocciPatterns[cocciPatterns.cid == spfile].iloc[0].patternTokens
    # patternFilter = set(scTokens).intersection(set(tokens))
    # if len(patternFilter) > 0:
    cmd = COCCI_PATH + ' --sp-file ' + join(DATASET, 'cocci', spfile) + ' ' + srcPath + ' --patch -o' + join(
        DATA_PATH, "introclass", manybug, 'patches', patchName) + ' > ' + join(DATA_PATH, "introclass", manybug,
                                                                               'patches',
                                                                               patchName + spfile + '.txt')
    # cmd = COCCI_PATH + ' --sp-file ' + join(DATASET,'cocci',spfile) + ' ' + srcPath + ' -o ' + join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt')
    t = cmd, manybug, patchName, spfile, srcPath
    return t
    # return None


def patchCoreIntro():


    manybugs = listdir(join(DATA_PATH,"introclass"))
    spfiles = listdir(join(DATASET,'cocci'))
    # workList = []



    filterList =[]
    for manybug in manybugs:
        if manybug == '.DS_Store':
            continue
        # files = listdir(join(join(DATA_PATH,"manybugs",manybug,'diffs')))
        if  os.path.exists(join(DATA_PATH, "introclass", manybug, 'patches')):
            shutil.rmtree(join(DATA_PATH, "introclass", manybug, 'patches'))

            os.mkdir(join(DATA_PATH, "introclass", manybug, 'patches'))
        else:
            os.mkdir(join(DATA_PATH, "introclass", manybug, 'patches'))

        if  os.path.exists(join(DATA_PATH, "introclass", manybug, 'patched')):
            shutil.rmtree(join(DATA_PATH, "introclass", manybug, 'patched'))

            os.mkdir(join(DATA_PATH, "introclass", manybug, 'patched'))
        else:
            os.mkdir(join(DATA_PATH, "introclass", manybug, 'patched'))

        files = get_filepaths(join(DATA_PATH, "introclass", manybug), '.c')
        sources = [i for i in files if not (i.endswith('oracle.c.patch') or i.endswith('oracle.c'))]

        filterList.extend(list(itertools.product(sources, spfiles)))
    print(len(filterList))
    workList = parallelRunMerge(filterCore,filterList)


    workList = list(filter(None, workList))
    print(len(workList))
    # for l in workList:
    #     cocciCore2(l)
    parallelRun(cocciCore2,workList)

def patched():
    manybugs = listdir(join(DATA_PATH,"introclass"))
    # spfiles = listdir(join(DATASET,'cocci'))
    workList = []
    for manybug in manybugs:
        # files = listdir(join(join(DATA_PATH,"manybugs",manybug,'diffs')))
        if  os.path.exists(join(DATA_PATH, "introclass_patched", manybug, 'patches')):
            shutil.rmtree(join(DATA_PATH, "introclass_patched", manybug, 'patches'))

            os.makedirs(join(DATA_PATH, "introclass_patched", manybug, 'patches'))
        else:
            os.makedirs(join(DATA_PATH, "introclass_patched", manybug, 'patches'))
        files = get_filepaths(join(DATA_PATH, "introclass", manybug), '.c')
        sources = [i for i in files if not (i.endswith('oracle.c.patch') or i.endswith('oracle.c'))]


        for src in sources:
            # srcPath = src.replace('/diffs/','/src/')
            srcPath = src
            patchName = src.split('/')[-1]


            spfiles = listdir(join(DATA_PATH,"introclass",manybug,'patches'))
            for spfile in spfiles:
                 spfile =spfile.replace(patchName,'').replace('.txt','')
                 cmd = COCCI_PATH + ' --sp-file ' + join(DATASET,'cocci',spfile) + ' ' + srcPath + ' -o ' + join(DATA_PATH,"introclass_patched",manybug,'patches',patchName+spfile+'.c')
                 t = cmd,manybug,patchName,spfile
                 workList.append(t)
    parallelRun(cocciCore,workList)



def cocciCore2(t):
    cmd,manybug,patchName,spfile,srcPath = t
    # cocciPatterns = load_zipped_pickle(join(DATA_PATH, 'allCocciPatterns.pickle'))
    # tokens = cocciPatterns[cocciPatterns.cid == spfile].iloc[0].patternTokens
    # with open(srcPath, mode='r') as srcFile:
    #     lines = srcFile.read()

    # patternFilter = set(getTokensForPatterns(lines)).intersection(set(tokens))
    # if len(patternFilter) > 0:

    # logging.info(cmd)
    output, e = shellGitCheckout(cmd)
    # logging.info(output)
    patchSize = os.path.getsize(join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt'))
    if patchSize == 0 :
        os.remove(join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt'))
    else:
        cmd = 'patch -d '+join(DATA_PATH, "introclass", manybug)+' -i '+join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt')+' -o '+join(DATA_PATH,"introclass",manybug,'patched',patchName+spfile+'.c')
        o,e = shellGitCheckout(cmd)

def cocciCore(t):
    cmd, manybug, patchName, spfile = t
    # logging.info(cmd)
    output, e = shellGitCheckout(cmd)
    # logging.info(output)
    patchSize = os.path.getsize(join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt'))
    if patchSize == 0 :
     os.remove(join(DATA_PATH,"introclass",manybug,'patches',patchName+spfile+'.txt'))


