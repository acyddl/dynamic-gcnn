import tensorflow as tf
import numpy as np
import argparse, os, sys
from main_funcs import train
class DGCNN_FLAGS:

    # gcnn_model flags
    NUM_EDGE_CONV = 3
    TRAIN         = True
    KVALUE        = 20
    DEBUG         = True
    
    # gcnn_trainval flags
    SEED          = -1
    LEARNING_RATE = 0.001
    GPUS = [0]
    MINIBATCH_SIZE = 1
    KVALUE = 20
    NUM_POINT = 2048
    NUM_CHANNEL = 4
    TRAINING = True
    ITERATION = 10000
    REPORT_STEP = 100

    # gcnn_io flags
    IO_TYPE    = 'h5'
    INPUT_FILE = '/scratch/kterao/dlprod_ppn_v08/dgcnn_p02_test_4ch.hdf5'
    BATCH_SIZE = 1
    LOG_DIR    = 'log'
    MODEL_PATH = ''
    
    def __init__(self):
        self._build_parsers()

    def _attach_common_args(self,parser):
        parser.add_argument('-kv','--kvalue',type=int,default=self.KVALUE,help='K value')
        parser.add_argument('--gpus', type=str, default='0',
                            help='GPUs to utilize (comma-separated integers')
        parser.add_argument('-np','--num_point', type=int, default=self.NUM_POINT,
                            help='Point number [default: %s]' % self.NUM_POINT)
        parser.add_argument('-it','--iterations', type=int, default=self.ITERATION,
                            help='Iterations to run [default: %s]' % self.ITERATION)
        parser.add_argument('-bs','--batch_size', type=int, default=self.BATCH_SIZE,
                            help='Batch Size during training for updating weights [default: %s]' % self.BATCH_SIZE)
        parser.add_argument('-mp','--model_path', type=str, default=self.MODEL_PATH,
                            help='model checkpoint file path [default: %s]' % self.MODEL_PATH)
        parser.add_argument('-io','--io_type',type=str,default=self.IO_TYPE,
                            help='IO handler type [default: %s]' % self.IO_TYPE)
        parser.add_argument('-if','--input_file',type=str,default=self.INPUT_FILE,
                            help='comma-separated input file list [default: %s]' % self.INPUT_FILE)
        return parser
        
    def _build_parsers(self):

        self.parser = argparse.ArgumentParser(description="Edge-GCNN Configuration Flags")
        subparsers = self.parser.add_subparsers(title="Modules", description="Valid subcommands", dest='script', help="aho")

        # train parser
        train_parser = subparsers.add_parser("train", help="Train Edge-GCNN")
        train_parser.add_argument('-sd','--seed', default=self.SEED,
                                  help='Seed for random number generators [default: %s]' % self.SEED)
        train_parser.add_argument('-ld','--log_dir', default=self.LOG_DIR,
                                  help='Log dir [default: %s]' % self.LOG_DIR)
        train_parser.add_argument('-mbs','--minibatch_size', type=int, default=self.MINIBATCH_SIZE,
                                  help='Mini-Batch Size during training for each GPU [default: %s]' % self.MINIBATCH_SIZE)
        train_parser.add_argument('-lr','--learning_rate', type=float, default=self.LEARNING_RATE,
                                  help='Initial learning rate [default: %s]' % self.LEARNING_RATE)
        train_parser.add_argument('-rs','--report_step', type=int, default=self.REPORT_STEP,
                                  help='Period (in steps) to print out loss and accuracy [default: %s]' % self.REPORT_STEP)
        # attach common parsers
        self.train_parser = self._attach_common_args(train_parser)

        # attach executables
        self.train_parser.set_defaults(func=train)

    def parse_args(self):
        args = self.parser.parse_args()
        self.update(vars(args))
        print("\n\n-- CONFIG --")
        for name in vars(self):
            attribute = getattr(self,name)
            if type(attribute) == type(self.parser): continue
            print("%s = %r" % (name, getattr(self, name)))
            
        # Set random seed for reproducibility
        np.random.seed(self.SEED)
        tf.set_random_seed(self.SEED)
        args.func(self)
                    
    def update(self, args):
        for name,value in args.iteritems():
            if name in ['func','script']: continue
            setattr(self, name.upper(), args[name])
        os.environ['CUDA_VISIBLE_DEVICES']=self.GPUS
        self.GPUS=[int(gpu) for gpu in self.GPUS.split(',')]
        self.INPUT_FILE=[str(f) for f in self.INPUT_FILE.split(',')]
        if self.SEED < 0:
            import time
            self.SEED = int(time.time())
        
if __name__ == '__main__':
    flags=GCNN_FLAGS()
    flags.parse_args()
    
