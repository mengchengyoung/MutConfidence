import os 
from keras.models import load_model
from lib.detail import Detail
from lib.vcf import VCF
import pysam 
import numpy as np

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
                site = dict(reference=line[0], pos=int(line[1]), ref=line[3], alt=line[4], format=line[-1])
                yield site
                line = f.readline().strip()
            else:
                self.head = []

class Predict():
    def __init__(self, args):
        self.args = args        
        self.model_file = self.args.model_file
        self.model = None
        self.feature = ['strand_bias', 'insert_average', 'mapping_quality', #应该与训练用的特征向量一致，且顺序一致
                        'base_quality', 'GC', 'depth', 'frequency', 'FOXOG']
        self.init()

    def init(self):
        if not os.path.exists(self.model_file):
            raise FileNotFoundError
        self.model = load_model(self.model_file)

    def serialize(self, site, detail:Detail):
        """
        return a serialized site-dict for csv output.
        override this function when turn to indel
        """
        feature = self.feature
        s = list()
        base = dict( reference = site['reference'],
                    pos = site['pos'] )
        detail.Base = base
        for field in feature:
            try:
                d = getattr(detail, 'get_{}'.format(field))
                if d == '.':
                    return False
                s.append(getattr(detail, 'get_{}'.format(field)))
            except AttributeError:
                if site[field] == '.':
                    return False 
                s.append(site[field])
        return s

    def process(self):
        Alignmentfile = pysam.AlignmentFile(self.args.bam_file) 
        #queue = self.IOqueue
        detail = Detail(Alignmentfile)
        vcf = VCF_filter(self.args.vcf_file)
        #vcf = VCF(self.args.vcf_file)
        sites_batch = list()
        for site in vcf.get_sites:
            new_site = self.serialize(site, detail)
            if new_site:
                sites_batch.append(new_site)
        res = self.model.predict(np.array(sites_batch))
        print(res)

