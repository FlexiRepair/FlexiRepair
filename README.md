# FlexiRepair 



## I. Introduction

We have presented FlexiRepair, an open framework for template-based program repair where we build on the concept of generic patch to define a unified  representation/notation for specifying fix patterns (aka templates).
![The workflow of this technique.\label{workflow}](https://github.com/FlexiRepair/FlexiRepair/blob/master/pipeline.png)


## II. Environment setup

#### Requirement
* Docker

#### Setup
* Download the [docker file](https://github.com/FlexiRepair/FlexiRepair/tree/master/dockerfile) 
* Build the docker image. It will install all the necessary requirements.
  ```powershell
  docker build -t flexi .
  ```
* Create a folder to storage the data that is going to be shared with the docker image.
  ```powershell
  mkdir flexi-data
  ```
* Run the following commmand with the full path the created folder:
  ```powershell
  docker run -v /home/user/flexi-data/:/data/flexi-data -it flexi:latest /bin/bash
  ```

## III. Step-by-Step execution

#### Inside the docker image

* Update [config file](https://github.com/FlexiRepair/FlexiRepair/tree/master/src/main/resources/config.yml) to change projects to mine.



In order to launch FlexiRepair, execute [flexi.sh](https://github.com/FlexiRepair/FlexiRepair/tree/master/flexi.sh) as follows:
  ```powershell
    bash flexi.sh [CONFIG_FILE] [JOB]
     e.g. bash flexi.sh src/main/resources/config.yml miner
   ```
     
A log file (app.log) is created after every execution of the flexi.sh. Please check this log file in order to access more information. 
 

    
#### Jobs  

*FlexiRepair* needs to follow an execution, **in the order listed below** in order to create clusters of patches.

   1. __miner__: *Miner* performs patch clustering, grouping together the code changes that are representing a
                 repeating code context and change operations. The changes are collected from the projects listed in [datasets.csv](https://github.com/FlexiRepair/FlexiRepair/tree/master/python/data/datasets.csv).
      
   2. __inferrer__: The goal of the *Inferrer* is to derive generic patches from the clusters of similar concrete patches.
   
   3. __validateCodeFlaws__: Creates patch candidates and validates them on the preinstalled CodeFlaws benchmark. 
   
  

## IV. Generated Patch Candidates
The plausible patches generated with FlexRepair are listed in patches folder.

```powershell
  |--- patches                   :  plausible patches
    |--- introclass_black        :  plausible patches passing introclass blackbox test-suite
    |--- introclass_white        :  plausible patches passing introclass whitebox test-suite
    |--- generic_black           :  generic patches used for generating "introclass_black"
    |--- generic_white           :  generic patches used for generating "introclass_white"


```
## V. Structure of the shared folder
```powershell
  |--- actions                      :  clusters of patches grouped together
  |--- commitsDF                    :  pickle objects containing data related to mine projects and patches
  |--- datasets                     :  clones of projects to be mined
  |--- pairs                        :  cluster comparsion index files
  |--- patches                      :  patches of the projects, inference indexes, and infered generic patches
  |------cocci                      :  generic patches

```


#### Data Viewer

The intermediate data provided computed during the steps are listed in directory flexi-data (or the corresponding folder shared with docker)
                                                                                                  
The data is stored in different formats. (e.g. pickle, redis db, csv, etc..)
<!--
###### Redis Commands

Connect to redis instance

 ```powershell
     redis-cli -p 6399
  ```   

We use 3 databases inside the redis, 0,1,2,3.
DB 0 stores the richedit dumps, comparison indices
DB 1 stores the filenames and their indices (used in comparison and stored in DB2, DB3) 
DB 2 stores the output of comparison action trees.
DB 3 stores the output of comparison token trees.

In order to switch between these database use the following command

 ```powershell
     select 2
  ```   

In order to trace the status of the stored rich edit scripts, use the following command

 ```powershell
     hlen dump
  ```   

In order to access the rich edit of a single hunk, first locate the key from DB 0. This command returns the exact name of the keys

 ```powershell
keys *NAME_OF_THE_HUNK

keys *fuse_67b14b_04e5b1_fabric#fabric-client#src#main#java#org#fusesource#fabric#jolokia#facade#facades#ProfileFacade.java.txt_1

OUTPUT:
1) "MethodDeclaration/40/fuse_67b14b_04e5b1_fabric#fabric-client#src#main#java#org#fusesource#fabric#jolokia#facade#facades#ProfileFacade.java.txt_1"
  ```   

Then, use the exact key in order to access the rich edit:
 ```powershell
hget dump NAME_OF_THE_EXACT_KEY

hget dump MethodDeclaration/40/fuse_67b14b_04e5b1_fabric#fabric-client#src#main#java#org#fusesource#fabric#jolokia#facade#facades#ProfileFacade.java.txt_1

OUTPUT:
"INS MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @TO@ TypeDeclaration@@[public]ProfileFacade, [Profile, HasId] @AT@ 7279 @LENGTH@ 309\n---INS Modifier@@public @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7279 @LENGTH@ 6\n---INS PrimitiveType@@void @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7286 @LENGTH@ 4\n---INS SimpleName@@MethodName:setConfiguration @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7291 @LENGTH@ 16\n---INS SingleVariableDeclaration@@String pid @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7308 @LENGTH@ 10\n------INS SimpleType@@String @TO@ SingleVariableDeclaration@@String pid @AT@ 7308 @LENGTH@ 6\n------INS SimpleName@@pid @TO@ SingleVariableDeclaration@@String pid @AT@ 7315 @LENGTH@ 3\n---INS SingleVariableDeclaration@@Map<String,String> configuration @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7320 @LENGTH@ 33\n------INS ParameterizedType@@Map<String,String> @TO@ SingleVariableDeclaration@@Map<String,String> configuration @AT@ 7320 @LENGTH@ 19\n---------INS SimpleType@@Map @TO@ ParameterizedType@@Map<String,String> @AT@ 7320 @LENGTH@ 3\n---------INS SimpleType@@String @TO@ ParameterizedType@@Map<String,String> @AT@ 7324 @LENGTH@ 6\n---------INS SimpleType@@String @TO@ ParameterizedType@@Map<String,String> @AT@ 7332 @LENGTH@ 6\n------INS SimpleName@@configuration @TO@ SingleVariableDeclaration@@Map<String,String> configuration @AT@ 7340 @LENGTH@ 13\n---INS VariableDeclarationStatement@@Map<String,Map<String,String>> configurations=getConfigurations(); @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7365 @LENGTH@ 70\n------INS ParameterizedType@@Map<String,Map<String,String>> @TO@ VariableDeclarationStatement@@Map<String,Map<String,String>> configurations=getConfigurations(); @AT@ 7365 @LENGTH@ 32\n---------INS SimpleType@@Map @TO@ ParameterizedType@@Map<String,Map<String,String>> @AT@ 7365 @LENGTH@ 3\n---------INS SimpleType@@String @TO@ ParameterizedType@@Map<String,Map<String,String>> @AT@ 7369 @LENGTH@ 6\n---------INS ParameterizedType@@Map<String,String> @TO@ ParameterizedType@@Map<String,Map<String,String>> @AT@ 7377 @LENGTH@ 19\n------------INS SimpleType@@Map @TO@ ParameterizedType@@Map<String,String> @AT@ 7377 @LENGTH@ 3\n------------INS SimpleType@@String @TO@ ParameterizedType@@Map<String,String> @AT@ 7381 @LENGTH@ 6\n------------INS SimpleType@@String @TO@ ParameterizedType@@Map<String,String> @AT@ 7389 @LENGTH@ 6\n------INS VariableDeclarationFragment@@configurations=getConfigurations() @TO@ VariableDeclarationStatement@@Map<String,Map<String,String>> configurations=getConfigurations(); @AT@ 7398 @LENGTH@ 36\n---------INS SimpleName@@configurations @TO@ VariableDeclarationFragment@@configurations=getConfigurations() @AT@ 7398 @LENGTH@ 14\n---------INS MethodInvocation@@MethodName:getConfigurations:[] @TO@ VariableDeclarationFragment@@configurations=getConfigurations() @AT@ 7415 @LENGTH@ 19\n---INS IfStatement@@if (configurations != null) {  configurations.put(pid,configuration);  setConfigurations(configurations);} @TO@ MethodDeclaration@@public, void, MethodName:setConfiguration, String pid, Map<String,String> configuration,  @AT@ 7444 @LENGTH@ 138\n------INS InfixExpression@@configurations != null @TO@ IfStatement@@if (configurations != null) {  configurations.put(pid,configuration);  setConfigurations(configurations);} @AT@ 7448 @LENGTH@ 22\n---------INS SimpleName@@configurations @TO@ InfixExpression@@configurations != null @AT@ 7448 @LENGTH@ 14\n---------INS Operator@@!= @TO@ InfixExpression@@configurations != null @AT@ 7462 @LENGTH@ 2\n---------INS NullLiteral@@null @TO@ InfixExpression@@configurations != null @AT@ 7466 @LENGTH@ 4\n------INS Block@@ThenBody:{  configurations.put(pid,configuration);  setConfigurations(configurations);} @TO@ IfStatement@@if (configurations != null) {  configurations.put(pid,configuration);  setConfigurations(configurations);} @AT@ 7472 @LENGTH@ 110\n---------INS ExpressionStatement@@MethodInvocation:configurations.put(pid,configuration) @TO@ Block@@ThenBody:{  configurations.put(pid,configuration);  setConfigurations(configurations);} @AT@ 7486 @LENGTH@ 39\n------------INS MethodInvocation@@configurations.put(pid,configuration) @TO@ ExpressionStatement@@MethodInvocation:configurations.put(pid,configuration) @AT@ 7486 @LENGTH@ 38\n---------------INS SimpleName@@Name:configurations @TO@ MethodInvocation@@configurations.put(pid,configuration) @AT@ 7486 @LENGTH@ 14\n---------------INS SimpleName@@MethodName:put:[pid, configuration] @TO@ MethodInvocation@@configurations.put(pid,configuration) @AT@ 7501 @LENGTH@ 23\n------------------INS SimpleName@@pid @TO@ SimpleName@@MethodName:put:[pid, configuration] @AT@ 7505 @LENGTH@ 3\n------------------INS SimpleName@@configuration @TO@ SimpleName@@MethodName:put:[pid, configuration] @AT@ 7510 @LENGTH@ 13\n---------INS ExpressionStatement@@MethodInvocation:setConfigurations(configurations) @TO@ Block@@ThenBody:{  configurations.put(pid,configuration);  setConfigurations(configurations);} @AT@ 7538 @LENGTH@ 34\n------------INS MethodInvocation@@setConfigurations(configurations) @TO@ ExpressionStatement@@MethodInvocation:setConfigurations(configurations) @AT@ 7538 @LENGTH@ 33\n---------------INS SimpleName@@MethodName:setConfigurations:[configurations] @TO@ MethodInvocation@@setConfigurations(configurations) @AT@ 7538 @LENGTH@ 33\n------------------INS SimpleName@@configurations @TO@ SimpleName@@MethodName:setConfigurations:[configurations] @AT@ 7556 @LENGTH@ 14\n"  
  ```  

Or use the following command to access specialized trees:

 ```powershell
hgetall NAME_OF_THE_EXACT_KEY

hgetall MethodDeclaration/40/fuse_67b14b_04e5b1_fabric#fabric-client#src#main#java#org#fusesource#fabric#jolokia#facade#facades#ProfileFacade.java.txt_1

OUTPUT:
1) "tokens"
2) "public  void  MethodName:setConfiguration  String  pid  Map  String  String  configuration  Map  String  Map  String  String  configurations  MethodName:getConfigurations:[]  configurations  !=  null  Name:configurations  pid  configuration  configurations "
3) "targetTree"
4) "[(55@@[(31@@)][(31@@)][(31@@)][(31@@[(44@@)][(44@@)])][(31@@[(44@@[(74@@)][(74@@)][(74@@)])][(44@@)])][(31@@[(60@@[(74@@)][(74@@)][(74@@[(74@@)][(74@@)][(74@@)])])][(60@@[(59@@)][(59@@)])])][(31@@[(25@@[(27@@)][(27@@)][(27@@)])][(25@@[(8@@[(21@@[(32@@)][(32@@[(42@@)][(42@@)])])])][(8@@[(21@@[(32@@[(42@@)])])])])])])]"
5) "actionTree"
6) "[(100@@[(100@@)][(100@@)][(100@@)][(100@@[(100@@)][(100@@)])][(100@@[(100@@[(100@@)][(100@@)][(100@@)])][(100@@)])][(100@@[(100@@[(100@@)][(100@@)][(100@@[(100@@)][(100@@)][(100@@)])])][(100@@[(100@@)][(100@@)])])][(100@@[(100@@[(100@@)][(100@@)][(100@@)])][(100@@[(100@@[(100@@[(100@@)][(100@@[(100@@)][(100@@)])])])][(100@@[(100@@[(100@@[(100@@)])])])])])])]"
7) "shapeTree"
8) "[(31@@[(83@@)][(39@@)][(42@@)][(44@@[(43@@)][(42@@)])][(44@@[(74@@[(43@@)][(43@@)][(43@@)])][(42@@)])][(60@@[(74@@[(43@@)][(43@@)][(74@@[(43@@)][(43@@)][(43@@)])])][(59@@[(42@@)][(32@@)])])][(25@@[(27@@[(42@@)][(-1@@)][(33@@)])][(8@@[(21@@[(32@@[(42@@)][(42@@[(42@@)][(42@@)])])])][(21@@[(32@@[(42@@[(42@@)])])])])])])]"
  ```  

After executing the actionSI / tokenSI steps, the rich edit scripts to be compared are stored in a key in DB 0. Use the following command to verify number of comparison to be made. 
The trees that are labelled to be same are stored in DB2 for action trees and,in DB3 for token trees. 

This command can also be used in order to progress the compare step. When the comparison is completed the following command will return 0.
 ```powershell
scard compare
  ``` 

-->
###### Pickle
The see content of the .pickle file the following script could be used.

  ```python
   import pickle as p
   import gzip
   def load_zipped_pickle(filename):
      with gzip.open(filename, 'rb') as f:
          loaded_object = p.load(f)
          return loaded_object
  ```
Usage

  ```python
  result = load_zipped_pickle('/data/flexi-data/commitsDF/git.pickle')
  # Result is pandas object which can be exported to several formats
  # Details on how to export is listed in offical library documentation
  # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

  ```
