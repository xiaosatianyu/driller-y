#!/usr/bin/env python
#coding=utf-8

import logging
from dpkt.tftp import ENOSPACE

# silence these loggers
logging.getLogger().setLevel("CRITICAL")
logging.getLogger("driller.fuzz").setLevel("INFO")

l = logging.getLogger("driller")
l.setLevel("INFO")

import os
import sys
import redis
import driller.tasks
import driller.config as config


'''
Large scale test script. Should just require pointing it at a directory full of binaries.
'''


#def start(binary_dir):
def start(binary,afl_engine):
    # cgc program
    binary_dir=config.BINARY_DIR_CGC #yyy
    
    jobs = [ ]
    binaries = os.listdir(binary_dir)
    if binary is not None: #
        binaries=[binary] # handle
    
    input_from="stdin" # the parameter to indicate the where does the input come from, stdin or file
    afl_input_para=[] # #such as ["@@", "/tmp/shelfish"]
    
    for binary in binaries: #
        if binary.startswith("."):
            continue 

        pathed_binary = os.path.join(binary_dir, binary) #
        if os.path.isdir(pathed_binary):
            continue
        if not os.access(pathed_binary, os.X_OK):
            continue
        
        ##annotation by yyy------------------------
#         identifier = binary[:binary.rindex("_")]  #
#         # remove IPC binaries from largescale testing ;
#         if (identifier + "_02") not in binaries:
#             jobs.append(binary) #
        ##end  ----------------------------------
        
        identifier = binary  
        jobs.append(pathed_binary)  #
        
    l.info("%d binaries found", len(jobs))
    l.debug("binaries: %r", jobs)

    # send all the binaries to the celery queue 
    l.info("%d binaries found", len(jobs))

    filter_t = set()  
    # yyy
#     try:
#         pwned = open("pwned").read()  
#         for pwn in pwned.split("\n")[:-1]:
#             filter_t.add(pwn)
#         l.info("already pwned %d", len(filter_t))
#     except IOError:
#         pass
    # yyy
    jobs = filter(lambda j: j not in filter_t, jobs) #

    l.info("going to work on %d", len(jobs))

    for binary_path in jobs:     
        #tasks.fuzz.delay(binary_path,input_from,afl_input_para,afl_engine) 
        driller.tasks.fuzz(binary_path+'-sort',input_from,afl_input_para,afl_engine,comapre_afl=False,inputs_sorted=True) 
     

    l.info("listening for tasks..")

#     redis_inst = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
#     p = redis_inst.pubsub() #
#     p.subscribe("crashes") #
# 
#     cnt = 1
#     for msg in p.listen():
#         if msg['type'] == 'message':
#             l.info("[%03d/%03d] crash found for '%s'", cnt, len(jobs), msg['data'])
#             cnt += 1
    
    ##监听task完成情况
    redis_inst = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    p = redis_inst.pubsub() #这是一个订阅发布器
    p.subscribe("tasks") #订阅 crashed 频道, 在fuzz函数中发射的
    
    for msg in p.listen():
        if msg['type'] == 'message':
            l.info("task: %s",msg['data'])
                    
          

def main(argv):
    #cgc pro
    binary=argv[1]
    if len(argv)<3:
        afl_engine="default"  ## fast yyy or default; default is shelfish-afl
    else:    
        afl_engine=argv[2] #"fast" "yyy"
            
    start(binary,afl_engine)
    ## end ---------------------
    
    
if __name__ == "__main__":
    #yyy.delay()
    sys.exit(main(sys.argv))
