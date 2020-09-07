from common.commons import *
DATA_PATH = os.environ["DATA_PATH"]
PROJECT_TYPE = os.environ["PROJECT_TYPE"]
REDIS_PORT = os.environ["REDIS_PORT"]
ROOT = os.environ["ROOT_DIR"]
INNER_DATA_PATH = join(ROOT,'data')

def statsNormal(isMiner=True):
    # tokens = join(DATA_PATH, 'tokens')
    # actions = join(DATA_PATH, 'actions')
    # import redis
    # redis_db = redis.StrictRedis(host="localhost", port=REDIS_PORT, db=0)
    # # keys = redis_db.scan(0, match='*', count='1000000')
    # keys = redis_db.hkeys("dump")  # hkeys "dump"
    # matches = pd.DataFrame(keys, columns=['pairs_key'])
    matches = load_zipped_pickle(join(DATA_PATH,'matches.pickle'))
    # matches = load_zipped_pickle(join(DATA_PATH,'singleHunks'))
    matches['pairs_key'] = matches['pairs_key'].apply(lambda x: x.decode())
    matches['root'] = matches['pairs_key'].apply(lambda x: x.split('/')[0])
    matches['size'] = matches['pairs_key'].apply(lambda x: x.split('/')[1])
    matches['file'] = matches['pairs_key'].apply(lambda x: x.split('/')[2])
    # matches['repo'] = matches['file'].apply(lambda x: x.split('_')[0])
    matches['repo'] = matches['file'].apply(lambda x: re.split('_[0-9a-f]{6,40}',x)[0])
    # matches['commit'] = matches['file'].apply(lambda x: x.split('_')[1])
    matches['commit'] = matches['file'].apply(lambda x: re.findall('_[0-9a-f]{6,40}',x)[0].replace('_',''))
    matches['hunk'] = matches['pairs_key'].apply(lambda x: x.split('/')[2].split('_')[-1])
    matches['fileName'] = matches['pairs_key'].apply(lambda x: '_'.join(x.split('/')[2].split('_')[:-1]))
    test = matches[['fileName','hunk']]
    df = test.groupby(by=['fileName'], as_index=False).agg(lambda x: x.tolist())

    # df = load_zipped_pickle('datasetGroupByHunk.pickle')
    yList = []
    colNames = []

    def haveAll(x):
        check = dict()
        if len(x)<2:
            return False
        for hunk in x:
            filename, hunkNo = hunk.rsplit('_',1)
            if filename in check:
                check[filename].append(hunkNo)
            else:
                check[filename] = [hunkNo]

        tv = []
        for k,v in check.items():
            selected = df[df.fileName == k]
            if tuple(selected.iloc[0].hunk) == tuple(v):
                tv.append(True)
            else:
                tv.append(False)
        result = np.all(tv)
        return result

    def combinationOfPatterns(x):
        check = dict()
        if len(x)<2:
            return False
        for hunk in x:
            filename, hunkNo = hunk.rsplit('_',1)
            if filename in check:
                check[filename].append(hunkNo)
            else:
                check[filename] = [hunkNo]

        tv = []

        res = check.copy()
        for k,v in check.items():
            # if len(v) == 1:
            #     res.pop(k,None)
            selected = df[df.fileName == k]
            if set(selected.iloc[0].hunk) != set(v):
                res.pop(k, None)
        # result = np.all(tv)
        indices = [i for i, val in enumerate(tv) if val == True]
        return res
    allHunks = []
    def test(x):
        try:
            fileList = []
            for i in x:

                fileName = i.rsplit('_', 1)[0]

                if fileName in byCombi.keys():
                    fileList.append(i)
            if len(fileList) > 0:

                if (set(fileList).issubset(set(x))):
                    # logging.info("In the same pattern")
                    allHunks.extend(fileList)
                    return True
                else:
                  logging.info("Mix")
            return False
        except Exception as e:
            logging.error(e)


    # for type in ['tokens', 'actions', 'shapes']:
    for type in ['actions']:
        statsS,clusterDF = stats(type,isMiner)
        if isMiner:
            clusterDF = clusterDF[clusterDF.members.str.len() > 1]

            clusterDF['vertical'] = clusterDF.members.apply(lambda x:len(set([i.rsplit('_',1)[0] for i in x])) == 1)
            clusterDF['v-h'] = clusterDF.members.apply(lambda x: len(set([i.rsplit('_', 1)[0] for i in x])))
            clusterDF['ms'] = clusterDF.members.apply(lambda x: len(x))
            clusterDF['horizontal'] = clusterDF.apply(lambda x: x['ms'] == x['v-h'] and x['v-h'] > 1, axis=1)



            logging.info('Spread horizontal %d vertical %d',len(clusterDF[clusterDF['horizontal'] == True]),  len(clusterDF[clusterDF['vertical'] == True]))
            logging.info('Spread patch horizontal %d vertical %d',clusterDF[clusterDF['horizontal'] == True]['v-h'].sum(),  clusterDF[clusterDF['vertical'] == True]['v-h'].sum())
            logging.info('Spread hunks horizontal %d vertical %d',clusterDF[clusterDF['horizontal'] == True]['ms'].sum(),  clusterDF[clusterDF['vertical'] == True]['ms'].sum())

        singlePatternAll= clusterDF[clusterDF.members.apply(lambda x:haveAll(x))]
        singlePatterns = list(set(singlePatternAll.cid.values.tolist()))

        # if type == 'actions':
        #     print('\n'.join(singlePatterns))
        hunks = set(itertools.chain.from_iterable(singlePatternAll.members.values.tolist()))
        logging.info("Match every member Fix\n %s # bugs: %d , # hunks %d ,#patterns %d", type,len(set([re.split('.txt_[0-9]+', i)[0] for i in hunks])),
                     len(hunks),
                     len(singlePatternAll))
        # nonEmpty = clusterDF[clusterDF.members.str.len() > 1]
        allhunks =set(itertools.chain.from_iterable(clusterDF.members.values.tolist()))
        byCombi = combinationOfPatterns(allhunks)


        multiple =clusterDF[clusterDF.members.apply(lambda x:test(x))]
        # print(len(multiple))
        # print(set(multiple.cid.values.tolist()).difference(singlePatterns))

        allHunks
        logging.info("%d patterns can match %d bugs, %d hunks",len(multiple),len(set([re.split('.txt_[0-9]+', i)[0] for i in allHunks])), len(allHunks))
        matches = pd.DataFrame(statsS, columns=['cluster', 'memberCount'])
        matches.sort_values(by='memberCount', ascending=False, inplace=True)
        matches
        if isMiner:
            matches.to_csv(join(DATA_PATH, "stats" + type + ".csv"), index=False)









        else:
            matches.to_csv(join(DATA_PATH, "statsDefects4J" + type + ".csv"), index=False)
        print(type, matches.memberCount.sum())
        print(type, matches.memberCount.sum())
        yList.append(matches.memberCount.values.tolist())
        colNames.append(type)
    # if isMiner:
    #     from common.commons import plotBox
    #     plotBox(yList,colNames,'dist_clusterMembers.pdf',False,False)
    # for i in range(2, 21):
    #     print('%d %d %d' % (matches[matches.memberCount >= i].memberCount.sum(), len(matches[matches.memberCount >= i]),i))

    # save_zipped_pickle(join(DATA_PATH,'statsShapes'))

idx = 0
def stats(type,isMiner=True):
    clustersDF = pd.DataFrame(columns=['cid', 'type', 'members'])


    shapesPath = join(DATA_PATH, type)
    shapes = listdir(shapesPath)
    shapes = [f for f in shapes if isdir(join(shapesPath, f))]
    shape = size = cluster = action = token = None

    def statsCore(cs):
        global idx
        if isMiner:
            cs = [i for i in cs if not (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith(
                'jfreechart'))]
        else:
            cs = [i for i in cs if (
                    i.startswith('commons-math') or i.startswith('commons-lang') or i.startswith(
                'closure-compiler') or i.startswith('joda-time') or i.startswith('mockito') or i.startswith(
                'jfreechart'))]
        if size == '1':
            return
        # print('Cluster %s : member size %s' % (shape+"-"+size +"-"+cluster, len(cs)))
        clusterSize = len(cs)
        if token is None:
            if action is None:
                # clusterSize = len(cs)
                # if clusterSize > 1:
                #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                t = shape + "-" + size + "-" + cluster, clusterSize
                clustersDF.loc[idx] = [t, type, cs]
                idx = idx + 1
            else:
                # clusterSize = len(cs)
                # if clusterSize > 1:
                #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
                t = shape + "-" + size + "-" + cluster + "-" + action, clusterSize
                clustersDF.loc[idx] = [t, type, cs]
                idx = idx + 1
        else:
            # clusterSize = len(cs)
            # if clusterSize > 1:
            #     clusterSize = len(set([re.split('.txt_[0-9]+', i)[0] for i in cs]))
            t = shape + "-" + size + "-" + cluster + "-" + action + "-" + token, clusterSize
            clustersDF.loc[idx] = [t, type, cs]
            idx = idx + 1
        # t = shape + "-" + size + "-" + cluster, len(cs)
        # if len(cs)>0:
        #     with open(join(shapesPath,t[0].replace('-','/'),cs[0]),'r') as pattern:
        #         line = pattern.read()
        #         if line.startswith('MOV') or line.startswith('DEL'):
        #             t = t[0],0
        if isMiner:
            if clusterSize > 1:
                statsS.append(t)
        else:
            if clusterSize > 0:
                statsS.append(t)

    statsS = []
    for shape in shapes:
        if shape.startswith('.'):
            continue
        sizes = listdir(join(shapesPath, shape))
        logging.debug(shape + ":" + str(len(sizes)))

        for size in sizes:
            if size.startswith('.'):
                continue
            clusters = listdir(join(shapesPath, shape, size))
            for cluster in clusters:
                if cluster.startswith('.'):
                    continue
                cs = listdir(join(shapesPath, shape, size, cluster))

                if shapesPath.endswith('actions'):
                    cs = listdir(join(shapesPath, shape, size, cluster))
                    statsCore(cs)
                else:
                    # level3
                    for action in cs:
                        if action.startswith('.'):
                            continue
                        tokens = listdir(join(shapesPath, shape, size, cluster, action))
                        if shapesPath.endswith('tokens'):
                            statsCore(tokens)
                        # else:
                        #     for token in tokens:
                        #         if token.startswith('.'):
                        #             continue
                        #         cs = listdir(join(shapesPath, shape, size, cluster, action, token))
                        #         statsCore(cs)
    return statsS,clustersDF



javaAst = ["AnonymousClassDeclaration", "ArrayAccess", "ArrayCreation", "ArrayInitializer", "ArrayType", "AssertStatement",
       "Assignment", "Block", "BooleanLiteral", "BreakStatement", "CastExpression", "CatchClause", "CharacterLiteral",
       "ClassInstanceCreation", "CompilationUnit", "ConditionalExpression", "ConstructorInvocation",
       "ContinueStatement", "DoStatement", "EmptyStatement", "ExpressionStatement", "FieldAccess", "FieldDeclaration",
       "ForStatement", "IfStatement", "ImportDeclaration", "InfixExpression", "Initializer", "Javadoc",
       "LabeledStatement", "MethodDeclaration", "MethodInvocation", "NullLiteral", "NumberLiteral",
       "PackageDeclaration", "ParenthesizedExpression", "PostfixExpression", "PrefixExpression", "PrimitiveType",
       "QualifiedName", "ReturnStatement", "SimpleName", "SimpleType", "SingleVariableDeclaration", "StringLiteral",
       "SuperConstructorInvocation", "SuperFieldAccess", "SuperMethodInvocation", "SwitchCase", "SwitchStatement",
       "SynchronizedStatement", "ThisExpression", "ThrowStatement", "TryStatement", "TypeDeclaration",
       "TypeDeclarationStatement", "TypeLiteral", "VariableDeclarationExpression", "VariableDeclarationFragment",
       "VariableDeclarationStatement", "WhileStatement", "InstanceofExpression", "LineComment", "BlockComment",
       "TagElement", "TextElement", "MemberRef", "MethodRef", "MethodRefParameter", "EnhancedForStatement",
       "EnumDeclaration", "EnumConstantDeclaration", "TypeParameter", "ParameterizedType", "QualifiedType",
       "WildcardType", "NormalAnnotation", "MarkerAnnotation", "SingleMemberAnnotation", "MemberValuePair",
       "AnnotationTypeDeclaration", "AnnotationTypeMemberDeclaration", "Modifier", "UnionType", "Dimension",
       "LambdaExpression", "IntersectionType", "NameQualifiedType", "CreationReference", "ExpressionMethodReference",
       "SuperMethodReference", "TypeMethodReference", "MethodName", "Operator", "New", "Instanceof"]

# cAst = ["unit","comment","literal","operator","modifier","name","type","condition","block","index","decltype","typename","atomic","assert","generic_selection","selector","association_list","association","expr_stmt","expr","decl_stmt","decl","init","range","break","continue","goto","label","typedef","asm","macro","enum","enum_decl","if","ternary","then","else","elseif","while","typeof","do","switch","case","default","for","foreach","control","incr","function","function_decl","lambda","specifier","return","call","sizeof","parameter_list","parameter","krparameter_list","krparameter","argument_list","argument","capture","struct","struct_decl","union","union_decl","class","class_decl","public","private","protected","signals","forever","emit","member_init_list","constructor","constructor_decl","destructor","destructor_decl","super","friend","extern","namespace","using","try","catch","finally","throw","throws","noexcept","template","directive","file","number","include","define","undef","line","ifdef","ifndef","elif","endif","pragma","error","warning","value","empty","region","endregion","import","marker","parse","mode","lock","fixed","checked","unchecked","unsafe","using_stmt","delegate","event","constraint","extends","implements","package","synchronized","interface","interface_decl","annotation_defn","static","attribute","target","linq","from","select","where","let","orderby","group","join","in","on","equals","by","into","escape","annotation","alignas","alignof","typeid","ref_qualifier","receiver","message","protocol_list","category","protocol","required","optional","property","attribute_list","synthesize","dynamic","encode","autoreleasepool","compatibility_alias","protocol_decl","cast","position","clause","empty_stmt"]
cAst = ["unit" ,"comment:block", "comment:line", "literal:string", "literal:char", "literal:number", "literal:boolean", "literal:null", "literal:complex", "operator", "modifier", "name", "type", "type:prev", "block", "block_content", "block:pseudo", "index", "decltype", "typename", "atomic", "assert:static", "generic_selection", "selector", "association_list", "association", "expr_stmt", "expr", "decl_stmt", "decl", "init", "range", "break", "continue", "goto", "label", "typedef", "asm", "macro", "enum", "enum_decl", "if_stmt", "if", "ternary", "then", "else", "if:elseif", "while", "typeof", "do", "switch", "case", "default", "for", "foreach", "control", "condition", "incr", "function", "function_decl", "lambda", "specifier", "return", "call", "sizeof", "parameter_list", "parameter", "krparameter_list", "krparameter", "argument_list", "argument", "capture", "parameter_list:pseudo", "parameter_list:indexer", "struct", "struct_decl", "union", "union_decl", "class", "class_decl", "public", "public:default", "private", "private:default", "protected", "protected:default", "signals", "forever", "emit", "member_init_list", "constructor", "constructor_decl", "destructor", "destructor_decl", "super_list", "super", "friend", "extern", "namespace", "using", "try", "catch", "finally", "throw", "throws", "noexcept", "template", "argument_list:generic", "parameter_list:generic", "directive", "file", "number", "literal", "include", "define", "undef", "line", "cpp:if", "ifdef", "ifndef", "cpp:else", "elif", "endif", "cpp:then", "pragma", "error", "warning", "value", "empty", "marker", "region", "endregion", "import", "parse", "mode", "lock", "fixed", "checked", "unchecked", "unsafe", "using_stmt", "delegate", "event", "constraint", "extends", "implements", "package", "assert", "synchronized", "interface", "interface_decl", "annotation_defn", "static", "attribute", "target", "linq", "from", "select", "where", "let", "orderby", "group", "join", "in", "on", "equals", "by", "into", "escape", "annotation", "alignas", "alignof", "typeid", "sizeof:pack", "enum:class", "enum_decl:class", "function:operator", "function_decl:operator", "ref_qualifier", "receiver", "message", "protocol_list", "category", "clause"]

def exportAbstractPatterns():
    dbDir = join(INNER_DATA_PATH, 'redis')

    portInner = REDIS_PORT
    startDB(dbDir, portInner, PROJECT_TYPE)
    clusterStats,df = stats('actions')
    logging.debug(len(clusterStats))
    port = REDIS_PORT
    import redis
    redis_db = redis.StrictRedis(host="localhost", port=port, db=0)
    isJava = False
    if 'java' == PROJECT_TYPE:
        isJava = True
    for id, members in df[['cid','members']].values.tolist():
        if (len(members) == 0):
            continue

        try:
            dKey = '/'.join(id[0].split('-')[:-1]) + "/" + members[0]
            # lines = redis_db.hget("dump",dKey )
            lines = redis_db.hget(dKey,'actionTree')
            lines = redis_db.hget(dKey,'shapeTree')
            cid = id[0].replace("-",'#')

            abstractPattern(cid,lines.decode(),isJava,members)
        except Exception as e:
            logging.error(e)

def abstractPattern(cid,lines,isJava,cMembers):

    if isJava:
        ast = javaAst
    else:
        ast = cAst
    movPattern = 'MOV (' + '|'.join(ast) + ')@@(.*)@TO@ (' + '|'.join(ast) + ')@@(.*)@AT@'
    delPattern = 'DEL (' + '|'.join(ast) + ')@@(.*)@AT@'
    insPattern = 'INS (' + '|'.join(ast) + ')@@(.*)@TO@ (' + '|'.join(ast) + ')@@(.*)@AT@'
    updPattern = 'UPD (' + '|'.join(ast) + ')@@(.*)@TO@(.*)@AT@'

    level = 'actions'

    lines = re.split("@LENGTH@ \d+", lines)
    tokens = []
    for line in lines:
        # levelPatch  = len(re.findall('\w*---', line))
        match = re.search(r"^\w*---+", line,re.M)


        if match is not None:
            not_matched, matched = line[:match.start()], match.group()
            levelPatch  = int(len(matched) / 3)
        else:
            levelPatch = 0
        line = line.strip().strip('-')
        type = ''
        if line is '':
            continue
        t = []
        searchPattern = ''
        if line.startswith('INS'):
            if level =='actions':
                t= [1,3]
            else:
                t = [1]
            searchPattern = insPattern
            type =' INS '
        elif line.startswith('UPD'):
            t = [1]
            searchPattern = updPattern
            type = ' UPD '
        elif line.startswith('DEL'):
            t = [1]
            searchPattern = delPattern
            type = ' DEL '
        elif line.startswith('MOV'):
            if level == 'actions':
                t = [1, 3]
            else:
                t = [1]
            searchPattern = movPattern
            type = ' MOV '
    # from common.preprocessing import preprocessingForSimi
        m = re.search(searchPattern, line, re.DOTALL)
        if t is None:
            print()
        if m:
            for k in t:
                prefix = '---' * levelPatch
                if prefix != '':
                    prefix = '\n'+prefix
                token = m.group(k)
                if level =='actions':
                    if k ==3:
                        prefix = 'TO '
                    else:
                        prefix = prefix + type

                tokens.append(prefix+token)

    tokens
    inferedFrom = "\n\n // Infered from ({})".format(', '.join(cMembers))
    tokens.append(inferedFrom)
    clusterSavePath = join(DATA_PATH,'patterns')
    os.makedirs(clusterSavePath, exist_ok=True)
    with open(join(clusterSavePath, cid), 'w', encoding='utf-8') as writeFile:
    #     # if levelPatch == 0:
        writeFile.write(' '.join(tokens))
        # else:
        #     writeFile.write('\n'.join(tokens))
