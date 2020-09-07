package edu.x.y;


import edu.x.y.richedit.jobs.CompareTrees;
import edu.x.y.richedit.jobs.EnhancedASTDiff;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.yaml.snakeyaml.Yaml;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Map;
import java.util.Properties;


public class Launcher {

    private static Logger log = LoggerFactory.getLogger(Launcher.class);

    public static void main(String[] args) throws IOException {


        Properties appProps = new Properties();

//        String hostname = "Unknown";
//        try
//        {
//            InetAddress addr;
//            addr = InetAddress.getLocalHost();
//            hostname = addr.getHostName();
//        }
//        catch (UnknownHostException ex)
//        {
//            System.out.println("Hostname can not be resolved");
//        }
//        String appConfigPath;
//        if (hostname.equals("Unknown")){
//             appConfigPath = "src/main/resource/app.properties";
//        }
//        else{
//             appConfigPath = "src/main/resource/"+hostname.split("\\.")[0]+".app.properties";
//        }
        if(args.length != 2)
        {
            System.out.println("Proper Usage is: \n\tfirst argument full path to .properties file (e.g. an example is located under resources) \n\tsecond argument jobType (e.g RICHEDITSCRIPT, COMPARE)");
            System.exit(0);
        }

        String appConfigPath = args[0];

        Yaml yaml = new Yaml();
//        InputStream inputStream = this.getClass()
//                .getClassLoader()
//                .getResourceAsStream("customer.yaml");
        Map<String, Object> obj = yaml.load(new FileInputStream(appConfigPath));

        appProps.load(new FileInputStream(appConfigPath));
        Map<String, Object> miner = (Map<String, Object>) obj.get("miner");
//        String numOfWorkers = appProps.getProperty("numOfWorkers", "10");
        String numOfWorkers = String.valueOf(miner.get("numOfWorkers"));
        String portDumps = String.valueOf(miner.get("portDumps"));
        String projectType = (String) miner.get("projectType");

        String hunkLimit = String.valueOf(miner.get("hunkLimit"));
        String patchSize = String.valueOf(miner.get("patchSize"));
        String projectL = (String) miner.get("projectList");
        String[] projectList = projectL.split(",");
        String input = (String) miner.get("inputPath");
        String redisPath = (String) miner.get("redisPath");
        String srcMLPath = (String) miner.get("srcMLPath");

//        String parameter = args[2];
//        String parameter = "L1";
        String jobType = args[1];
//        String jobType = "RICHEDITSCRIPT";
//        jobType = "COMPARE";


        mainLaunch( numOfWorkers, jobType, portDumps,projectType,input,redisPath, srcMLPath,hunkLimit,projectList,patchSize);


    }

    public static void mainLaunch(String numOfWorkers, String jobType, String portDumps, String projectType, String input, String redisPath,String srcMLPath,String hunkLimit,String[] projectList,String patchSize){


        String dbDir;
        String dumpsName;
        String gumInput;

        dumpsName = "dumps-"+projectType+".rdb";

        gumInput = input;
        dbDir = redisPath;


        try {
            switch (jobType) {
                case "RICHEDITSCRIPT":
                    EnhancedASTDiff.main(gumInput, portDumps, dbDir, dumpsName, srcMLPath,hunkLimit,projectList,patchSize,projectType);
                    break;

                case "COMPARE":
//                    String job;
//                    String compareDBName;
//                    switch (parameter){
//                        case "L1":
////                            job = "shape";
//                            job = "single";
//                            compareDBName = "clusterl0-gumInputALL.rdb";
//                            break;
//                        case "L2":
//                            job = "action";
//                            compareDBName = "clusterl1-gumInputALL.rdb";
//                            break;
//                        case "L3":
//                            job = "token";
//                            compareDBName = "clusterl2-gumInputALL.rdb";
//                            break;
//                        default:
//                            throw new Error("unknown level please specify L1,L2,L3");
//                    }


                    CompareTrees.main(redisPath, portDumps,dumpsName, numOfWorkers);
                    break;
//                case "PATTERN":
//                    ClusterToPattern.main(portDumps,redisPath, dumpsName, parameter);
//                    break;
                default:
                    throw new Error("unknown Job");

            }
        } catch (Exception e) {
//            log.error(e.getMessage());
            e.printStackTrace();
//            e.printStackTrace();

        }




        }

}


