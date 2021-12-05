#!/usr/bin/env python2 -tt
import os, re, argparse, subprocess, time
from shutil import copyfile
import threading

class commThread(threading.Thread):
    """ Add the TCP thread here: 
    """ 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        self.expStart = False

    def run(self):
        while not self.terminate:
            if self.expStart:
                self.experimentStart()
                self.expStart = True

    def extractLables(self, line):
        label = '#!' + line.split()[-1] + '\n'
        exp = ''
        if '127.0.0.1' in line:
            exp += 'Local Fetch\n'
        elif '172.' in line:
            exp += 'Remote (LAN) Fetch\n'
        fsize_bsize = re.search('ile(.*) ', line).group(1).split(':')
        if 'file' in line:
            exp += 'File Size: ' + str(pow(2, int(fsize_bsize[0]))) + '\n'
            exp += 'Block Size: ' + fsize_bsize[1].split()[0] + '\n'
            exp += 'Iterations: ' + line.split()[-2] + '\n'

        elif 'bigFile' in line:
            exp += 'File Size: 1 MB\nBlock Size: ' + fsize_bsize[1].split()[0] + '\n'
        elif 'biggerFile' in line:
            exp += 'File Size: 1 GB\nBlock Size: ' + fsize_bsize[1].split()[0] + '\n'
        elif 'biggestFile' in line:
            exp += 'File Size: 4.1 GB\nBlock Size: ' + fsize_bsize[1].split()[0] + '\n'

        if '-f' in line:
            exp += 'Flood (No Sleep)\n'
        elif '-r' in line:
            exp += 'Random Sleep\n'

        return label + exp

    def experimentStart(self):
        interm_res = 'exp-output.csv'
        command = './verifier'
        exp_dir = 'ExpRes/'
        exp_lbl = []

        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)

        #ap = argparse.ArgumentParser(description = 'Runs experiments in batches and autogenerates their labels and log files.')
        #ap.add_argument('script', help='Batch experiment script to run.')
        # ap.add_argument('--log' , help='With log.', action = 'store_true')
        #args = ap.parse_args()

        # log = args.log
        exp_script = "scripted_exp.bat"
            
        with open (exp_script) as exp:
            script_lines = exp.readlines()

        for l in script_lines:
            if l[:3] == 'rem' or l == '\n':
                continue

            if 'Sleep' == l.split()[0]:
                print('\nSleeping for %s seconds.' %str(l.split()[1]))
                time.sleep(int(l.split()[1]))
                print('Resuming...\n')
            if 'Run:' == l.split()[0]:
                arguments = ' '.join(l.strip('Run:').split()[:-1])
                expName =  l.split()[-1]
                print('Running experiment ' + expName + ' with arguments: ' + arguments)

                res = subprocess.Popen(command+' '+arguments, shell=True, stderr=subprocess.STDOUT)
                res.wait()
                print("Finished")

            if os.path.isfile(interm_res):
                print('Moving results of', expName, 'to', exp_dir+expName)
                os.rename(interm_res, exp_dir+expName+'.csv')
                copyfile(exp_script, exp_dir + exp_script)
                exp_lbl.append(self.extractLables(l))
            else:
                print('Experiment', expName , 'did not produce any results.', interm_res, 'not found!')
                #exit()
                
        with open (exp_dir+'exps.exp', 'w') as op:
            op.writelines(exp_lbl)
  
                  
#if __name__ == '__main__':
#  main()
                      

