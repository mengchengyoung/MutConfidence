import pysam
import os 
import glob
from lib.detail import Detail
from lib.vcf import VCF
from lib.queue_manager import queue_manager
from lib.multithreading import MultiThread
import csv
import logging
from queue import Queue
from tqdm import tqdm

logger = logging.getLogger(__name__)

class Files():
    """
    load vcf files of negtive and positve sample.
    """
    #pass
    def __init__(self, negtive_dir, positive_dir):
        self.negtive_dir = negtive_dir
        self.positive_dir = positive_dir

    def load(self):
        samples = os.listdir(self.negtive_dir)
        for sample in samples:
            negtive_sample = self.negtive_dir + '/' + sample
            positive_sample = self.positive_dir + '/' + sample
            bam = glob.glob("{}/Alignment/{}.uniq.bam".format(self.negtive_dir, sample))
            yield negtive_sample, positive_sample, bam[0]

class VCF_filter(VCF):
    def get_iterator(self):
        """
        The first line is not mark with #, so override this function
        """
        with open(self.filename) as f:
            line = f.readline()
            line =f.readline().strip()
            while line:
                line = line.split('\t')
                site = dict(reference=line[0], pos=int(line[1]), ref=line[3], FILTER=line[-4], alt=line[4], format=line[-1])
                yield site
                line = f.readline().strip()
            else:
                self.head = []

class Generate():
    """
    load the sample
    """
    def __init__(self, args, path='/annoroad/data1/bioinfo/PROJECT/Commercial/Medical/Leukemia/data/Commercial_V3'):
        self.args = args
        self.files = Files(self.args.negtive_dir, self.args.positive_dir)
        self.IOqueue = None
        self.add_queue('IO')
        #self.header = self.args.header
        self.headers = ['strand_bias', 'insert_average', 'mapping_quality',
                        'base_quality','GC'] # this heature genrate from vcf model
        self.extra = ['reference', 'pos', 'depth', 'frequency', 'FOXOG',
                      'NORMAL', 'Tlodfstar', 'PONFilter', 'confidence'] # this feature original with site object
 
    def add_queue(self, qname):
        #queue_manager.add_queue(qname, 32)
        #queue = queue_manager.get_queue(qname)
        queue = Queue()
        self.IOqueue = queue

    @staticmethod
    def diff(raw_sites, filter_sites):
        """ 
        get the filter out data 
        """
        Positive_sites, Negtive_sites = list(), list()
        for i in raw_sites:
            if i in filter_sites:
                Positive_sites.append(i)
            else:
                Negtive_sites.append(i)
        return Positive_sites, Negtive_sites
    
    def IOthread(self):
        f = open(self.args.output_dir, 'w')
        csv_writer = csv.DictWriter(f, self.headers + self.extra)
        csv_writer.writeheader()
        while True:
            row = self.IOqueue.get()
            if row == 'EOF':
                f.close()
                return 
            csv_writer.writerows([row])

    def serialize(self, site, detail):
        """
        return a serialized site-dict for csv output.
        override this function when turn to indel
        """
        header = self.headers
        s = { i : None for i in header }
        base = dict( reference = site['reference'],
                    pos = site['pos'] )
        detail.Base = base
        for field in header:
            s[field] = getattr(detail, 'get_{}'.format(field))
        for i in self.extra:
            s[i] = site[i]
        return s

    def process(self):
        """
            main function of this class, IO thread terminate when 
            the main function finished
        """
        IOthread = MultiThread(self.IOthread)
        IOthread.start()
        for rawfile, filterfile, bamfile in tqdm(self.files.load()):
            logger.info("read file {}".format(rawfile))
            vcf1, vcf2 = VCF(rawfile), VCF_filter(filterfile)
            Alignmentfile = pysam.AlignmentFile(bamfile)

            detail = Detail(Alignmentfile)
            Positive_sites, Negtive_sites = self.diff(vcf1.get_sites, vcf2.get_sites)
            assert len(Negtive_sites) != 0, filterfile
            assert len(Positive_sites) != 0, rawfile
            for site in Positive_sites:
                site['confidence'] = 1
                s = self.serialize(site, detail)
                self.IOqueue.put(s)

            for site in Negtive_sites:
                site['confidence'] = 0
                s = self.serialize(site, detail)
                self.IOqueue.put(s)
        else:
            self.IOqueue.put('EOF')
        IOthread.join()
