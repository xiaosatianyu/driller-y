#coding=utf-8
import os
import sys
import driller.tasks
import shutil
import redis
import subprocess
import time
import driller.config as config


def clean_redis(binary):
    redis_pool = redis.ConnectionPool(host=driller.config.REDIS_HOST, port=driller.config.REDIS_PORT, db=driller.config.REDIS_DB) 
    redis_inst = redis.Redis(connection_pool=redis_pool)
    # delete all catalogued inputs
    redis_inst.delete("%s-catalogue" % binary)
    # delete all the traced entries
    redis_inst.delete("%s-traced" % binary)
    # delete the finished entry
    redis_inst.delete("%s-finsihed" % binary)
    # delete the fuzz bitmaps
    redis_inst.delete("%s-bitmaps" % binary)
    
def start_listener(workdir):

    driller_queue_dir = os.path.join(workdir, "driller", "queue")
    binary_id=os.path.basename(workdir)
    channel = "%s-generated" % binary_id  #监听测试用例的信道
    base="/home/xiaosatianyu/workspace/git/driller-yyy/driller"
    args = [ os.path.join(base, "bin", "driller", "listen.py"),  driller_queue_dir,  channel ]
    p = subprocess.Popen(args) #启动listen.py   #要启动这个脚本成功,必须在driller的目录下

    
def start_sym_test(binary_path):
    #seed_dir="/tmp/driller/claw32/sync/fuzzer-master"
    #seed_dir="/tmp/output-yyy"
    seed_dir="/home/xiaosatianyu/Desktop/driller/seed"
    
    ##unix--------------------------
    #binary_path="/home/xiaosatianyu/Desktop/driller/binary-unix/fauxware"
    #binary_path="/home/xiaosatianyu/Desktop/driller/binary-unix/Snail_Mail"
    ##cgc---------------
    
    #binary_path="/home/xiaosatianyu/Desktop/driller/binary-cgc/YAN01_00015"
    binary=os.path.basename(binary_path)
    
    input_data_path=os.path.join(seed_dir,"test")
    input_data = open(input_data_path, "rb").read() #读取测试用例内容
    bitmap_hash="hello"
    tag='test'
    #input_from="file" 
    #afl_input_para=["@@"]
    input_from="stdin"
    afl_input_para=[]
    
    workdir=os.path.join("/tmp/driller",binary)
    if os.path.exists(workdir):
            shutil.rmtree(workdir) #删除工作目录, 此时尚未生成相关的目录,所以先删除一下没事
    
    #开启监听器
    clean_redis(binary)
    start_listener(workdir)      
    
    driller.tasks.drill(binary_path, 
                        input_data, 
                        input_data_path, 
                        bitmap_hash, 
                        tag, 
                        input_from, 
                        afl_input_para)
#end start_sym_test

       
    
if __name__ == "__main__":
    binaries_dir="/home/xiaosatianyu/Desktop/driller/生成数量多的cgc"
    target_pros=os.listdir(binaries_dir)
    target_pros.sort()
    for i in target_pros:
        if os.path.exists(os.path.join("/tmp/driller",i)):
            #表示已经存在了
            continue
        target_pro=os.path.join(binaries_dir,i)
        print "deal with %s" % os.path.basename(target_pro)
        start_sym_test(target_pro)
        
    sys.exit()
