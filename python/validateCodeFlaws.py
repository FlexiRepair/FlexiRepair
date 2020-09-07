import os
from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]
ROOT_DIR = os.environ["ROOT_DIR"]
DATASET = os.environ["dataset"]
COCCI_PATH = join(os.environ["coccinelle"],'spatch')
CODEFLAWS_PATH = os.environ["CODEFLAWS_PATH"]

VALID_LIST = os.environ["VALID_LIST"]
VALID_TYPE = os.environ["VALID_TYPE"]
PRIORITIZION = os.environ["PRIORITIZION"]
def patchSourceFile(bugPath,spfile,bugName):

    srcPath = bugPath
    patchName = bugName

    if(isfile(join(CODEFLAWS_PATH,bugName,'patched',patchName+spfile+'.c'))):
        return join(CODEFLAWS_PATH,bugName,'patched',patchName+spfile+'.c')

    if not (isfile(join(CODEFLAWS_PATH,bugName,'patches',patchName+spfile+'.txt'))):
        cmd = COCCI_PATH + ' --sp-file ' + join(DATASET, 'cocci', spfile) + ' ' + srcPath + ' --patch -o' + join(
            CODEFLAWS_PATH, bugName, 'patches', patchName) + ' > ' + join(CODEFLAWS_PATH, bugName,
                                                                                   'patches',
                                                                                   patchName + spfile + '.txt')

        output, e = shellGitCheckout(cmd)
    # logging.info(output)
    patchSize = os.path.getsize(join(CODEFLAWS_PATH,bugName,'patches',patchName+spfile+'.txt'))
    if patchSize == 0 :
        # os.remove(join(DATA_PATH,"introclass",bugName,'patches',patchName+spfile+'.txt'))
        return None
    else:

        cmd = 'patch -d '+'/'.join(srcPath.split('/')[:-1])+' -i '+join(CODEFLAWS_PATH,bugName,'patches',patchName+spfile+'.txt')+' -o '+join(CODEFLAWS_PATH,bugName,'patched',patchName+spfile+'.c')
        o,e = shellGitCheckout(cmd)
        return join(CODEFLAWS_PATH, bugName, 'patched', patchName + spfile + '.c')

def getTestList(path,isHeldout):
    files = listdir(path)
    #
    if isHeldout:
        inputs = [i for i in files if i.startswith('heldout-input-')]
    else:
        inputs = [i for i in files if i.startswith('input-')]
    return inputs


def readTestSuite(testPath):
    regex = r"([p|n0-9]+)\)"
    with open(testPath,mode='r') as testFile:
        test_str = testFile.read()
    matches = re.finditer(regex, test_str, re.MULTILINE)

    testList = []
    for matchNum, match in enumerate(matches, start=1):

         for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            testList.append(match.group(groupNum))
    return testList

def test_all(testerPath,validTests,testPath):

    failure_cases = []
    failure = 0
    total = len(validTests)
    #remove prev outputs
    [os.remove(join(testPath, i)) for i in listdir(testPath) if i.endswith('my_output')]
    for test in validTests:

        outpos = test.replace('input-','output-')

        cmd = 'bash ' + join(ROOT_DIR,'data' , 'test-valid2.sh') + ' {} {} {} {} '.format(join(testPath, test),
                                                                              join(testPath, outpos), testerPath, join(testPath,'time.out'))
        out,e = shellGitCheckout(cmd)


        if 'Accepted' not in out or e != '':
            failure += 1
            failure_cases.append(test)
            break

    return failure_cases, failure, total

def validateCore(t):
    bugName,isHeldout,prioritize = t

    if not os.path.exists(join(CODEFLAWS_PATH, bugName, 'patches')):
        os.makedirs(join(CODEFLAWS_PATH, bugName, 'patches'))
    if not os.path.exists(join(CODEFLAWS_PATH, bugName, 'patched')):
        os.makedirs(join(CODEFLAWS_PATH, bugName, 'patched'))

    fix = 'failure'
    output = ''

    output += 'bugName:' + bugName + ', '

    spfiles = load_zipped_pickle(join(DATA_PATH, 'uPatterns.pickle'))

    spfiles['uProjects'] = spfiles.uFiles.apply(lambda x: list(set([i.split('/{')[0].replace('(','') for i in x])))
    spfiles = spfiles[~spfiles.uProjects.apply(lambda x: np.all([i == 'codeflaws' for i in x]))]

    spfiles.sort_values(by=prioritize,inplace=True,ascending=False)
    spfiles = spfiles[['uid']]

    cmd = 'make -C ' + join(CODEFLAWS_PATH, bugName) + ' clean'
    o, e = shellGitCheckout(cmd)

    contestid, problem, _, buggyId, acceptedId = bugName.split('-')


    for idx, spfile in enumerate(spfiles.uid.values.tolist()):
        if spfile == '.DS_Store':
            continue

        buggyFileName = contestid+'-'+problem+'-'+buggyId+'.c'
        path = join(DATA_PATH,'codeflaws',bugName,buggyFileName)
        patch = patchSourceFile(path, spfile, bugName)

        times = 0
        if patch is None:
            continue

        shutil.copy2(patch,join(CODEFLAWS_PATH, bugName))

        cmd = 'make -C ' + join(CODEFLAWS_PATH, bugName) + ' FILENAME=' + bugName + spfile
        o, e = shellGitCheckout(cmd)

        if isfile(join(DATA_PATH,'codeflaws',bugName,bugName+spfile)):

            cmd = 'mv ' + join(DATA_PATH,'codeflaws',bugName,bugName+spfile) + ' ' + join(DATA_PATH,'codeflaws',bugName,contestid+'-'+problem+'-'+buggyId)
            o, e = shellGitCheckout(cmd)

            output += '@True:' + str(idx) + ':' + patch.split('/')[-1] + '@'
            validTests = getTestList(join(CODEFLAWS_PATH, bugName),isHeldout)

            post_failure_cases, post_failure, total = test_all(join(CODEFLAWS_PATH, bugName, contestid+'-'+problem+'-'+buggyId), validTests, join(CODEFLAWS_PATH, bugName))

            output += str(post_failure) + ' '
            if post_failure == 0:
                times += 1
                fix = 'success'
                output += 'fix {} by {} '.format(bugName, patch)
                break

    output += 'times:{}, '.format(times) + fix
    # print(output)
    return output


def validate():

     bugs2test= listdir(CODEFLAWS_PATH)
     bugs2test.sort()


     isHeldout = True
     if VALID_TYPE == 'black':
         isHeldout = False
     validList = VALID_LIST.split(',')



     prioritize = ''
     if PRIORITIZION == 'project':
         prioritize = 'uProject'
     elif PRIORITIZION == 'patch':
         prioritize = 'uPatch'
     elif PRIORITIZION == 'file':
         prioritize = 'uFilenames'
     elif PRIORITIZION == 'function':
         prioritize = 'uFunction'
     elif PRIORITIZION == 'hunk':
         prioritize = 'uFreq'
     else:
        raise Exception("Unknown PRIORITIZION " +PRIORITIZION)
        return

     bugList = []
     if(validList == ['ALL']):
         for b in bugs2test:
             if b == '.DS_Store' or b == 'README.md' or b.endswith('.txt') or b.endswith('.tar.gz'):
                 continue
             t = b,isHeldout,prioritize
             bugList.append(t)
     else:
         for b in bugs2test:
             if b == '.DS_Store' or b == 'README.md' or b.endswith('.txt') or b.endswith('.tar.gz'):
                 continue
             if b not in validList:
                 continue
             t = b,isHeldout,prioritize
             bugList.append(t)

     # results = parallelRunMerge(testCore, bugList,max_workers=10)
     results = parallelRunMerge(validateCore, bugList)
     print('\n'.join(results))
     print('Validation results save to :' + join(DATA_PATH, 'codeFlawsResults'+PRIORITIZION+VALID_TYPE))
     with open(join(DATA_PATH, 'codeFlawsResults'+PRIORITIZION+VALID_TYPE), 'w',
               encoding='utf-8') as writeFile:
         writeFile.write('\n'.join(results))
