from common.commons import *





if __name__ == '__main__':


    try:
        args = getRun()
        setLogg()


        setEnv(args)

        job = args.job

        ROOT_DIR = os.environ["ROOT_DIR"]
        REPO_PATH = os.environ["REPO_PATH"]
        CODE_PATH = os.environ["CODE_PATH"]
        DATA_PATH = os.environ["DATA_PATH"]
        COMMIT_DFS = os.environ["COMMIT_DFS"]
        BUG_POINT = os.environ["BUG_POINT"]
        COMMIT_FOLDER = os.environ["COMMIT_FOLDER"]
        FEATURE_DIR = os.environ["FEATURE_DIR"]
        DATASET_DIR = os.environ["DATASET_DIR"]
        PROJECT_TYPE = os.environ["PROJECT_TYPE"]
        REDIS_PORT = os.environ["REDIS_PORT"]
        jdk8 = os.environ["JDK8"]
        pd.options.mode.chained_assignment = None



        print(job)


        if job =='miner':
            print('Cloning repositories')
            from otherDatasets import core
            core()

        # elif job =='richedit':
            print('Mining')
            dbDir = join(DATA_PATH, 'redis')
            stopDB(dbDir, REDIS_PORT)

            cmd = 'bash ' + join(ROOT_DIR,'data' , 'runJava.sh') + ' {} {} {} '.format(join(Path(ROOT_DIR).parent, 'target','FlexiRepair-1.0.0-jar-with-dependencies.jar'),args.prop,"RICHEDITSCRIPT")

            logging.info(cmd)
            os.system(cmd)

            print('Indexing')
        # elif job =='actionSI':
            from pairs import actionPairs
            matches = actionPairs()

            from pairs import createPairs
            createPairs(matches)

            from pairs import importAction
            importAction()
            print('Clustering')
        # elif job =='compare':

            cmd = 'bash ' + join(ROOT_DIR,'data' , 'runJava.sh') + ' {} {} {} '.format(join(Path(ROOT_DIR).parent, 'target','FlexiRepair-1.0.0-jar-with-dependencies.jar'),args.prop,"COMPARE")
            logging.info(cmd)
            os.system(cmd)


        # elif job == 'cluster':
            from abstractPatch import cluster

            dbDir = join(ROOT_DIR,'data','redis')
            startDB(dbDir, REDIS_PORT, PROJECT_TYPE)
            cluster(join(DATA_PATH,'actions'),join(DATA_PATH, 'pairs'),'actions')


        elif job =='inferrer':
            from sprinferIndex import runSpinfer
            runSpinfer()

            from sprinferIndex import divideCoccis
            divideCoccis()
            from sprinferIndex import removeDuplicates
            removeDuplicates()

        elif job == 'validateCodeFlaws':
            from validateCodeFlaws import validate
            validate()

        elif job =='patchIntro':
            from sprinferIndex import patchCoreIntro
            patchCoreIntro()
            # from sprinferIndex import patched
            # patched()

        elif job =='validateIntro':
            # from patch_validate_introClass2 import patch_validate
            # patch_validate()
            from test_patched_file import patch_validate
            patch_validate()
        elif job =='checkCorrectIntro':
            from test_patched_file import checkCorrect
            checkCorrect()


        elif job == 'introclass':
            from getIntroClass import export
            export()

        elif job =='stats':
            from stats import statsNormal
            statsNormal(True)

        elif job == 'patterns':

            from stats import exportAbstractPatterns
            exportAbstractPatterns()
        else:
            logging.error('Unknown job %s',job)
    except Exception as e:
        logging.error(e)
